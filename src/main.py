from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

app = FastAPI(title="NGO Website API", description="API for www.jemcrownfoundation.org managing blogs and engagement", version="0.1.0")

# Pydantic model for blog post validation
class BlogPost(BaseModel):
    title: str
    content: str
    timestamp: Optional[str] = None

# Pydantic model for engagement data
class EngagementData(BaseModel):
    page: str
    duration: float
    timestamp: Optional[str] = None

# In-memory stores
blog_posts = []
engagement_data = []

@app.post("/blog/add")
async def add_blog_post(title: str = Form(...), content: str = Form(...)):
    try:
        post = BlogPost(title=title, content=content, timestamp=datetime.now().isoformat())
        blog_posts.append(post.dict())
        return JSONResponse(content={"status": "added", "post_count": len(blog_posts)})
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"error": "Invalid blog post data", "message": str(e)})

@app.get("/blog/list")
async def list_blog_posts():
    return JSONResponse(content=blog_posts)

@app.post("/track/engagement")
async def track_engagement(page: str = Form(...), duration: float = Form(...)):
    try:
        entry = EngagementData(page=page, duration=duration, timestamp=datetime.now().isoformat())
        engagement_data.append(entry.dict())
        return JSONResponse(content={"status": "tracked", "entry_count": len(engagement_data)})
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"error": "Invalid engagement data", "message": str(e)})

@app.get("/engagement/stats")
async def get_engagement_stats():
    total_duration = sum(entry["duration"] for entry in engagement_data)
    return JSONResponse(content={"total_visits": len(engagement_data), "total_duration": total_duration})

@app.get("/calculate")
async def calculate(operation: str, a: float, b: float):
    if not operation or not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise HTTPException(status_code=400, detail={"error": "Invalid input parameters"})
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            raise HTTPException(status_code=400, detail={"error": "Division by zero"})
        result = a / b
    else:
        raise HTTPException(status_code=400, detail={"error": "Invalid operation"})
    return JSONResponse(content={"operation": operation, "result": result})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)