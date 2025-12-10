import json
from collections import defaultdict
from agent.state import AgentState

def report_generator_node(state: AgentState):
    print("--- Report Generator Agent: Compiling report ---")
    query = state.get("query", "Unknown Query")
    summaries = state.get("summaries", [])
    output_format = state.get("format", "markdown")
    
    # Parse summaries
    parsed_summaries = []
    for s in summaries:
        try:
            parsed_summaries.append(json.loads(s))
        except:
            # Fallback for old string format or errors
            parsed_summaries.append({"title": "Unknown", "summary": [s], "category": "Uncategorized", "source": "", "thumbnail": ""})
            
    # Group by Category
    grouped = defaultdict(list)
    for item in parsed_summaries:
        cat = item.get("category", "General")
        grouped[cat].append(item)
    
    if output_format == "json":
        report_data = {
            "query": query,
            "source_summaries": parsed_summaries # Flat list with categories
            # Or structured: "categories": {cat: [items]}
        }
        return {"report": json.dumps(report_data, ensure_ascii=False, indent=2)}
    
    else:
        # Markdown generation (Flat list, no categories)
        report = f"# Research Report: {query}\n\n"
        
        for item in parsed_summaries:
            title = item.get("title")
            url = item.get("source")
            thumbnail = item.get("thumbnail")
            points = item.get("summary", [])
            
            report += f"### {title}\n\n"
            
            # Summary points first
            if isinstance(points, list):
                for point in points:
                    report += f"- {point}\n"
            else:
                report += f"{points}\n"
            report += "\n"
            
            # Source URL and Date
            if url:
                date_str = f" ({item.get('date')})" if item.get('date') else ""
                report += f"**출처**: [{url}]({url}){date_str}\n\n"
            
            # Thumbnail
            if thumbnail:
                report += f"![thumbnail]({thumbnail})\n\n"
            
            report += "---\n\n"
            
        return {"report": report}
