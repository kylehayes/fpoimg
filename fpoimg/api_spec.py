"""Generate the public API contract from registered image views and docstrings."""
from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin
from flask import Blueprint, current_app, jsonify, render_template

from .generators.formats import FORMAT_MIMETYPES, EXTENSION_MAP
from .generators.gradient import PRESETS
from .utils.params import (
    MIN_DIMENSION, MAX_DIMENSION, DEFAULT_BG_COLOR, DEFAULT_TEXT_COLOR,
)

api_bp = Blueprint('api', __name__)


def image_endpoint(view):
    """Mark an image route for OpenAPI inclusion; does not change request handling.

    Put route-specific ``get`` metadata after ``---`` in the view's docstring.
    Shared query parameters, path parameters and responses are added centrally.
    """
    view.is_image_endpoint = True
    return view


class ImagePlugin(FlaskPlugin):
    def path_helper(self, path=None, operations=None, parameters=None, *,
                    view=None, app=None, **kwargs):
        path = super().path_helper(path, operations, parameters,
                                   view=view, app=app, **kwargs)
        rule = self._rule_for_view(view, app=app)
        operation = operations['get']
        operation['operationId'] = view.__name__
        operation['tags'] = ['Images']
        operation['parameters'] = [
            name
            for name in sorted(rule.arguments)
        ] + [
            name
            for name in ('text', 'bg_color', 'text_color', 'gradient',
                         'gradient_angle', 'dims')
        ]
        operation['responses'] = {
            '200': {'$ref': '#/components/responses/' +
                    ('Image' if 'ext' in rule.arguments else 'PNGImage')},
            '404': {'$ref': '#/components/responses/NotFound'},
            '500': {'$ref': '#/components/responses/ServerError'},
        }
        return path


