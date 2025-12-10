from agent.state import AgentState
from agent.utils.tools import tavily_search, youtube_search
from agent.utils.ranker import rank_results

def search_node(state: AgentState):
    query = state.get("query", "")
    date_range = state.get("date_range", {})
    
    print(f"--- Search Agent: Searching for '{query}' with range {date_range} ---")
    
    # Fetch ample results to ensure we can meet target_count even with failures
    # Broad Web/Community Search (20 items)
    web_results = tavily_search(query, max_results=20, date_range=date_range)
    
    # YouTube Search (10 items)
    yt_results = youtube_search(query, max_results=10, date_range=date_range)
    
    # Combined results (total ~30 candidates)
    all_results = web_results + yt_results
    
    print(f"--- Search Agent: Reranking {len(all_results)} results (Web/Comm: {len(web_results)}, YT: {len(yt_results)}) ---")
    
    # Rerank and keep top 20 to pass to extractor
    ranked_results = rank_results(query, all_results, top_k=20)
    
    for i, res in enumerate(ranked_results):
        print(f"  - [{i+1}] [{res.get('relevance_score')}/10] {res.get('title')} ({res.get('source')})")
            
    return {"search_results": ranked_results}
