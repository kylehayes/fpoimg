"""Verify the discovery surface is crawlable, consistent, and host-independent."""
import json
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree

import pytest

from fpoimg.discovery import PAGES, PUBLIC_ORIGIN


class MetadataParser(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.titles = []
        self.metas = {}
        self.links = {}
        self.in_title = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'title':
            self.in_title = True
        elif tag == 'meta':
            self.metas[attrs.get('name', attrs.get('property'))] = attrs.get('content')
        elif tag == 'link':
            self.links[attrs.get('rel')] = attrs.get('href')

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, text):
        if self.in_title:
            self.titles.append(text)


def test_sitemap_only_lists_working_html_pages(client):
    response = client.get('/sitemap.xml', base_url='https://untrusted.example')
    assert response.status_code == 200
    assert response.mimetype == 'application/xml'
    root = ElementTree.fromstring(response.data)
    urls = [loc.text for loc in root.findall('{*}url/{*}loc')]
    assert len(urls) == len(set(urls)) == len(PAGES)
    assert set(urls) == {PUBLIC_ORIGIN + p['path'] for p in PAGES.values()}
    for url in urls:
        page = client.get(urlsplit(url).path)
        assert page.status_code == 200
        assert page.mimetype == 'text/html'


def test_robots_allows_search_and_discovery_without_gallery(client):
    response = client.get('/robots.txt')
    assert response.status_code == 200
    assert response.mimetype == 'text/plain'
    robots = RobotFileParser()
    robots.parse(response.get_data(as_text=True).splitlines())
    assert robots.site_maps() == [PUBLIC_ORIGIN + '/sitemap.xml']
    for bot in ('Googlebot', 'bingbot', 'OAI-SearchBot', 'PerplexityBot'):
        for path in ('/', '/docs', '/openapi.json', '/llms.txt', '/sitemap.xml',
                     '/static/css/styles2.css', '/400x300?text=Test'):
            assert robots.can_fetch(bot, PUBLIC_ORIGIN + path)
        assert not robots.can_fetch(bot, PUBLIC_ORIGIN + '/test')


@pytest.mark.parametrize('page', PAGES.values(), ids=lambda page: page['path'])
def test_page_metadata_is_unique_and_canonical(client, page):
    response = client.get(page['path'] + '?tracking=test', base_url='https://untrusted.example')
    assert response.status_code == 200
    metadata = MetadataParser(response.get_data(as_text=True))
    assert metadata.titles == [page['title']]
    assert metadata.metas['description'] == page['description']
    assert metadata.links['canonical'] == PUBLIC_ORIGIN + page['path']
    assert metadata.metas['og:url'] == metadata.links['canonical']
    assert metadata.links['describedby'] == '/llms.txt'
    assert metadata.links['alternate'] == '/openapi.json'
    assert 'noindex' not in metadata.metas.get('robots', '')


def test_homepage_structured_data_matches_visible_claims(client):
    html = client.get('/').get_data(as_text=True)
    scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    assert len(scripts) == 1
    data = json.loads(scripts[0])
    assert data['@context'] == 'https://schema.org'
    assert data['@type'] == 'WebApplication'
    assert data['url'] == PUBLIC_ORIGIN + '/'
    assert data['isAccessibleForFree'] is True
    assert data['offers']['price'] == '0'
    assert data['description'] in html
    assert 'PNG, JPEG, WebP, or SVG' in html
    assert 'aggregateRating' not in data


def test_llms_links_and_examples_work(client):
    response = client.get('/llms.txt')
    assert response.status_code == 200
    assert response.mimetype == 'text/plain'
    text = response.get_data(as_text=True)
    assert text.startswith('# FPOImg\n')
    urls = re.findall(r'https://fpoimg\.com/[^\s)]+', text)
    assert PUBLIC_ORIGIN + '/docs' in urls
    assert PUBLIC_ORIGIN + '/openapi.json' in urls
    for url in urls:
        parsed = urlsplit(url)
        target = parsed.path + ('?' + parsed.query if parsed.query else '')
        assert client.get(target).status_code == 200
