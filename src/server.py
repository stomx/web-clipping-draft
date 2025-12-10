import sys
import os
from pathlib import Path

# Add project root to python path to allow importing from src
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
import json
import asyncio
from dotenv import load_dotenv

from src.graph import create_graph
from src.utils.input_handler import create_graph_inputs

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

@app.post("/research/stream")
async def stream_research(request: ResearchRequest):
    """
    Streams the progress and results of the web research agent using Server-Sent Events (SSE).
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

    async def event_generator():
        try:
            # Stream events from the graph
            async for event in graph.astream(inputs):
                # The event structure depends on LangGraph output
                # Usually it's a dictionary where keys are node names and values are state updates
                
                # We serialize the entire event to JSON for the client
                data = json.dumps(event, default=str, ensure_ascii=False)
                yield f"data: {data}\n\n"
                
        except Exception as e:
            error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"
        
        # Signal completion (optional, depending on client logic)
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
