from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from datetime import datetime

app = FastAPI()

# In-memory store for blog posts
blog_posts = []

@app.post("/blog/add")
async def add_blog_post(title: str = Form(...), content: str = Form(...)):
    post = {"title": title, "content": content, "timestamp": datetime.now().isoformat()}
    blog_posts.append(post)
    return JSONResponse(content={"status": "added", "post_count": len(blog_posts)})

@app.get("/blog/list")
async def list_blog_posts():
    return JSONResponse(content=blog_posts)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)