import requests
from loguru import logger

TIMEOUT = 60

scraper_is_installed = False

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/553.37 (KHTML, like Gecko) Chrome/56.0.1264 Safari/537.36"


def check_url(url: str) -> bool:
    if url in ("", "http://", "https://"):
        return False

    if url.startswith("http://"):
        url = url.replace("http://", "https://")

    with logger.contextualize(url=url):
        e = "Unknown error"
        try:
            headers = {"User-Agent": USER_AGENT}
            result = requests.get(url, headers=headers, timeout=TIMEOUT)
            status = result.status_code
        except Exception as e:
            status = -1
            error = str(e)

        if status == 200:
            logger.debug("URL checked successfully", status=status)
        elif status == -1:
            logger.debug("Error checking URL", error=error)
        else:
            logger.debug("Bad status checking URL", status=status)

        return status == 200
