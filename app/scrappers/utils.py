import aiohttp
from datetime import datetime, date
import cloudscraper
from bs4 import BeautifulSoup

scrapper = cloudscraper.create_scraper()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36 Edg/83.0.478.45",
    "Accept-Encoding": "*"
}

async def getSource(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
                response.raise_for_status()
                return await response.text()
    except Exception as e:
        raise Exception(f"Failed to fetch URL {url}: {str(e)}")

def toInt(value):
    try:
        return int(value.replace(',', ''))
    except (ValueError, AttributeError):
        return 0

def convertBytes(num):
    if not isinstance(num, (int, float)):
        try:
            num = float(num)
        except (ValueError, TypeError):
            return "0 bytes"
            
    step_unit = 1000.0
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < step_unit:
            return "%3.1f %s" % (num, x)
        num /= step_unit
    return "%3.1f %s" % (num, 'TB')

def convertDateToTimestamp(value):
    try:
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M")
        return int(dt.timestamp())
    except ValueError:
        return int(datetime.now().timestamp())

def convertStrToDate(Str):
    monthNo = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05",
        "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10",
        "Nov": "11", "Dec": "12"
    }

    try:
        parts = Str.split()
        month = monthNo[parts[0][:-1]]
        day = parts[1][:-2]
        year = "20" + parts[2][1:] if len(parts) > 2 else datetime.now().strftime("%Y")
        torrentDate = f"{year}-{month}-{day} 00:00"
    except Exception:
        torrentDate = date.today().strftime("%Y-%m-%d %H:%M")
    return torrentDate

def getTPBTrackers():
    trackers = [
        "udp://tracker.coppersurfer.tk:6969/announce",
        "udp://9.rarbg.to:2920/announce",
        "udp://tracker.opentrackr.org:1337",
        "udp://tracker.internetwarriors.net:1337/announce",
        "udp://tracker.leechers-paradise.org:6969/announce",
        "udp://tracker.pirateparty.gr:6969/announce",
        "udp://tracker.cyberia.is:6969/announce"
    ]
    return "&tr=" + "&tr=".join(aiohttp.helpers.quote(tracker) for tracker in trackers)