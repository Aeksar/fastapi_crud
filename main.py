from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from src.api import task_router, user_router, auth_router
from src.settings import GLOBAL_PREFIX
from src.tasks.config import broker

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not broker.is_worker_process:
        await broker.startup()
    yield
    await broker.shutdown()

app = FastAPI(
    version="1.0",
    debug=True,
    title="Task CRUD",
    description="API с крудами и аутентификацией",
    lifespan=lifespan,
)

app.include_router(task_router, prefix=GLOBAL_PREFIX)
app.include_router(user_router, prefix=GLOBAL_PREFIX)
app.include_router(auth_router, prefix=GLOBAL_PREFIX)

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0")