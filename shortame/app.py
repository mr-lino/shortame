from dataclasses import asdict
from typing import Annotated

from fastapi import Body, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from loguru import logger
from pydantic import HttpUrl

from shortame.config import settings
from shortame.services.url_services import UrlShortener

logger.add(sink="app.log")

app = FastAPI()

ORIGINS = ["http://localhost:5000", "http://127.0.0.1:5000", settings.domain_name]

METHODS = ["GET", "POST"]

HEADERS = ["*"]

app.add_middleware(
    CORSMiddleware, allow_origins=ORIGINS, allow_methods=METHODS, allow_headers=HEADERS
)


@app.post("/url", status_code=status.HTTP_200_OK)
async def url(long_url: Annotated[HttpUrl, Body(embed=True)]):
    shortener = UrlShortener()
    url = shortener.shorten_and_persist(long_url=long_url.unicode_string())
    return asdict(url)


@app.get("/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect():
    pass
