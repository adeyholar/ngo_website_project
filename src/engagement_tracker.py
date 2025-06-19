from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
import json
import os

app = FastAPI()

# Load or initialize engagement data from a file
DATA_FILE = "engagement_data.json"
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        engagement_data = json.load(f)
else:
    engagement_data = []

@app.post("/track/engagement")
async def track_engagement(page: str = None, duration: float = None):  # Query parameters
    if page is None or duration is None:
        return JSONResponse(status_code=400, content={"detail": "Both 'page' and 'duration' are required query parameters"})
    entry = {"page": page, "duration": duration, "timestamp": datetime.now().isoformat()}
    engagement_data.append(entry)
    # Save to file for persistence
    with open(DATA_FILE, "w") as f:
        json.dump(engagement_data, f)
    return JSONResponse(content={"status": "tracked", "count": len(engagement_data)})

@app.get("/engagement/stats")
async def get_engagement_stats():
    total_duration = sum(entry["duration"] for entry in engagement_data)
    return JSONResponse(content={"total_visits": len(engagement_data), "total_duration": total_duration})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)