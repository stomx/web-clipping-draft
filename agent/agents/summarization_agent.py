from agent.state import AgentState
from agent.utils.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

import json
import asyncio
import re
from agent.state import AgentState
from agent.utils.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

def clean_json_string(content_str: str) -> str:
    """
    Attempt to clean up common JSON formatting errors from LLM output.
    """
    content_str = content_str.strip()
    
    # Remove markdown code blocks
    if content_str.startswith("```json"):
        content_str = content_str[7:]
    if content_str.endswith("```"):
        content_str = content_str[:-3]
    if content_str.startswith("```"):
        content_str = content_str[3:]
        
    content_str = content_str.strip()
    
    # Sometimes LLM outputs text before or after JSON, try to find the JSON object/array
    # Find first '{' and last '}'
    start = content_str.find("{")
    end = content_str.rfind("}")
    if start != -1 and end != -1:
        content_str = content_str[start:end+1]
        
    return content_str

async def summarize_item(llm, content, language, output_format):
    text = content.get("content", "")
    url = content.get("url", "N/A")
    title = content.get("title", "No Title")
    thumbnail = content.get("thumbnail", "")
    description = content.get("description", "")
    
    if not text:
        return None
        
    summary_data = []
    category = "General"
    
    if llm:
        # Ask LLM to return a JSON array of sentences AND a category
        prompt = f"""
        Task: Summarize the following content in {language}.
        
        Requirements:
        1. LANGUAGE: The summary MUST be written in {language} ONLY. Do not use any other language for the summary text itself.
        2. POINTS: Provide 3 to 5 key points as distinct sentences.
        3. TERMS: If technical terms are used, include the original English term in parentheses (e.g., "생성형 AI (Generative AI)").
        4. CATEGORY: Assign a category to this content (e.g., "Concept", "News", "Tutorial", "Industry Case", "Opinion", "Tool").
        
        Format the output strictly as a JSON object with keys:
        - "points": [list of strings]
        - "category": "string"
        
        Content:
        {text[:5000]} 
        """
        try:
            response = await llm.ainvoke([SystemMessage(content=f"You are a helpful research assistant. You MUST output ONLY in {language}."), HumanMessage(content=prompt)])
            content_str = clean_json_string(response.content)
            
            try:
                parsed = json.loads(content_str)
            except json.JSONDecodeError:
                print(f"JSON Parse Error for {url}. Attempting recovery...")
                # Recovery Strategy 1: Regex extraction
                try:
                    points_match = re.search(r'"points":\s*\[(.*?)\]', content_str, re.DOTALL)
                    category_match = re.search(r'"category":\s*"([^"]+)"', content_str)
                    
                    if points_match:
                        # Try to parse just the list part
                        points_str = f"[{points_match.group(1)}]"
                        # Fix common trailing comma issue like ["a", "b",]
                        points_str = re.sub(r',\s*\]', ']', points_str)
                        summary_data = json.loads(points_str)
                    
                    if category_match:
                        category = category_match.group(1)
                        
                    if not summary_data:
                         raise ValueError("Regex failed")
                         
                except Exception as e:
                    # Recovery Strategy 2: Fallback to raw text
                    # If completely broken, just treat the whole content as one summary point (cleaned up)
                    print(f"Recovery failed: {e}. Using raw text.")
                    raw_text = response.content.strip()
                    # Remove markdown blocks if still present
                    if raw_text.startswith("```"): raw_text = raw_text.split("\n", 1)[-1]
                    if raw_text.endswith("```"): raw_text = raw_text.rsplit("\n", 1)[0]
                    
                    summary_data = [raw_text]
                    category = "Uncategorized"
            
            if not summary_data and parsed:
                 summary_data = parsed.get("points", [])
                 category = parsed.get("category", "General")
            
            if not isinstance(summary_data, list):
                if summary_data:
                    summary_data = [str(summary_data)]
                else:
                    summary_data = ["Summary generation failed."]
                
        except Exception as e:
            summary_data = [f"Error generating summary: {e}"]
    else:
         summary_data = [f"(Mock Summary) {text[:200]}..."]

    date = content.get("published_date", "")

    # Construct result object (without description)
    result_obj = {
        "title": title,
        "summary": summary_data,
        "category": category,
        "source": url,
        "date": date,
        "thumbnail": thumbnail
    }

    # Return object directly (don't json dump yet if we want to process it later)
    # But current architecture passes strings. Let's dump to string but include category.
    if output_format == "json":
        return json.dumps(result_obj, ensure_ascii=False)
    else:
        # Markdown formatting - simplified, report generator will handle grouping if possible.
        # But wait, Summarization node returns list of strings.
        # Report generator needs structured data to group by category.
        # We should return the JSON string representation and let Report Generator parse it.
        return json.dumps(result_obj, ensure_ascii=False) # Always return JSON string internally for consistency


async def summarization_async(state: AgentState):
    print("--- Summarization Agent: Summarizing content (Async) ---")
    contents = state.get("contents", [])
    language = state.get("language", "Korean")
    output_format = state.get("format", "markdown")
    
    llm = get_llm()
    
    # Process all items in parallel
    tasks = [summarize_item(llm, content, language, output_format) for content in contents]
    results = await asyncio.gather(*tasks)
    
    # Filter Nones
    summaries = [r for r in results if r is not None]
         
    return {"summaries": summaries}

def summarization_node(state: AgentState):
    return asyncio.run(summarization_async(state))
