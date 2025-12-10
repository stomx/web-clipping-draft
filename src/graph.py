from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.agents.search_agent import search_node
from src.agents.content_extractor import content_extractor_node
from src.agents.summarization_agent import summarization_node
from src.agents.analyzer_agent import analyzer_node
from src.agents.report_generator import report_generator_node

def create_graph():
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("search", search_node)
    workflow.add_node("extract", content_extractor_node)
    workflow.add_node("summarize", summarization_node)
    # workflow.add_node("analyze", analyzer_node) # Removed
    workflow.add_node("report", report_generator_node)
    
    # Define Edges
    workflow.set_entry_point("search")
    
    workflow.add_edge("search", "extract")
    workflow.add_edge("extract", "summarize")
    workflow.add_edge("summarize", "report") # Skip analyze
    # workflow.add_edge("analyze", "report") # Removed
    workflow.add_edge("report", END)
    
    # Compile
    app = workflow.compile()
    return app
