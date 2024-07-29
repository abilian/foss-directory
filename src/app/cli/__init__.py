import importlib
import os
import runpy
import shutil
import sys
from pathlib import Path

import click
from flask import Flask, current_app
from flask.cli import with_appcontext

from app import jobs


def register_commands(app: Flask):
    app.cli.add_command(dev)
    app.cli.add_command(script)
    app.cli.add_command(config)
    app.cli.add_command(pages)

    register_jobs(app)


def register_jobs(app: Flask):
    jobs_dir = Path(jobs.__file__).parent
    for fn in jobs_dir.glob("[a-z]*.py"):
        name = fn.name[0:-3]
        module = importlib.import_module(f"app.jobs.{name}")
        if hasattr(module, "register"):
            module.register(app.cli)  # type: ignore


#
# Development commands
#
@click.command()
@click.option("--server", default="flask")
@click.option("--coverage")
@with_appcontext
def dev(server, coverage=False):
    "Run dev servers"
    if server == "flask":
        if coverage:
            flask = shutil.which("flask")
            web_cmd = f"coverage run {flask} run --no-reload"
        else:
            web_cmd = "flask run"
    elif server == "gunicorn":
        web_cmd = "gunicorn -w1 --timeout 300 --bind 0.0.0.0:5000 'wsgi:app'"
    elif server == "uvicorn":
        web_cmd = "uvicorn --host 0.0.0.0 --port 5000 --wsgi 'wsgi:app'"
    else:
        raise click.BadParameter("No such server")

    daemons = [
        ("web", web_cmd),
        ("tailwind", "flask tailwind start"),
    ]
    run_daemons(daemons)


def run_daemons(daemons):
    import honcho.manager

    # root = (Path(current_app.path) / "..").resolve()
    # debug(root)
    # if not (root / ".git").exists():
    #     print(f"root = {root}")
    #     print("project must be installed in development mode")
    #     sys.exit(1)

    manager = honcho.manager.Manager()
    for name, cmd in daemons:
        # manager.add_process(name, cmd, cwd=str(root))
        manager.add_process(name, cmd)

    manager.loop()
    sys.exit(manager.returncode)


@click.command()
@with_appcontext
def config():
    "Show current congifuration"
    config = current_app.config
    print("Current config:")
    print("===============")
    for key in sorted(config):
        print(f"{key}: {config[key]}")
    print()
    print("Current env:")
    print("============")
    for key in sorted(os.environ):
        print(f"{key}: {os.environ[key]}")


@click.command()
@with_appcontext
def pages():
    pagic = current_app.extensions["pagic"]

    pages = [page_class() for page_class in pagic.all_page_classes]
    pages.sort(key=lambda x: x.name)

    for page in pages:
        print(f"{page.name}: {page.endpoint}: {page.path}")


#
# Production
#
@click.command()
@click.argument("path", type=click.Path(exists=True))
@with_appcontext
def script(path):
    """Run given script in the app context."""
    runpy.run_path(path, run_name="__main__")


@click.command()
@click.argument("name", type=str)
@with_appcontext
def job(name):
    """Run given script in the app context."""
    module = importlib.import_module(f"app.jobs.{name}")
    module.run()
