import uvicorn
from fastapi import FastAPI
from oxyde import db

from oxyde_config import DATABASES
from routes import users, posts, comments, tags

app = FastAPI(
    title="Blog API",
    description="REST API for blog with Oxyde ORM",
    version="0.1.0",
    lifespan=db.lifespan(**DATABASES)
)

app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(tags.router)


@app.get("/")
async def root():
    return {"message": "Blog API is running!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
