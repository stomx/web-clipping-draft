from agent.state import AgentState
from agent.utils.tools import fetch_web_content, fetch_youtube_transcript

import asyncio
import aiohttp
from agent.state import AgentState
from agent.utils.async_tools import fetch_web_content_async, fetch_youtube_transcript

async def process_item(session, item):
    """
    Process a single search result item.
    """
    source_type = item.get("source")
    thumbnail = item.get("thumbnail", "")
    description = item.get("description", "")
    content_data = None
    
    # Try fetching full content
    try:
        if source_type in ["web", "community"]: 
            fetched_data = await fetch_web_content_async(session, item.get("url"))
            if fetched_data:
                content_data = fetched_data.get("text")
                if fetched_data.get("thumbnail"): thumbnail = fetched_data.get("thumbnail")
                if fetched_data.get("description"): description = fetched_data.get("description")
                
        elif source_type == "youtube":
            content_data = await asyncio.to_thread(fetch_youtube_transcript, item.get("video_id"))
    except Exception as e:
        print(f"Extraction error for {item.get('url')}: {e}")

    # Fallback: Use content provided by search API (Tavily) if fetch failed
    if not content_data and item.get("content"):
        print(f"  -> Using fallback content for {item.get('url')}")
        content_data = item.get("content")
        
    if content_data:
        return {
            "url": item.get("url"),
            "title": item.get("title", "No Title"),
            "content": content_data,
            "type": source_type,
            "thumbnail": thumbnail,
            "description": description,
            "published_date": item.get("published_date", "")
        }
    return None

async def content_extractor_async(state: AgentState):
    print("--- Content Extractor Agent: Fetching content (Async) ---")
    results = state.get("search_results", [])
    target_count = state.get("target_count", 5)
    contents = []
    
    # Process in batches of 5 to respect rate limits and allow early exit
    batch_size = 5
    
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(results), batch_size):
            # Check if we have enough
            if len(contents) >= target_count:
                break
                
            batch = results[i : i + batch_size]
            print(f"--- Extractor: Processing batch {i//batch_size + 1} (Items {i+1}-{i+len(batch)})... ---")
            
            tasks = [process_item(session, item) for item in batch]
            batch_results = await asyncio.gather(*tasks)
            
            for res in batch_results:
                if res:
                    contents.append(res)
                    if len(contents) >= target_count:
                        break
            
            print(f"--- Extractor: Currently have {len(contents)}/{target_count} items ---")

    print(f"--- Extractor: Finished with {len(contents)} items ---")
    return {"contents": contents}

def content_extractor_node(state: AgentState):
    # Wrapper to run async function in sync graph
    return asyncio.run(content_extractor_async(state))
