import os
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

from datetime import datetime

def tavily_search(query: str, max_results=5, date_range=None):
    """
    Search web using Tavily API. 
    Includes generic web and specific community domains to get broad coverage.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("Warning: TAVILY_API_KEY not found. Returning mock data.")
        return [{"url": "https://en.wikipedia.org/wiki/Artificial_intelligence", "content": "Mock Result", "score": 0.9}]
    
    try:
        client = TavilyClient(api_key=api_key)
        
        # We can explicitly include domains if we want to ensure coverage, 
        # or just let Tavily search everything.
        # To make it "platform agnostic" but inclusive, we can just search normally.
        # But if we want to ensure community sites are candidates, we can add them to the query 
        # or just rely on the high max_results.
        
        # Calculate days for max info
        days = 3 # Default to recent 3 days if no range
        if date_range and date_range.get("startDate"):
            try:
                start_date_str = date_range.get("startDate")
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                delta = datetime.now() - start_date
                days = max(1, delta.days + 1) # Ensure at least 1 day
            except Exception as e:
                print(f"Error parsing start date: {e}")

        # Use advanced search depth to get more metadata like published_date
        search_params = {
            "query": query, 
            "max_results": max_results,
            "search_depth": "advanced",
            "days": days
        }
        
        response = client.search(**search_params)
        
        # Debug: Check if published_date is present
        if response.get("results"):
            print(f"DEBUG: First result keys: {response['results'][0].keys()}")
            print(f"DEBUG: First result date: {response['results'][0].get('published_date')}")
        
        results = []
        for r in response.get("results", []):
            # Check domain to tag source roughly (optional but helpful for reranker)
            url = r.get("url", "")
            if any(d in url for d in ["reddit.com", "news.ycombinator.com", "velog.io", "medium.com"]):
                r["source"] = "community"
            else:
                r["source"] = "web"
                
            # Ensure content/snippet is preserved
            if "content" not in r and "snippet" in r:
                r["content"] = r["snippet"]
            results.append(r)
        return results
    except Exception as e:
        print(f"Tavily search error: {e}")
        return []

# Removed separate community_search as it is now merged or we just use broad search


def youtube_search(query: str, max_results=3, date_range=None):
    """
    Search YouTube videos.
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("Warning: YOUTUBE_API_KEY not found. Returning mock data.")
        # Use a video that definitely has captions
        return [{
            "url": "https://www.youtube.com/watch?v=Ai8xZp3_33g", 
            "title": "Mock Video (AI)", 
            "video_id": "Ai8xZp3_33g", 
            "source": "youtube",
            "thumbnail": "https://i.ytimg.com/vi/Ai8xZp3_33g/hqdefault.jpg",
            "description": "Mock description for the video."
        }]

    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        publishedAfter = None
        publishedBefore = None
        
        if date_range:
            # Convert to RFC 3339 format (YYYY-MM-DDThh:mm:ssZ)
            s_date = date_range.get("startDate")
            s_time = date_range.get("startTime", "00:00:00")
            e_date = date_range.get("endDate")
            e_time = date_range.get("endTime", "23:59:59")
            
            if s_date:
                publishedAfter = f"{s_date}T{s_time}Z"
            if e_date:
                publishedBefore = f"{e_date}T{e_time}Z"

        request = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=max_results,
            publishedAfter=publishedAfter,
            publishedBefore=publishedBefore
        )
        response = request.execute()
        
        results = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            
            # Extract high res thumbnail if available, else default
            thumbnails = snippet.get("thumbnails", {})
            thumb_url = thumbnails.get("high", {}).get("url") or thumbnails.get("medium", {}).get("url") or thumbnails.get("default", {}).get("url")
            
            results.append({
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "title": snippet["title"],
                "video_id": video_id,
                "source": "youtube",
                "thumbnail": thumb_url,
                "description": snippet.get("description", "")
            })
        return results
    except Exception as e:
        print(f"YouTube search error: {e}")
        return []

def fetch_web_content(url: str):
    """
    Fetch text content and metadata from a URL.
    Returns a dict with 'text', 'thumbnail', 'description'.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Error fetching {url}: Status Code {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from p, h1, h2, h3, li
        tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
        text = ' '.join([t.get_text() for t in tags])
        
        # Extract Metadata
        thumbnail = ""
        description = ""
        
        # OpenGraph Image
        og_image = soup.find("meta", property="og:image")
        if og_image:
            thumbnail = og_image.get("content", "")
            
        # Description (meta description or og:description)
        meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", property="og:description")
        if meta_desc:
            description = meta_desc.get("content", "")
        if not text:
            print(f"Warning: No text found at {url} (Length: {len(response.text)})")
            return None
            
        # Extract Date
        published_date = ""
        date_metas = [
            {"property": "article:published_time"},
            {"name": "date"},
            {"name": "pubdate"},
            {"name": "original-publication-date"},
            {"name": "publication_date"},
            {"property": "og:published_time"}
        ]
        
        for meta_attr in date_metas:
            tag = soup.find("meta", attrs=meta_attr)
            if tag and tag.get("content"):
                published_date = tag.get("content").split("T")[0] # Extract YYYY-MM-DD
                break

        return {
            "text": text[:5000],
            "thumbnail": thumbnail,
            "description": description,
            "published_date": published_date
        }
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def fetch_youtube_transcript(video_id: str):
    """
    Fetch transcript for a YouTube video.
    """
    try:
        # Version 1.2.3 requires instantiation
        api = YouTubeTranscriptApi()
        
        # Fetch transcript (defaults to 'en', can add other languages if needed)
        # Prioritize Korean, then English
        try:
             transcript = api.fetch(video_id, languages=['ko', 'en'])
        except:
             # Fallback to default
             transcript = api.fetch(video_id)
             
        formatter = TextFormatter()
        return formatter.format_transcript(transcript)[:5000] # Limit length

    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}")
        return None
