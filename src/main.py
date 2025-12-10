import argparse
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from src.graph import create_graph

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
    
    inputs = {
        "query": args.query,
        "language": args.lang,
        "format": args.format,
        "date_range": {
            "startDate": args.startDate,
            "endDate": args.endDate,
            "startTime": args.startTime,
            "endTime": args.endTime
        },
        "target_count": args.count,
        "depth": 0,
        "max_depth": 0 # Currently disabling deep loop by default for safety
    }
    
    print(f"Starting research for: {args.query}")
    print(f"Time Range: {args.startDate} {args.startTime} ~ {args.endDate} {args.endTime}")
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

