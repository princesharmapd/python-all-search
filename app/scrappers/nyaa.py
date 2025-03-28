from bs4 import BeautifulSoup
from datetime import datetime
import aiohttp
from .utils import convertDateToTimestamp

async def searchNyaa(search_key, filter_criteria=None, filter_mode=None, page=1):
    baseUrl = f"https://nyaa.si/?f=0&c=0_0&q={aiohttp.helpers.quote(search_key)}&p={page}"
    if filter_criteria and filter_mode:
        if filter_criteria == "time":
            filter_criteria = "id"
        baseUrl += f"&s={filter_criteria}&o={filter_mode}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(baseUrl, timeout=aiohttp.ClientTimeout(total=3)) as response:
                html = await response.text()
    except Exception as e:
        raise Exception(f"Failed to fetch Nyaa: {str(e)}")

    soup = BeautifulSoup(html, "html.parser")
    torrents = []
    totalPages = 1

    try:
        table = soup.find("table", class_="table")
        if not table:
            return torrents, totalPages
            
        # Get pagination info
        pagination = soup.find("ul", class_="pagination")
        if pagination:
            page_links = [li for li in pagination.find_all("li") if li.text.isdigit()]
            if page_links:
                totalPages = int(page_links[-1].text)

        # Parse torrents
        for row in table.find("tbody").find_all("tr"):
            try:
                cols = row.find_all("td")
                if len(cols) < 7:
                    continue
                    
                # Remove comment link if exists
                title_col = cols[1]
                if title_col.find("a", class_="comments"):
                    title_col.find("a", class_="comments").decompose()
                
                title = title_col.text.strip()
                magnet = cols[2].find_all("a")[1]["href"]
                size = cols[3].text.strip().replace('i', '')
                date = convertDateToTimestamp(cols[4].text.strip())
                seeds = cols[5].text.strip()
                leeches = cols[6].text.strip()
                
                torrents.append({
                    "name": title,
                    "link": magnet,
                    "size": size,
                    "seeds": seeds,
                    "leeches": leeches,
                    "added": date,
                    "uploader": "unknown",
                    "provider": "nyaa"
                })
            except Exception as e:
                print(f"Error parsing torrent row: {e}")
                continue
                
    except Exception as e:
        print(f"Error parsing Nyaa page: {e}")
        
    return torrents, totalPages