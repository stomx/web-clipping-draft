import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_fixed
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# Initialize UserAgent
ua = UserAgent()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def fetch_web_content_async(session, url: str):
    """
    Fetch text content and metadata from a URL asynchronously.
    """
    try:
        headers = {'User-Agent': ua.random}
        async with session.get(url, headers=headers, timeout=15) as response:
            if response.status != 200:
                print(f"Error fetching {url}: Status Code {response.status}")
                return None
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract text
            tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
            text = ' '.join([t.get_text() for t in tags])
            
            # Extract Metadata
            thumbnail = ""
            description = ""
            
            og_image = soup.find("meta", property="og:image")
            if og_image:
                thumbnail = og_image.get("content", "")
                
            meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", property="og:description")
            if meta_desc:
                description = meta_desc.get("content", "")
            
            if not text:
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
                "text": text[:10000], # Increased limit
                "thumbnail": thumbnail,
                "description": description,
                "published_date": published_date
            }
    except Exception as e:
        print(f"Async fetch error {url}: {e}")
        return None

def fetch_youtube_transcript(video_id: str):
    """
    Fetch transcript for a YouTube video. (Sync wrapper, usually fast enough)
    """
    try:
        api = YouTubeTranscriptApi()
        try:
             transcript = api.fetch(video_id, languages=['ko', 'en'])
        except:
             transcript = api.fetch(video_id)
             
        formatter = TextFormatter()
        return formatter.format_transcript(transcript)[:10000]
    except Exception as e:
        # print(f"Error fetching transcript for {video_id}: {e}")
        return None
