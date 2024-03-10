import logging
import colorlog
import pathlib
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
import uvicorn


from sqlalchemy import text
from sqlalchemy.orm import Session

from .src.conf.config import settings
from .src.database.db import get_db, get_redis
from .src.database import db
from .src.routes import contacts, auth, users

logger = logging.getLogger(f"{settings.app_name}")
logger.setLevel(logging.DEBUG if settings.app_mode == "dev" else logging.INFO)
handler = colorlog.StreamHandler()
handler.setLevel(logging.DEBUG if settings.app_mode == "dev" else logging.INFO)
handler.setFormatter(colorlog.ColoredFormatter("%(yellow)s%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("lifespan before")
    try:
        await startup()
    except redis.ConnectionError as err:
        logger.error(f"redis err: {err}")
    except Exception as err:
        logger.error(f"other app err: {err}")
    yield
    logger.debug("lifespan after")



app = FastAPI(lifespan=lifespan)


# @app.on_event("startup")
async def startup():
    redis_live: bool | None = await db.check_redis()
    if not redis_live:
        # db.redis_pool = False
        app.dependency_overrides[get_redis] = deny_get_redis
        logger.debug("startup DISABLE REDIS THAT DOWN")
    else:
        await FastAPILimiter.init(get_redis())
        app.dependency_overrides[get_limit] = RateLimiter(
            times=settings.reate_limiter_times, seconds=settings.reate_limiter_seconds
        )
        logger.debug("startup done")


origins = ["http://localhost:3002"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_limit():
    return None


async def deny_get_redis():
    return None


static_dir: pathlib.Path = pathlib.Path(settings.STATIC_DIRECTORY)


class StaticFilesCache(StaticFiles):
    def __init__(self, *args, cachecontrol="public, max-age=31536000, s-maxage=31536000, immutable", **kwargs):
        self.cachecontrol = cachecontrol
        super().__init__(*args, **kwargs)

    def file_response(self, *args, **kwargs) -> Response:
        resp: Response = super().file_response(*args, **kwargs)
        resp.headers.setdefault("Cache-Control", self.cachecontrol)
        return resp


def add_static(_app):
    _app.mount(
        path="/static",
        app=StaticFilesCache(directory=settings.STATIC_DIRECTORY, cachecontrol="private, max-age=3600"),
        name="static",
    )
    _app.mount(path="/sphinx", app=StaticFilesCache(directory=settings.SPHINX_DIRECTORY, html=True), name="sphinx")


templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "tilte": f"{settings.app_version.upper()} APP {settings.app_name.upper()}"}
    )


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": f"Welcome to FastAPI on Howe Work 14 APP: {settings.app_name.upper()}!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )


app.include_router(
    contacts.router,
    prefix="/api",
    dependencies=[Depends(get_limit)],
)
app.include_router(
    auth.router,
    prefix="/api/auth",
    dependencies=[Depends(get_limit)],
)
app.include_router(users.router, prefix="/api")

add_static(app)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.app_host, port=settings.app_port, reload=True)