from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import sqlite3

app = FastAPI(title="NGO Website API", description="API for www.jemcrownfoundation.org managing blogs and engagement", version="0.1.0")

# Pydantic model for blog post validation
class BlogPost(BaseModel):
    title: str
    content: str
    timestamp: str

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
async def add_blog_post(title: str = Form(...), content: str = Form(...)):
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
async def list_blog_posts():
    conn = sqlite3.connect("ngo_database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM blog_posts")
    posts = [{"id": row[0], "title": row[1], "content": row[2], "timestamp": row[3]} for row in c.fetchall()]
    conn.close()
    return JSONResponse(content=posts)

@app.put("/blog/update/{post_id}")
async def update_blog_post(post_id: int, title: str = Form(None), content: str = Form(None)):
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
async def delete_blog_post(post_id: int):
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

# Existing engagement and calculator endpoints remain unchanged
# ... (keep the engagement and calculate endpoints as in the previous version)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)