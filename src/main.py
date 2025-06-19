from fastapi import FastAPI, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import os
from dotenv import load_dotenv
from typing import Optional

app = FastAPI(title="NGO Website API", description="API for www.jemcrownfoundation.org managing blogs and engagement", version="0.1.0")

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

# Pydantic model for blog post validation
class BlogPost(BaseModel):
    title: str
    content: str
    timestamp: str

# Pydantic model for engagement data
class EngagementData(BaseModel):
    page: str
    duration: float
    timestamp: Optional[str] = None

# In-memory stores
engagement_data = []  # Added missing definition

# API key security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail={"error": "Invalid API key"})
    return api_key

# Role-based access
def get_role(api_key: str):
    if api_key == API_KEY and "admin" in api_key.lower():  # Case-insensitive check
        return "admin"
    return "user"

# Database setup
def init_db():
    conn = sqlite3.connect("ngo_database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS blog_posts 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.post("/blog/add")
async def add_blog_post(title: str = Form(...), content: str = Form(...), api_key: str = Depends(get_api_key)):
    role = get_role(api_key)
    if role != "admin":
        raise HTTPException(status_code=403, detail={"error": "Admin access required"})
    try:
        post = BlogPost(title=title, content=content, timestamp=datetime.now().isoformat())
        conn = sqlite3.connect("ngo_database.db")
        c = conn.cursor()
        c.execute("INSERT INTO blog_posts (title, content, timestamp) VALUES (?, ?, ?)",
                  (post.title, post.content, post.timestamp))
        conn.commit()
        conn.close()
        return JSONResponse(content={"status": "added", "post_id": c.lastrowid})
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"error": "Invalid blog post data", "message": str(e)})

@app.get("/blog/list")
async def list_blog_posts(api_key: str = Depends(get_api_key)):
    conn = sqlite3.connect("ngo_database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM blog_posts")
    posts = [{"id": row[0], "title": row[1], "content": row[2], "timestamp": row[3]} for row in c.fetchall()]
    conn.close()
    return JSONResponse(content=posts)

@app.put("/blog/update/{post_id}")
async def update_blog_post(post_id: int, title: str = Form(None), content: str = Form(None), api_key: str = Depends(get_api_key)):
    role = get_role(api_key)
    if role != "admin":
        raise HTTPException(status_code=403, detail={"error": "Admin access required"})
    if title is None and content is None:
        raise HTTPException(status_code=400, detail={"error": "At least one field (title or content) is required"})
    conn = sqlite3.connect("ngo_database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM blog_posts WHERE id = ?", (post_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail={"error": "Post not found"})
    updates = {}
    if title:
        updates["title"] = title
    if content:
        updates["content"] = content
    updates["timestamp"] = datetime.now().isoformat()
    c.execute("UPDATE blog_posts SET title = COALESCE(?, title), content = COALESCE(?, content), timestamp = ? WHERE id = ?",
              (title, content, updates["timestamp"], post_id))
    conn.commit()
    conn.close()
    return JSONResponse(content={"status": "updated", "post_id": post_id})

@app.delete("/blog/delete/{post_id}")
async def delete_blog_post(post_id: int, api_key: str = Depends(get_api_key)):
    role = get_role(api_key)
    if role != "admin":
        raise HTTPException(status_code=403, detail={"error": "Admin access required"})
    conn = sqlite3.connect("ngo_database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM blog_posts WHERE id = ?", (post_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail={"error": "Post not found"})
    c.execute("DELETE FROM blog_posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return JSONResponse(content={"status": "deleted", "post_id": post_id})

@app.post("/track/engagement")
async def track_engagement(page: str = Form(...), duration: float = Form(...), api_key: str = Depends(get_api_key)):
    try:
        entry = EngagementData(page=page, duration=duration, timestamp=datetime.now().isoformat())
        engagement_data.append(entry.dict())  # Now defined
        return JSONResponse(content={"status": "tracked", "entry_count": len(engagement_data)})
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"error": "Invalid engagement data", "message": str(e)})

@app.get("/engagement/stats")
async def get_engagement_stats(api_key: str = Depends(get_api_key)):
    total_duration = sum(entry["duration"] for entry in engagement_data)  # Now defined
    return JSONResponse(content={"total_visits": len(engagement_data), "total_duration": total_duration})

@app.get("/calculate")
async def calculate(operation: str, a: float, b: float, api_key: str = Depends(get_api_key)):
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