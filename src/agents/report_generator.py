import json
from collections import defaultdict
from src.state import AgentState

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
            parsed_summaries.append({"title": "Unknown", "summary": [s], "category": "Uncategorized", "source": "", "thumbnail": "", "description": ""})
            
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
        # Markdown generation with Categories
        report = f"# Research Report: {query}\n\n"
        
        # Sort categories to have Concept/General first? (Optional)
        # For now alphabetical or simple iteration
        
        for category, items in grouped.items():
            report += f"## {category}\n\n"
            for item in items:
                title = item.get("title")
                url = item.get("source")
                thumbnail = item.get("thumbnail")
                desc = item.get("description")
                points = item.get("summary", [])
                
                report += f"### {title}\n"
                if thumbnail:
                    report += f"![Thumbnail]({thumbnail})\n\n"
                
                report += "**Summary:**\n"
                if isinstance(points, list):
                    for point in points:
                        report += f"- {point}\n"
                else:
                    report += f"{points}\n"
                report += "\n"
                
                if desc:
                    report += f"**Description:** {desc}\n\n"
                report += f"**Source:** {url}\n\n"
                report += "---\n\n"
            
        return {"report": report}
