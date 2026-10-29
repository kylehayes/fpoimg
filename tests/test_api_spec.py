"""Contract validity, route coverage, executable examples and generated HTML."""
import io
from html.parser import HTMLParser

import pytest
from apispec_webframeworks.flask import FlaskPlugin
from openapi_spec_validator import validate
from PIL import Image

from fpoimg.app import create_app
from fpoimg.generators.formats import EXTENSION_MAP, FORMAT_MIMETYPES


def resolve(spec, reference):
    if '$ref' not in reference:
        return reference
    _, _, kind, name = reference['$ref'].split('/')
    return spec['components'][kind][name]


def test_spec_is_valid_and_public(client):
    response = client.get('/openapi.json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    spec = response.get_json()
    validate(spec)
    assert spec['security'] == []
    assert spec['servers'] == [{'url': 'https://fpoimg.com',
                                'description': 'Public service'}]


def test_spec_covers_every_image_route(app):
    spec = app.extensions['fpoimg_spec']
    rules = [rule for rule in app.url_map.iter_rules()
             if rule.endpoint.startswith('routes.show_image_')]
    assert set(spec['paths']) == {
        FlaskPlugin.flaskpath2openapi(rule.rule) for rule in rules
    }
    operation_ids = []
    for rule in rules:
        operation = spec['paths'][FlaskPlugin.flaskpath2openapi(rule.rule)]['get']
        parameters = [resolve(spec, p) for p in operation['parameters']]
        assert {p['name'] for p in parameters if p['in'] == 'path'} == rule.arguments
        assert all(p['required'] for p in parameters if p['in'] == 'path')
        operation_ids.append(operation['operationId'])
    assert len(operation_ids) == len(set(operation_ids))
    assert not any(p in spec['paths'] for p in ('/test', '/docs', '/openapi.json'))


def test_docstring_changes_reach_both_outputs(monkeypatch):
    from fpoimg.routes import show_image_square
    monkeypatch.setattr(show_image_square, '__doc__',
                        show_image_square.__doc__.replace('Generate a square PNG',
                                                         'Updated square summary'))
    with create_app().test_client() as client:
        assert client.get('/openapi.json').get_json()['paths']['/{square}']['get'][
            'summary'] == 'Updated square summary'
        assert b'Updated square summary' in client.get('/docs').data


@pytest.mark.parametrize('operation_id', [
    'show_image_square', 'show_image_square_ext', 'show_image_square_first',
    'show_image_square_colors', 'show_image_width_height',
    'show_image_width_height_ext', 'show_image_width_height_first',
    'show_image_width_height_ext_caption', 'show_image_width_height_colors',
])
def test_documented_examples_return_declared_images(client, app, operation_id):
    spec = app.extensions['fpoimg_spec']
    operation = next(item['get'] for item in spec['paths'].values()
                     if item['get']['operationId'] == operation_id)
    response = client.get(operation['x-example-url'])
    assert response.status_code == 200
    assert response.mimetype in resolve(spec, operation['responses']['200'])['content']
    if response.mimetype == 'image/svg+xml':
        import xml.etree.ElementTree as ET
        assert ET.fromstring(response.data).tag == '{http://www.w3.org/2000/svg}svg'
    else:
        image = Image.open(io.BytesIO(response.data))
        image.verify()
    assert 'no-store' in response.headers['Cache-Control']


@pytest.mark.parametrize('extension,fmt', EXTENSION_MAP.items())
def test_format_contract_matches_actual_response(client, app, extension, fmt):
    spec = app.extensions['fpoimg_spec']
    operation = spec['paths']['/{width}x{height}.{ext}']['get']
    content = resolve(spec, operation['responses']['200'])['content']
    response = client.get('/40x30.' + extension)
    assert response.status_code == 200
    assert response.mimetype == FORMAT_MIMETYPES[fmt]
    assert response.mimetype in content


def test_documented_fallbacks_and_precedence(client):
    response = client.get('/1x6000.unknown?dims=false&bg_color=invalid')
    image = Image.open(io.BytesIO(response.data))
    assert response.mimetype == 'image/png'
    assert image.size == (10, 5000)
    assert image.getpixel((0, 0)) == (199, 199, 199)
    response = client.get('/40x30/tomato/white?bg_color=blue&dims=false')
    assert Image.open(io.BytesIO(response.data)).getpixel((0, 0)) == (255, 99, 71)
    response = client.get('/40x30.svg/red?text=Ignored&dims=false')
    assert b'>red</text>' in response.data
    assert b'Ignored' not in response.data


class ReferenceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script':
            self.scripts.append(attrs)
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
        if 'id' in attrs:
            self.ids.add(attrs['id'])


def test_docs_are_readable_without_javascript_and_links_resolve(client, app):
    response = client.get('/docs')
    assert response.status_code == 200
    assert response.mimetype == 'text/html'
    parser = ReferenceParser()
    parser.feed(response.get_data(as_text=True))
    assert not parser.scripts
    assert '/openapi.json' in parser.links
    for item in app.extensions['fpoimg_spec']['paths'].values():
        operation = item['get']
        assert operation['operationId'] in parser.ids
        assert operation['x-example-url'] in parser.links
        assert operation['summary'].encode() in response.data
    assert all(link[1:] in parser.ids for link in parser.links if link.startswith('#'))
    assert b'href="/docs"' in client.get('/').data
