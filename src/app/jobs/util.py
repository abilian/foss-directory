import stat
from datetime import datetime, timedelta
from pathlib import Path

import dateutil.parser
import requests
import rich


def fetch_file_if_newer(url, name=""):
    if not name:
        name = url.split("/")[-1]
    filename = f"{name}"

    need_refresh = refresh_needed(url, filename)

    if not need_refresh:
        rich.print(f"[green]No need to refresh file {name}[/green]")
        return

    rich.print(f"[yellow]Fetching newer version: {name}[/yellow]")

    fd = open(filename, "wb")
    r = requests.get(url, stream=True)

    for chunk in r.iter_content(chunk_size=512 * 1024):
        if chunk:  # filter out keep-alive new chunks
            fd.write(chunk)

    fd.close()


def refresh_needed(url, filename):
    path = Path(filename)
    if not path.exists():
        return True

    last_modified_dst = datetime.utcfromtimestamp(path.stat()[stat.ST_CTIME])

    r = requests.head(url)

    if "Last-Modified" not in r.headers:
        return datetime.utcnow() > last_modified_dst + timedelta(days=1)

    last_modified_src_aware = dateutil.parser.parse(r.headers["Last-Modified"])
    last_modified_src = last_modified_src_aware.replace(tzinfo=None)

    return last_modified_src > last_modified_dst + timedelta(days=1)


def count_lines(fd):
    total = 0
    while True:
        chunk = fd.read(1024 * 1024)
        if not chunk:
            break
        total += chunk.count(b"\n")
    return total
