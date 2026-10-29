"""Public discovery endpoints and metadata for crawlable content pages."""
from flask import Blueprint, Response, render_template, request

PUBLIC_ORIGIN = 'https://fpoimg.com'
DESCRIPTION = (
    'FPOImg is a free placeholder image API for developers and designers. '
    'Generate images for wireframes, prototypes, and CMS layouts using a URL. '
    'Customize dimensions, colors, gradients, and text without an account or API key.'
)

# This list defines sitemap membership and page-specific metadata together.
PAGES = {
    'routes.home': {
        'path': '/', 'title': 'Free Placeholder Image Generator & API | FPOImg',
        'description': DESCRIPTION,
    },
    'api.docs': {
        'path': '/docs', 'title': 'Placeholder Image API Reference | FPOImg',
        'description': 'Generate placeholder images by URL: API parameters, dimensions, captions, colors, gradients, PNG, JPEG, WebP, and SVG examples.',
    },
    'routes.examples': {
        'path': '/examples', 'title': 'Placeholder Image API Examples | FPOImg',
        'description': 'Explore placeholder image examples with custom sizes, captions, named colors, and hidden dimensions for mockups and prototypes.',
    },
    'routes.gradients': {
        'path': '/gradients', 'title': 'Gradient Placeholder Image Generator | FPOImg',
        'description': 'Create gradient placeholder images using preset backgrounds or custom two-color gradients, angles, sizes, and captions.',
    },
    'routes.colors': {
        'path': '/colors', 'title': 'CSS Named Colors for Placeholder Images | FPOImg',
        'description': 'Browse CSS named colors and use them in FPOImg image URLs for backgrounds, text, and custom gradients.',
    },
}

discovery_bp = Blueprint('discovery', __name__)


@discovery_bp.app_context_processor
def page_metadata():
    page = PAGES.get(request.endpoint)
    if page is None:
        return {}
    metadata = {**page, 'canonical': PUBLIC_ORIGIN + page['path']}
    if request.endpoint == 'routes.home':
        metadata['structured_data'] = {
            '@context': 'https://schema.org', '@type': 'WebApplication',
            '@id': PUBLIC_ORIGIN + '/#application', 'name': 'FPOImg',
            'url': PUBLIC_ORIGIN + '/', 'description': DESCRIPTION,
            'applicationCategory': 'DeveloperApplication',
            'operatingSystem': 'Any', 'isAccessibleForFree': True,
            'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
            'featureList': [
                'URL-based placeholder image generation',
                'Custom dimensions, colors, captions, and gradients',
                'PNG, JPEG, WebP, and SVG output',
                'No account or API key required',
            ],
        }
    return {'page_metadata': metadata}


@discovery_bp.get('/robots.txt')
def robots():
    # The wildcard allows search crawlers, including OAI-SearchBot. Do not add
    # bot-specific groups unless they carry the same gallery exclusion.
    return Response(
        'User-agent: *\nDisallow: /test\nAllow: /\n\n'
        f'Sitemap: {PUBLIC_ORIGIN}/sitemap.xml\n',
        mimetype='text/plain',
    )


@discovery_bp.get('/sitemap.xml')
def sitemap():
    # Only stable HTML content pages; omit generated image permutations.
    return Response(render_template('discovery/sitemap.xml', pages=PAGES.values(),
                                    origin=PUBLIC_ORIGIN), mimetype='application/xml')


@discovery_bp.get('/llms.txt')
def llms():
    return Response(render_template('discovery/llms.txt', description=DESCRIPTION,
                                    origin=PUBLIC_ORIGIN), mimetype='text/plain')
