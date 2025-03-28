import aiohttp
from .utils import toInt, convertBytes, getTPBTrackers

PAGE_COUNT = 20

def sort_torrents(torrents, sort_criteria, sort_mode):
    if not torrents:
        return torrents
        
    if sort_criteria == "seeders":
        reverse = sort_mode != "asc"
        return sorted(torrents, key=lambda x: x.get("seeds", 0), reverse=reverse)
    elif sort_criteria == "leechers":
        reverse = sort_mode != "asc"
        return sorted(torrents, key=lambda x: x.get("leeches", 0), reverse=reverse)
    elif sort_criteria == "size":
        reverse = sort_mode != "asc"
        return sorted(torrents, key=lambda x: x.get("sizeInt", 0), reverse=reverse)
    elif sort_criteria == "time":
        reverse = sort_mode != "asc"
        return sorted(torrents, key=lambda x: x.get("added", 0), reverse=reverse)
    return torrents

async def searchTPB(search_key, sort_criteria=None, sort_mode=None, page=1, nsfw=False):
    torrents = []
    baseUrl = f"https://apibay.org/q.php?q={search_key.replace(' ', '%20')}&cat=100,200,300,400,600"

    if nsfw:
        baseUrl = f"https://apibay.org/q.php?q={search_key.replace(' ', '%20')}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(baseUrl) as response:
                resp_json = await response.json()
    except Exception as e:
        raise Exception(f"Failed to fetch from TPB: {str(e)}")

    if not resp_json or resp_json[0].get("name") == "No results returned":
        return torrents, 1

    for t in resp_json:
        try:
            torrents.append({
                "name": t.get("name", ""),
                "seeds": toInt(t.get("seeders", 0)),
                "leeches": toInt(t.get("leechers", 0)),
                "size": convertBytes(int(t.get("size", 0))),
                "sizeInt": int(t.get("size", 0)),
                "added": int(t.get("added", 0)),
                "uploader": t.get("username", "unknown"),
                "link": f"http://apibay.org/t.php?id={t.get('id', '')}",
                "provider": "tpb"
            })
        except (ValueError, KeyError):
            continue

    if sort_criteria and sort_mode:
        torrents = sort_torrents(torrents, sort_criteria, sort_mode)

    totalPages = max(1, len(torrents) // PAGE_COUNT)
    start = PAGE_COUNT * (page - 1)
    end = PAGE_COUNT * page
    return torrents[start:end], totalPages

async def getTPBTorrentData(link):
    data = {"magnet": "", "files": []}
    if not link or "id=" not in link:
        return data
        
    id = link.split('id=')[-1].split('&')[0]
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://apibay.org/t.php?id={id}") as response:
                resp_json = await response.json()
    except Exception as e:
        raise Exception(f"Failed to fetch torrent data: {str(e)}")

    if not resp_json or resp_json.get("name") == "Torrent does not exsist.":
        return data

    try:
        info_hash = resp_json.get("info_hash", "")
        name = resp_json.get("name", "")
        if info_hash and name:
            data["magnet"] = f"magnet:?xt=urn:btih:{info_hash}&dn={aiohttp.helpers.quote(name)}{getTPBTrackers()}"
    except Exception:
        pass

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://apibay.org/f.php?id={id}") as response:
                files_json = await response.json()
                if isinstance(files_json, list):
                    data["files"] = [
                        f"{file.get('name', [''])[0]} ({convertBytes(toInt(file.get('size', [0])[0]))})"
                        for file in files_json if file
                    ]
    except Exception:
        pass

    return data