from agent.state import AgentState
from agent.utils.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

def analyzer_node(state: AgentState):
    print("--- Analyzer Agent: Analyzing trends and sentiment ---")
    summaries = state.get("summaries", [])
    language = state.get("language", "Korean")
    combined_summaries = "\n\n".join(summaries)
    
    analysis_result = ""
    llm = get_llm()
    
    if llm and combined_summaries:
        prompt = f"""
        Analyze the following summaries. 
        1. Identify key trends.
        2. Verify source credibility (general assessment).
        3. Analyze overall sentiment.
        
        Write the analysis in {language}.
        
        Summaries:
        {combined_summaries}
        """
        try:
            response = llm.invoke([SystemMessage(content=f"You are an expert analyst. Always answer in {language}."), HumanMessage(content=prompt)])
            analysis_result = response.content
        except Exception as e:
            analysis_result = f"Error during analysis: {e}"
    else:
        analysis_result = "Analysis not possible (No LLM or no summaries)."
        
    return {"analysis": analysis_result}

