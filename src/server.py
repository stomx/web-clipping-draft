import sys
from pathlib import Path
import json
import asyncio
from typing import Optional, Dict, Any

# Add project root to python path to allow importing from src
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from src.graph import create_graph
from src.utils.input_handler import create_graph_inputs
from src.utils.job_manager import job_manager, JobStatus

# Load env variables
load_dotenv()

app = FastAPI(title="Web Research Agent API")

# Initialize the graph
graph = create_graph()

class ResearchRequest(BaseModel):
    query: str = Field(..., description="Research topic")
    lang: str = Field(default="Korean", description="Output language")
    format: str = Field(default="json", description="Output format (markdown or json)")
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
                async for event in graph.astream(inputs):
                    data = json.dumps(event, default=str, ensure_ascii=False)
                    yield f"data: {data}\n\n"
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