def build_spec(app):
    """Build once per app, without deriving public URLs from request headers."""
    spec = APISpec(
        title='FPOImg Placeholder Image API', version='1.0.0',
        openapi_version='3.0.3', plugins=[ImagePlugin()],
        servers=[{'url': 'https://fpoimg.com', 'description': 'Public service'}],
        security=[],
        info={'description': (
            'Free URL-based placeholder images for wireframes, prototypes, and '
            'CMS layouts. No account or API key is required. GET an image URL '
            'directly or use it as an HTML img src. Responses contain image bytes, '
            'not JSON or a hosted-image URL. PNG is the default; an extension '
            'selects JPEG, WebP, or SVG. These are geometric placeholders with '
            'text and colors, not prompt-generated photographs or illustrations. '
            'Prefer query parameters for captions and colors to avoid ambiguous '
            'path segments. URL-encode query values; encode # as %23 or omit it.'
        )},
        tags=[{'name': 'Images', 'description': 'Generate placeholder images on demand.'}],
        externalDocs={'url': 'https://fpoimg.com/docs',
                      'description': 'API reference and examples'},
    )

    def parameter(name, location, description, schema, example=None):
        data = {'name': name, 'in': location, 'description': description,
                'required': location == 'path', 'schema': schema}
        if example is not None:
            data['example'] = example
        spec.components.parameter(name, location, data)

    for name in ('width', 'height', 'square'):
        parameter(name, 'path', (
            f'{"Both dimensions" if name == "square" else name.capitalize()} in pixels. '
            f'Nonnegative integers are accepted and clamped to {MIN_DIMENSION}–'
            f'{MAX_DIMENSION}; out-of-range values are not rejected. '
            'Negative numbers do not match the route.'
        ), {'type': 'integer', 'minimum': 0}, 300)
    parameter('ext', 'path',
              'Output extension: ' + ', '.join(EXTENSION_MAP) +
              '. Case-insensitive. Unrecognized extensions fall back to PNG.',
              {'type': 'string'}, 'webp')
    parameter('first', 'path',
              'A CSS named color or 3/6-digit hex without # sets the background. '
              'Anything else is a caption. Use ?text=red for a caption that looks '
              'like a color. A path color overrides bg_color; a path caption overrides text.',
              {'type': 'string'}, 'steelblue')
    for name, label in (('bg', 'Background'), ('text_c', 'Text')):
        parameter(name, 'path',
                  f'{label} color: CSS name or 3/6-digit hex. Overrides the '
                  'corresponding query color. Invalid colors use the default.',
                  {'type': 'string'}, 'tomato' if name == 'bg' else 'white')
    parameter('caption', 'path',
              'URL-encoded caption. Overrides the text query parameter. '
              'Supports literal \\n or encoded newline characters. Raster captions wrap; SVG captions do not.',
              {'type': 'string'}, 'Hello World')
    parameter('text', 'query',
              'Caption; supports literal \\n or encoded newline characters. '
              'Raster captions wrap automatically; SVG captions do not. '
              'Ignored when a path caption is present.',
              {'type': 'string', 'default': ''}, 'Blog Cover')
    for name, default in (('bg_color', DEFAULT_BG_COLOR),
                          ('text_color', DEFAULT_TEXT_COLOR)):
        parameter(name, 'query',
                  'CSS named color or 3/6-digit hex, optionally prefixed with # '
                  '(encode # as %23). Invalid values fall back to the default. '
                  'A corresponding path color takes precedence. '
                  + ('A valid gradient replaces the background color.' if name == 'bg_color' else ''),
                  {'type': 'string', 'default': default}, 'tomato' if name == 'bg_color' else 'white')
    parameter('gradient', 'query',
              'Preset name (case-insensitive): ' + ', '.join(PRESETS) +
              '. Alternatively, two CSS names or hex colors separated by a comma. '
              'Invalid or empty values use a solid background.',
              {'type': 'string', 'default': ''}, 'sunset')
    parameter('gradient_angle', 'query',
              'CSS-style degrees: 0=up, 90=right, 180=down, 270=left. '
              'Omit to use the preset angle, or 180 for custom gradients. '
              'Invalid integers use that same default. Ignored without a valid gradient.',
              {'type': 'integer'}, 45)
    parameter('dims', 'query',
              'Show dimension text. Only false (case-insensitive) hides it; '
              'other values show it. Captions still render when dimensions are hidden.',
              {'type': 'boolean', 'default': True}, False)

    for name, mimetypes in (('Image', FORMAT_MIMETYPES.values()),
                            ('PNGImage', ['image/png'])):
        spec.components.response(name, {
            'description': 'Generated image bytes. Embed the request URL directly in an img src.',
            'headers': {
                'Cache-Control': {'description': 'Images are currently served without caching.',
                                  'schema': {'type': 'string'},
                                  'example': 'no-store, no-cache, must-revalidate, max-age=0'},
                'X-FPOImg-New': {'description': 'Optional service announcement; may be absent.',
                                 'schema': {'type': 'string'}},
            },
            'content': {mime: {'schema': {'type': 'string', 'format': 'binary'}}
                        for mime in mimetypes},
        })
    spec.components.response('NotFound', {
        'description': 'The URL does not match a route (for example, negative dimensions).',
        'content': {'application/json': {'schema': {
            'type': 'object', 'required': ['code', 'name', 'description'],
            'properties': {'code': {'type': 'integer'}, 'name': {'type': 'string'},
                           'description': {'type': 'string'}},
        }, 'example': {'code': 404, 'name': 'Not Found',
                       'description': 'The requested URL was not found on the server.'}}},
    })
    spec.components.response('ServerError', {
        'description': 'Image generation failed.',
        'content': {'text/html': {'schema': {'type': 'string'}, 'example': 'Server Error'}},
    })
    for view in app.view_functions.values():
        if getattr(view, 'is_image_endpoint', False):
            spec.path(view=view, app=app)
    return spec.to_dict()


@api_bp.get('/openapi.json')
def openapi():
    """Serve the generated contract used by tools and the HTML reference."""
    return jsonify(current_app.extensions['fpoimg_spec'])


@api_bp.get('/docs')
def docs():
    """Render the generated contract as HTML without client-side dependencies."""
    spec = current_app.extensions['fpoimg_spec']

    def resolve(value):
        if '$ref' in value:
            _, _, kind, name = value['$ref'].split('/')
            return spec['components'][kind][name]
        return value

    return render_template('docs.html', spec=spec, resolve=resolve)
