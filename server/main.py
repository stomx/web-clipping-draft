import sys
from pathlib import Path
import json
import asyncio
from typing import Optional, Dict, Any

# Add project root to python path to allow importing from agent
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from agent.graph import create_graph
from agent.utils.input_handler import create_graph_inputs
from server.job_manager import job_manager, JobStatus

# Load env variables
load_dotenv()

app = FastAPI(title="Web Research Agent API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the graph
graph = create_graph()

class ResearchRequest(BaseModel):
    query: str = Field(..., description="Research topic")
    lang: str = Field(default="Korean", description="Output language")
    format: str = Field(default="markdown", description="Output format (markdown or json)")
    start_date: Optional[str] = Field(default=None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="End date (YYYY-MM-DD)")
    start_time: Optional[str] = Field(default=None, description="Start time (HH:MM:SS)")
    end_time: Optional[str] = Field(default=None, description="End time (HH:MM:SS)")
    count: int = Field(default=5, description="Target number of summaries")
    mode: str = Field(default="stream", pattern="^(stream|async)$", description="Execution mode: 'stream' (SSE) or 'async' (polling)")

async def run_research_background(job_id: str, inputs: Dict[str, Any]):
    """
    Executes the research graph in the background and updates job status.
    """
    try:
        job_manager.update_job(job_id, JobStatus.IN_PROGRESS)
        
        # Invoke the graph (await the result)
        result = await graph.ainvoke(inputs)
        
        # The result typically contains the 'report' key or the final state
        # We'll save the whole result for now, or just the report if preferred
        final_report = result.get("report", "No report generated")
        
        job_manager.update_job(job_id, JobStatus.COMPLETED, result={"report": final_report})
        
    except Exception as e:
        print(f"Error processing job {job_id}: {e}")
        job_manager.update_job(job_id, JobStatus.FAILED, error=str(e))

@app.post("/research")
async def research_endpoint(request: ResearchRequest, background_tasks: BackgroundTasks):
    """
    Initiates research. Supports 'stream' (SSE) and 'async' (polling) modes.
    """
    inputs = create_graph_inputs(
        query=request.query,
        lang=request.lang,
        format=request.format,
        start_date=request.start_date,
        end_date=request.end_date,
        start_time=request.start_time,
        end_time=request.end_time,
        count=request.count
    )

    if request.mode == "stream":
        async def event_generator():
            try:
                # Use astream_events v2 for granular updates (including LLM outputs)
                async for event in graph.astream_events(inputs, version="v2"):
                    kind = event["event"]
                    
                    # 1. Custom handling for individual LLM outputs (Summaries)
                    if kind == "on_chat_model_end":
                        # We only want summaries, not other LLM calls (if any)
                        # We can try to infer context or just process all valid JSONs
                        data = event["data"]["output"].content
                        
                        # Try to detect if it's a summary result (JSON structure)
                        # This is a bit loose but effective for streaming visibility
                        try:
                            # Verify it looks like our summary structure
                            # It might be a Raw string if regex failed inside agent, but usually it's JSON string
                            # The agent returns a list of strings, but here we catch the raw LLM output
                            # The LLM output is what we want to stream immediately
                            
                            # Clean it up slightly for the client
                            cleaned_data = data.strip()
                            if cleaned_data.startswith("```json"):
                                cleaned_data = cleaned_data[7:-3]
                            elif cleaned_data.startswith("```"):
                                cleaned_data = cleaned_data[3:-3]
                                
                            # Send as a special event type for the client to render incrementally
                            payload = json.dumps({"custom_summary": cleaned_data}, ensure_ascii=False)
                            yield f"data: {payload}\n\n"
                        except:
                            pass

                    # 2. Standard State Updates (Node completions)
                    # on_chain_end usually corresponds to a node finishing in LangGraph
                    elif kind == "on_chain_end":
                         # We can also look for 'on_chain_end' with name 'LangGraph' or specific node names
                         # But simplistic approach: if it has output that matches our state keys
                         output = event["data"].get("output")
                         if output and isinstance(output, dict):
                             # Filter out huge dumps, we just want specific keys
                             if any(k in output for k in ["search_results", "contents", "summaries", "report"]):
                                 payload = json.dumps(output, default=str, ensure_ascii=False)
                                 yield f"data: {payload}\n\n"

            except Exception as e:
                error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
                yield f"data: {error_data}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    
    elif request.mode == "async":
        job_id = job_manager.create_job()
        background_tasks.add_task(run_research_background, job_id, inputs)
        return {
            "job_id": job_id, 
            "status": JobStatus.PENDING, 
            "message": "Research started in background. Check status at GET /jobs/{job_id}"
        }

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Retrieves the status and result of an async job.
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)