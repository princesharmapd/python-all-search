from bs4 import BeautifulSoup
from .utils import toInt, convertStrToDate, convertDateToTimestamp, getSource
import aiohttp
import re

async def search1337x(search_key, filter_criteria=None, filter_mode=None, page=1, nsfw=False):
    baseUrl = "https://1337xx.to"
    if filter_criteria and filter_mode:
        baseUrl += f"/sort-search/{search_key.replace(' ', '%20')}/{filter_criteria}/{filter_mode}/{page}/"
    else:
        baseUrl += f"/search/{search_key.replace(' ', '%20')}/{page}/"
    
    torrents = []
    try:
        source = await getSource(baseUrl)
    except Exception as e:
        raise Exception(f"Failed to fetch 1337x: {str(e)}")

    soup = BeautifulSoup(source, "html.parser")

    try:
        pagination = soup.find("div", class_="pagination")
        if pagination:
            pages = [li.text for li in pagination.find_all("li") if li.text.isdigit()]
            totalPages = int(pages[-1]) if pages else 1
        else:
            totalPages = 1
    except Exception as e:
        print(f"Error parsing pages: {e}")
        totalPages = 1

    for tr in soup.select("tbody > tr"):
        try:
            is_nsfw = "xxx" in tr.select_one("td.coll-1 > a")["href"].lower()
            if not nsfw and is_nsfw:
                continue
                
            name_a = tr.select("td.coll-1 > a")[1]
            name = name_a.text.strip()
            link = f"http://1337xx.to{name_a['href']}"
            
            seeds = toInt(tr.select_one("td.coll-2").text)
            leeches = toInt(tr.select_one("td.coll-3").text)
            
            size_text = tr.select_one("td.coll-4").text
            size = re.sub(r'(\d+\.?\d*)([KMGT]?B)', r'\1 \2', size_text, flags=re.IGNORECASE)
            
            date_text = tr.select_one("td.coll-date").text
            date = convertDateToTimestamp(convertStrToDate(date_text))
            
            uploader = tr.select_one("td.coll-5 > a").text if tr.select_one("td.coll-5 > a") else "Unknown"
            
            torrents.append({
                "name": name,
                "seeds": seeds,
                "leeches": leeches,
                "size": size,
                "added": date,
                "uploader": uploader,
                "link": link,
                "provider": "1337x"
            })
        except Exception as e:
            print(f"Error parsing torrent: {e}")
            continue

    return torrents, totalPages

async def get1337xTorrentData(link):
    data = {"magnet": "", "torrent_file": "", "files": []}
    try:
        source = await getSource(link)
        soup = BeautifulSoup(source, "html.parser")
        
        # Get magnet link
        magnet_item = soup.select_one('ul.dropdown-menu > li:last-child > a')
        if magnet_item and 'href' in magnet_item.attrs:
            data["magnet"] = magnet_item['href']
        
        # Get torrent file
        torrent_item = soup.select_one('ul.dropdown-menu > li:first-child > a')
        if torrent_item and 'href' in torrent_item.attrs:
            data["torrent_file"] = torrent_item['href']
        
        # Get files list
        files_div = soup.select_one('div.file-content')
        if files_div:
            data["files"] = [li.text.strip() for li in files_div.select('ul > li') if li.text.strip()]
            
    except Exception as e:
        raise Exception(f"Failed to fetch torrent data: {str(e)}")
    
    return data