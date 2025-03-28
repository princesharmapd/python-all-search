from .scrappers.tpb import getTPBTorrentData, searchTPB
from .scrappers.i1337x import search1337x, get1337xTorrentData
from .scrappers.nyaa import searchNyaa
from .scrappers.rarbg import searchRarbg, getRarbgTorrentData
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from typing import Optional
from fastapi.responses import JSONResponse
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def errors_handling(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        return JSONResponse(status_code=500, content={'reason': str(exc)})

@app.get("/")
def read_root():
    return {"message": "ok"}

@app.get("/search/1337x")
async def search1337xRoute(q: str, sort_type: Optional[str] = Query(None, regex="^time$|^size$|^seeders$|^leechers$"), sort_mode: Optional[str] = Query(None, regex="^asc$|^desc$"), page: Optional[int] = Query(1, gt=0), nsfw: Optional[bool] = Query(False)):
    torrents, totalPages = await search1337x(q, sort_type, sort_mode, page, nsfw)
    return {"torrents": torrents, "totalPages": totalPages}

@app.get("/search/nyaa")
async def searchNyaaRoute(q: str, sort_type: Optional[str] = Query(None, regex="^time$|^size$|^seeders$|^leechers$"), sort_mode: Optional[str] = Query(None, regex="^asc$|^desc$"), page: Optional[int] = Query(1, gt=0)):
    torrents, totalPages = await searchNyaa(q, sort_type, sort_mode, page)
    return {"torrents": torrents, "totalPages": totalPages}

@app.get("/search/rarbg")
async def searchRarbgRoute(q: str, sort_type: Optional[str] = Query(None, regex="^time$|^size$|^seeders$|^leechers$"), sort_mode: Optional[str] = Query(None, regex="^asc$|^desc$"), page: Optional[int] = Query(1, gt=0), nsfw: Optional[bool] = Query(False)):
    torrents, totalPages = await searchRarbg(q, sort_type, sort_mode, page, nsfw)
    return {"torrents": torrents, "totalPages": totalPages}

@app.get("/search/tpb")
async def searchTPBRoute(q: str, sort_type: Optional[str] = Query(None, regex="^time$|^size$|^seeders$|^leechers$"), sort_mode: Optional[str] = Query(None, regex="^asc$|^desc$"), page: Optional[int] = Query(1, gt=0), nsfw: Optional[bool] = Query(False)):
    torrents, totalPages = await searchTPB(q, sort_type, sort_mode, page, nsfw)
    return {"torrents": torrents, "totalPages": totalPages}

@app.get("/get/1337x")
async def get1337xRoute(link: str):
    return {"data": await get1337xTorrentData(link)}

@app.get("/get/rarbg")
async def getRarbgRoute(link: str):
    return {"data": await getRarbgTorrentData(link)}

@app.get("/get/tpb")
async def getTPBRoute(link: str):
    return {"data": await getTPBTorrentData(link)}

handler = Mangum(app)