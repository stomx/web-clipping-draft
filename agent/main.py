import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to python path to allow importing from agent
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from agent.graph import create_graph
from agent.utils.input_handler import create_graph_inputs

# Load environment variables
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="AI Web Research Agent")
    parser.add_argument("query", type=str, help="Research query topic")
    parser.add_argument("--lang", type=str, default="Korean", help="Output language (default: Korean)")
    parser.add_argument("--format", type=str, default="json", choices=["markdown", "json"], help="Output format (markdown or json)")
    
    # Date/Time arguments
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    
    default_start_date = yesterday.strftime("%Y-%m-%d")
    default_end_date = now.strftime("%Y-%m-%d")
    default_start_time = "00:00:00"
    default_end_time = now.strftime("%H:%M:%S")

    parser.add_argument("--startDate", type=str, default=default_start_date, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--endDate", type=str, default=default_end_date, help="End date (YYYY-MM-DD)")
    parser.add_argument("--startTime", type=str, default=default_start_time, help="Start time (HH:MM:SS)")
    parser.add_argument("--endTime", type=str, default=default_end_time, help="End time (HH:MM:SS)")
    parser.add_argument("--count", type=int, default=5, help="Target number of summaries (default: 5)")
    
    args = parser.parse_args()
    
    app = create_graph()
    
    inputs = create_graph_inputs(
        query=args.query,
        lang=args.lang,
        format=args.format,
        start_date=args.startDate,
        end_date=args.endDate,
        start_time=args.startTime,
        end_time=args.endTime,
        count=args.count
    )
    
    print(f"Starting research for: {args.query}")
    print(f"Time Range: {inputs['date_range']['startDate']} {inputs['date_range']['startTime']} ~ {inputs['date_range']['endDate']} {inputs['date_range']['endTime']}")
    print(f"Language: {args.lang}, Format: {args.format}")
    
    # Run the graph
    result = app.invoke(inputs)
    
    # Output the report
    output_content = result.get("report")
    
    print("\n\n" + "="*50)
    print("FINAL REPORT")
    print("="*50)
    print(output_content)
    
    # Save to file
    ext = "json" if args.format == "json" else "md"
    filename = f"research_report_{args.lang}.{ext}"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(output_content)
    print(f"\nReport saved to {filename}")

if __name__ == "__main__":
    main()

