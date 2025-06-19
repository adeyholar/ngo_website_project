from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from datetime import datetime  # Added import

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

# New calculator endpoints
@app.get("/calculate")
async def calculate(operation: str, a: float, b: float):
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            return JSONResponse(status_code=400, content={"error": "Division by zero"})
        result = a / b
    else:
        return JSONResponse(status_code=400, content={"error": "Invalid operation"})
    return JSONResponse(content={"operation": operation, "result": result})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)