from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI()

# 1. CORS ආරක්ෂාව (Blogger එකට විතරක් ඉඩ දීම)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-blog-name.blogspot.com", # ඔයාගේ blogger link එක මෙතන දාන්න
        "http://localhost:8000",                # පරීක්ෂණ කටයුතු සඳහා
        "null"                                  # සමහර විට Local file වලින් run කරන විට අවශ්‍ය වේ
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PlaylistRequest(BaseModel):
    url: str

@app.post("/analyze")
def analyze_playlist(data: PlaylistRequest, x_api_key: str = Header(None)):
    # 2. API Key එකක් පාවිච්චි කිරීම
    SECRET_KEY = "MySecretStartupKey123" 
    
    if x_api_key != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized access!")

    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': 'in_playlist',
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data.url, download=False)
            entries_raw = info.get('entries', [])
            
            video_list = []
            total_seconds = 0
            for entry in entries_raw:
                if entry:
                    # මෙන්න මෙතන .get('duration') පස්සේ , 0 එකතු කරන්න
                    d = entry.get('duration', 0) 
                    
                    # තවදුරටත් ආරක්ෂිත වෙන්න මේ පරීක්ෂාවත් දාමු
                    if d is None:
                        d = 0
                        
                    total_seconds += d
                    video_list.append({
                        "title": entry.get('title', 'Untitled Video'),
                        "duration": d
                    })
            
            return {
                "status": "success",
                "title": info.get('title', 'Playlist'),
                "total_duration": total_seconds,
                "entries": video_list
            }
	
    except Exception as e:
        return {"status": "error", "message": str(e)}