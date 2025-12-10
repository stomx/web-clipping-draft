from datetime import datetime, timedelta
from typing import Dict, Any, Optional

def create_graph_inputs(
    query: str,
    lang: str = "Korean",
    format: str = "json",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    count: int = 5
) -> Dict[str, Any]:
    """
    Constructs the input dictionary for the LangGraph agent.
    
    Args:
        query: Research topic
        lang: Output language
        format: Output format (markdown/json)
        start_date: Start date for search (YYYY-MM-DD)
        end_date: End date for search (YYYY-MM-DD)
        start_time: Start time (HH:MM:SS)
        end_time: End time (HH:MM:SS)
        count: Target number of summaries
        
    Returns:
        Dictionary compatible with AgentState
    """
    
    # Set default dates if not provided
    now = datetime.now()
    if not end_date:
        end_date = now.strftime("%Y-%m-%d")
    if not start_date:
        yesterday = now - timedelta(days=1)
        start_date = yesterday.strftime("%Y-%m-%d")
        
    if not end_time:
        end_time = now.strftime("%H:%M:%S")
    if not start_time:
        start_time = "00:00:00"

    inputs = {
        "query": query,
        "language": lang,
        "format": format,
        "date_range": {
            "startDate": start_date,
            "endDate": end_date,
            "startTime": start_time,
            "endTime": end_time
        },
        "target_count": count,
        "depth": 0,
        "max_depth": 0 
    }
    
    return inputs
