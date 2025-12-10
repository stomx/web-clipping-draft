import json
from typing import List, Dict, Any
from src.utils.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

def rank_results(query: str, results: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Rerank search results using LLM based on relevance to the query.
    """
    if not results:
        return []
    
    llm = get_llm()
    if not llm:
        # Fallback: Just return the top_k results as is if no LLM
        return results[:top_k]

    # Prepare input for LLM
    candidates_text = ""
    for i, res in enumerate(results):
        candidates_text += f"[{i}] Title: {res.get('title')}\n    Snippet: {res.get('description', '')[:200]}\n    Source: {res.get('source')}\n\n"

        prompt = f"""

        You are a Search Relevance Ranker.

        

        Query: "{query}"

        

        Task: 

        1. Rank the following search results based on their relevance, information density, and credibility.

        2. DEDUPLICATE: If multiple results convey the exact same information (e.g. same press release on different sites), keep only the best source and discard the others (score 0).

        3. DIVERSITY: Prefer a diverse set of sources (e.g. mix of official docs, news, videos, community discussions).

        

        Return a JSON object with a key "rankings" containing a list of objects.

        Each object must have:

        - "index": (int) the original index of the result [0, 1, ...]

        - "score": (int) relevance score from 0 to 10. Give 0 if irrelevant or duplicate.

        - "reason": (string) brief reason for the score

        

        Results to Rank:

        {candidates_text}

        """

    try:
        response = llm.invoke([
            SystemMessage(content="You are a precise ranking algorithm. Output valid JSON only."), 
            HumanMessage(content=prompt)
        ])
        
        content_str = response.content.strip()
        if content_str.startswith("```json"):
            content_str = content_str[7:-3].strip()
        elif content_str.startswith("```"):
            content_str = content_str[3:-3].strip()
            
        data = json.loads(content_str)
        rankings = data.get("rankings", [])
        
        # Map scores back to results
        ranked_results = []
        for r in rankings:
            idx = r.get("index")
            if idx is not None and 0 <= idx < len(results):
                item = results[idx]
                item["relevance_score"] = r.get("score", 0)
                item["relevance_reason"] = r.get("reason", "")
                ranked_results.append(item)
        
        # Sort by score descending
        ranked_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Return top K
        return ranked_results[:top_k]

    except Exception as e:
        print(f"Ranking error: {e}")
        # Fallback to original order
        return results[:top_k]
