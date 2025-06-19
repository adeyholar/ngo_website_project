from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

app = FastAPI()

# Pydantic model for blog post validation
class BlogPost(BaseModel):
    title: str
    content: str
    timestamp: Optional[str] = None

# In-memory store for blog posts
blog_posts = []

@app.post("/blog/add")
async def add_blog_post(title: str = Form(...), content: str = Form(...)):
    try:
        # Validate and create blog post
        post = BlogPost(title=title, content=content, timestamp=datetime.now().isoformat())
        blog_posts.append(post.dict())
        return JSONResponse(content={"status": "added", "post_count": len(blog_posts)})
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"error": "Invalid blog post data", "message": str(e)})

@app.get("/blog/list")
async def list_blog_posts():
    return JSONResponse(content=blog_posts)

# Calculator endpoint with validation
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