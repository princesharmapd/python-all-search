from bs4 import BeautifulSoup
from .utils import toInt, convertDateToTimestamp, getSource
import aiohttp

async def searchRarbg(search_key, filter_criteria=None, filter_mode=None, page=1, nsfw=False):
    baseUrl = f"https://rargb.to/search/{page}/?search={aiohttp.helpers.quote(search_key)}"
    if not nsfw:
        baseUrl += "&category[]=movies&category[]=tv&category[]=games&category[]=music&category[]=anime&category[]=apps&category[]=documentaries&category[]=other"
    
    if filter_criteria and filter_mode:
        if filter_criteria == "time":
            filter_criteria = "data"
        baseUrl += f"&order={filter_criteria}&by={filter_mode}"
    
    torrents = []
    try:
        source = await getSource(baseUrl)
        soup = BeautifulSoup(source, "html.parser")
        
        # Get total pages
        try:
            pager = soup.find("div", id="pager_links")
            if pager:
                pages = [a.text for a in pager.find_all("a") if a.text.isdigit()]
                totalPages = int(pages[-1]) if pages else 1
            else:
                totalPages = 1
        except Exception:
            totalPages = 1

        # Parse torrents
        for tr in soup.select("tr.lista2"):
            try:
                tds = tr.select("td")
                if len(tds) < 8:
                    continue
                    
                name = tds[1].a.text.strip()
                link = f"http://rargb.to{tds[1].a['href']}"
                size = tds[4].text.strip()
                date = convertDateToTimestamp(tds[3].text[:-3])
                seeds = toInt(tds[5].font.text if tds[5].font else tds[5].text)
                leeches = toInt(tds[6].text)
                uploader = tds[7].text.strip()
                
                torrents.append({
                    "name": name,
                    "seeds": seeds,
                    "leeches": leeches,
                    "size": size,
                    "added": date,
                    "uploader": uploader,
                    "link": link,
                    "provider": "rarbg"
                })
            except Exception as e:
                print(f"Error parsing torrent: {e}")
                continue
                
    except Exception as e:
        raise Exception(f"Failed to fetch RARBG: {str(e)}")
    
    return torrents, totalPages

async def getRarbgTorrentData(link):
    data = {"magnet": "", "files": []}
    try:
        source = await getSource(link)
        soup = BeautifulSoup(source, "html.parser")
        
        # Get magnet link
        magnet_link = soup.select_one("table.lista > tbody > tr:first-child > td.lista > a")
        if magnet_link and 'href' in magnet_link.attrs:
            data["magnet"] = magnet_link['href']
        
        # Get files list
        files_div = soup.select_one("table.lista > tbody > tr:nth-child(7) > td.lista > div")
        if files_div:
            data["files"] = [li.text.strip() for li in files_div.select("ul > li")]
            
    except Exception as e:
        raise Exception(f"Failed to fetch torrent data: {str(e)}")
    
    return data