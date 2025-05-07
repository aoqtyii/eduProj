# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Adjust imports based on your structure
from app.api.endpoints import auth, dashboard, users, courses, lessons, enrollments, progress, practice, mistake_notebook, ai_analysis  # Import courses router
from app.core.config import settings

# from app.db.session import engine # If using Alembic/init_db script
# from app.db.base_class import Base # If using Alembic/init_db script

# Optional: If you need to create tables on startup (not recommended for prod)
# async def create_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="XXX School AI Education Platform API",
    # Optional: Add OpenAPI URL prefix if needed
    # openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Optional: Run create_tables on startup
# @app.on_event("startup")
# async def on_startup():
#     await create_tables()

# CORS Middleware Configuration
# Ensure your frontend origin is allowed
origins = [
    "http://localhost:5173",  # Default Vite dev port
    # Add your production frontend URL here
    # "https://your-ai-education-frontend.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
api_prefix = settings.API_V1_STR
app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{api_prefix}/users", tags=["Users"])
app.include_router(dashboard.router, prefix=f"{api_prefix}/dashboard", tags=["Dashboard"])
app.include_router(courses.router, prefix=f"{api_prefix}/courses", tags=["Courses"])
app.include_router(lessons.router, prefix=f"{api_prefix}/lessons", tags=["Lessons"])  # Add lessons router
app.include_router(enrollments.router, prefix=f"{api_prefix}/enrollments", tags=["Enrollments"])  # Add enrollments
app.include_router(progress.router, prefix=f"{api_prefix}/progress", tags=["Progress"])  # Add progress router
app.include_router(practice.router, prefix=f"{api_prefix}/practice", tags=["Practice Center"])
app.include_router(mistake_notebook.router, prefix=f"{api_prefix}/mistake-notebook", tags=["Mistake Notebook"]) # <--- 添加新路由
app.include_router(ai_analysis.router, prefix=f"{api_prefix}/ai-analysis", tags=["AI Analysis"]) #


# ... include other routers ..

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Education Platform API"}

# Optional: Add basic error handling or logging middleware if needed
# if __name__ == "__main__":
#     import uvicorn
#
#     # 启动 Uvicorn 服务器
#     # 第一个参数 "app.main:app" 是字符串形式的应用路径 (适用于命令行)
#     # 这里我们直接传递 app 对象本身，因为我们就在这个文件里
#     uvicorn.run(
#         app,                     # FastAPI 应用实例
#         host="0.0.0.0",          # 监听的主机地址
#         port=8000,               # 监听的端口
#         reload=True              # 启用自动重载 (开发时方便)
#         # 注意: reload=True 在程序化调用时可能不如命令行 --reload 可靠
#         # 如果遇到问题，可以尝试移除 reload=True，然后通过命令行启动进行开发
#     )