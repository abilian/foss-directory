import click
import svcs
from flask.cli import with_appcontext
from loguru import logger

from app.extensions import db
from app.models import Societe, Solution
from app.services.screenshots import ScreenshotService
from app.services.web import check_url

TIMEOUT = 60


def register(cli):
    cli.add_command(take_screenshots)


@click.command("take-screenshots")
@click.option("--overwrite", "-o", is_flag=True)
@with_appcontext
def take_screenshots(overwrite=False):
    """Take screenshots"""

    print("\n" + 78 * "-" + "\n")
    take_screenshots_societes(overwrite)

    print("\n" + 78 * "-" + "\n")
    take_screenshots_solutions(overwrite)


def take_screenshots_societes(overwrite):
    societes: list[Societe] = db.session.query(Societe).all()
    for societe in societes:
        if societe.screenshot_id and not overwrite:
            continue

        url = societe.site_web
        if not url:
            continue

        if not url.startswith("http"):
            url = "https://" + url
            societe.site_web = url

        if url.strip() != url:
            url = url.strip()
            societe.site_web = url

        if not url.startswith("http"):
            url = "https://" + url
            societe.site_web = url

        if not check_site_web(societe):
            continue

        logger.debug(f"Taking screenshot for: {societe.nom} {url}")
        screenshotter = svcs.flask.container.get(ScreenshotService)
        session = screenshotter.start_session(url)
        if session.object_id:
            societe.screenshot_id = session.object_id
            db.session.commit()


def take_screenshots_solutions(overwrite):
    solutions: list[Solution] = db.session.query(Solution).all()
    for solution in solutions:
        if solution.screenshot_id and not overwrite:
            continue

        url = solution.home_url
        if not url.startswith("http"):
            url = "http://" + url
            solution.home_url = url

        if not check_url(url):
            continue

        logger.debug(f"Taking screenshot for: {solution.name} {url}")
        screenshotter = svcs.flask.container.get(ScreenshotService)
        session = screenshotter.start_session(url)
        if session.object_id:
            solution.screenshot_id = session.object_id
            db.session.commit()


def check_site_web(societe: Societe) -> bool:
    url = societe.site_web
    status = check_url(url)
    if not status:
        print(f"### {societe.nom}: {url} -> {status}")
        societe.bad_url = True
        return False

    return True


# def take_screenshot_old(url):
#     screenshot_path = Path("tmp/screenshot.png")
#     if screenshot_path.exists():
#         screenshot_path.unlink()
#
#     if sys.platform == "darwin":
#         timeout = "gtimeout"
#     else:
#         timeout = "timeout"
#     args = [
#         timeout,
#         str(TIMEOUT),
#         "yarn",
#         "run",
#         "pageres",
#         "--filename=tmp/screenshot",
#         "-c",
#         url,
#         "1024x768",
#     ]
#     status = subprocess.call(args)
#     print("...", status)
#     print()
#     if status != 0:
#         return None
#
#     os.system("ls -l tmp")
#     if not screenshot_path.exists():
#         return None
#
#     if screenshot_path.stat().st_size < 10000:
#         print("not saving")
#         return None
#
#     return screenshot_path.read_bytes()
