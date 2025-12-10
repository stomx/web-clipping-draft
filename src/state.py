import operator
from typing import TypedDict, Annotated, List, Dict, Any, Union

class AgentState(TypedDict):
    query: str
    language: str  # Output language
    format: str # Output format (markdown or json)
    date_range: Dict[str, str] # {startDate, endDate, startTime, endTime}
    target_count: int # Target number of successful extractions
    
    # Deep Research
    depth: int # Current recursion depth (starts at 0)
    max_depth: int # Max recursion depth
    
    search_results: Annotated[List[Dict[str, Any]], operator.add]
    contents: Annotated[List[Dict[str, Any]], operator.add]  # content from web or youtube transcript
    summaries: Annotated[List[str], operator.add] # Stores formatted string blocks (for MD) or JSON strings
    
    analysis: str
    report: str
    errors: Annotated[List[str], operator.add]
