import random
import re
import sys
from dataclasses import dataclass

import click
import ramda as r
import requests
import trafilatura
from bs4 import BeautifulSoup
from devtools import debug
from flask.cli import with_appcontext
from hyperlink import URL
from langid import langid
from lxml.html.clean import Cleaner
from sqlalchemy.orm import Session
from tldextract import tldextract
from urllib3.exceptions import HTTPError

from app.extensions import db
from app.models import Page, Societe

TIMEOUT = 30
MAX_DEPTH = 2
MAX_PAGES_PER_DOMAIN = 50
MAX_TEXT_LENGTH = 50000


def register(cli):
    cli.add_command(crawler)


@click.group()
def crawler():
    """Crawl members websites and collect content."""


@crawler.command()
@click.option("--reset", is_flag=True)
@click.option("--reset-roots", is_flag=True)
@with_appcontext
def seed(reset=False, reset_roots=False):
    print("Seeding crawl session from company websites")
    if reset:
        db.session.query(Page).delete()
        db.session.commit()

    crawler = Crawler(db.session)

    if reset_roots:
        crawler.reset_roots()
        db.session.commit()

    crawler.seed()
    db.session.commit()


@crawler.command("reset-session")
@with_appcontext
def reset_session():
    print("Starting new crawl session")

    pages = db.session.query(Page).all()
    for page in pages:
        page.status = 0
    db.session.commit()


@crawler.command()
@click.option("--domain")
@click.option("--debug", is_flag=True)
@with_appcontext
def crawl(domain="", debug=False):
    print("Crawling...")

    crawler = Crawler(db.session, debug=debug)
    crawler.crawl(
        domain=domain,
    )
    db.session.commit()


@dataclass
class Crawler:
    session: Session
    allowed_domains: set[str] | None = None
    debug: bool = False

    def seed(self):
        urls = self.get_root_urls()
        for url in urls:
            if not self.has_url(url):
                self.add_url(url, 0)

    def reset_roots(self):
        urls = self.get_root_urls()
        for url in urls:
            page = self.session.query(Page).filter(Page.url == url).first()
            if page:
                db.session.delete(page)

    def get_root_urls(self) -> list[str]:
        result = []
        societes = self.session.query(Societe).filter(Societe.active == True).all()

        for societe in societes:
            url = societe.site_web.strip()
            if not url:
                continue
            if not url.startswith("http"):
                url = "http://" + url

            url_obj = URL.from_text(url)
            normalized_url_obj = url_obj.normalize()
            scheme = normalized_url_obj.scheme
            if scheme not in ("http", "https"):
                continue

            url = normalized_url_obj.to_text()
            result.append(url)

        return result

    def crawl(self, domain=""):
        domain_list = r.map(lambda x: x[0], db.session.query(Page.domain).all())
        self.allowed_domains = set(domain_list)

        for depth in range(0, 2):
            query = (
                self.session.query(Page)
                .filter(Page.status == 0)
                .filter(Page.depth == depth)
            )
            if domain:
                query = query.filter(Page.domain == domain)
            pages_to_crawl = query.all()
            if not pages_to_crawl:
                continue

            print(f".. {len(pages_to_crawl)} pages to crawl")

            random.shuffle(pages_to_crawl)
            for page in pages_to_crawl:
                self.crawl_page(page)
                sys.stdout.flush()

    def has_url(self, url: str):
        if not self.session:
            return False

        page = self.session.query(Page).filter(Page.url == url).first()
        return bool(page)

    def add_url(self, url: str, depth: int):
        if self.has_url(url):
            return

        domain = self.get_domain(URL.from_text(url))
        if self.allowed_domains and domain not in self.allowed_domains:
            return

        print(f"... Adding url to crawl: {url}")
        page = Page(url=url, domain=domain, depth=depth)
        if not self.session:
            return
        self.session.add(page)
        self.session.commit()

    def crawl_page(self, page: Page):
        url = page.url
        print(f"\ncrawling: {url}")
        headers = {
            "Accept-Language": "fr, en",
        }

        try:
            response = requests.head(
                url, allow_redirects=True, headers=headers, timeout=TIMEOUT
            )
        except (HTTPError, OSError) as e:
            debug("Error:", e)
            page.status = -1
            return

        if self.debug:
            debug(response.status_code, response.headers)

        page.status = response.status_code
        page.content_type = response.headers.get("content-type", "")
        if page.status not in (200, 204) or not page.content_type.startswith(
            "text/html"
        ):
            page.html = ""
            page.text = ""
            return

        try:
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
        except:
            page.status = -1
            return

        page.status = response.status_code
        page.content_type = response.headers.get("content-type", "")
        html = response.text.strip()

        if (
            page.status not in (200, 204)
            or not page.content_type.startswith("text/html")
            or not html
        ):
            page.html = ""
            page.text = ""
            return

        cleaner = Cleaner(style=True)
        try:
            html = cleaner.clean_html(html)
        except ValueError:
            pass
        page.html = html

        self.extract_text(page)

        if page.depth < MAX_DEPTH:
            self.extract_links(page)

        print(78 * "=")

    def extract_text(self, page: Page) -> None:
        html = page.html
        if html:
            text = BeautifulSoup(html, features="lxml").text
            text = re.sub("[ \t]+", " ", text)
            text = re.sub("\n+", "\n", text)
            page.lang = langid.classify(text)[0]

            content = trafilatura.extract(html) or ""
            text = content
        else:
            text = ""
        if len(text) > MAX_TEXT_LENGTH:
            text = text[0:MAX_TEXT_LENGTH]
        page.text = text

    def extract_links(self, page: Page) -> None:
        soup = BeautifulSoup(page.html, features="lxml")
        links = set(
            r.map(
                lambda x: x.get("href"),
                soup.findAll("a", attrs={"href": True}),
            )
        )
        if self.debug:
            debug(links)
        self.add_links(page, links)

    def add_links(self, page: Page, links: set[str]) -> None:
        page_url_obj = URL.from_text(page.url)
        for link in links:
            try:
                link_obj = page_url_obj.click(link).normalize()
            except (ValueError, NotImplementedError):
                print(f"Not adding {link}")
                continue

            link_obj = self.clean_url(link_obj)
            if self.is_bad_url(link_obj):
                print(f"Not adding {link_obj}")
                continue
            domain = self.get_domain(link_obj)

            if domain != page.domain:
                print(f"Not adding {link_obj}")
                continue

            self.add_url(link_obj.to_text(), depth=page.depth + 1)

    @staticmethod
    def clean_url(url_obj: URL) -> URL:
        u = url_obj
        new_url_obj = URL(u.scheme, u.host, u.path, u.query)
        return new_url_obj

    @staticmethod
    def get_domain(url_obj: URL) -> str:
        host = url_obj.host
        domain = tldextract.extract(host).registered_domain
        return domain

    @staticmethod
    def is_bad_url(url_obj: URL) -> bool:
        last_segment = url_obj.path[-1]
        if re.match(r".*.(pdf|js|css|gif|jpeg|png|mpeg|mov|zip)$", last_segment):
            return True
        return False
