"""Flask route definitions — thin layer that parses params and delegates."""
import logging
from flask import Blueprint, request, render_template, send_file

from .utils.colors import parse_color
from .utils.params import clamp_dimension, DEFAULT_BG_COLOR, DEFAULT_TEXT_COLOR
from .generators.image import generate_image
from .generators.formats import image_to_bytes, FORMAT_MIMETYPES, EXTENSION_MAP
from .generators.gradient import parse_gradient_param, PRESETS
from .generators.svg import generate_svg
from .whats_new import WHATS_NEW

logger = logging.getLogger(__name__)

routes_bp = Blueprint('routes', __name__)


@routes_bp.route("/")
def home():
    logger.info("Home page")
    return render_template('./home2.html')


@routes_bp.route('/examples')
def examples():
    logger.info("Examples page")
    return render_template('./examples.html')


@routes_bp.route('/gradients')
def gradients():
    """Gradient picker page with premade presets and custom builder."""
    logger.info("Gradients page")
    return render_template('./gradients.html', presets=PRESETS)


# --- Image routes ---
# Square
@routes_bp.route('/<int:square>')
def show_image_square(square):
    return _generate_response(square, square)


@routes_bp.route('/<int:square>.<ext>')
def show_image_square_ext(square, ext):
    return _generate_response(square, square, fmt=_resolve_format(ext))


# Width x Height
@routes_bp.route('/<int:width>x<int:height>')
def show_image_width_height(width, height):
    return _generate_response(width, height)


@routes_bp.route('/<int:width>x<int:height>.<ext>')
def show_image_width_height_ext(width, height, ext):
    return _generate_response(width, height, fmt=_resolve_format(ext))


# Width x Height with caption
@routes_bp.route('/<int:width>x<int:height>/<caption>')
def show_image_width_height_caption(width, height, caption):
    return _generate_response(width, height, caption)


@routes_bp.route('/<int:width>x<int:height>.<ext>/<caption>')
def show_image_width_height_ext_caption(width, height, ext, caption):
    return _generate_response(width, height, caption, fmt=_resolve_format(ext))


def _resolve_format(ext):
    """Resolve a file extension to a format name, defaulting to PNG."""
    return EXTENSION_MAP.get(ext.lower(), "PNG")


def _generate_response(width, height, caption=None, fmt="PNG"):
    """Parse request params, generate image, and return HTTP response."""
    width = clamp_dimension(width)
    height = clamp_dimension(height)

    if caption is None:
        caption = request.args.get('text', '')

    bg_color = parse_color(request.args.get('bg_color', DEFAULT_BG_COLOR), DEFAULT_BG_COLOR)
    text_color = parse_color(request.args.get('text_color', DEFAULT_TEXT_COLOR), DEFAULT_TEXT_COLOR)

    # Gradient support
    gradient = parse_gradient_param(request.args.get('gradient', ''))
    gradient_angle = request.args.get('gradient_angle', None, type=int)

    logger.info("Showing image width='%d' height='%d' caption='%s' fmt='%s' gradient='%s'",
                width, height, caption, fmt, request.args.get('gradient', ''))

    # SVG is a completely different path
    if fmt == "SVG":
        img_io = generate_svg(width, height, caption, bg_color, text_color,
                              gradient=gradient, gradient_angle=gradient_angle)
        mimetype = FORMAT_MIMETYPES["SVG"]
    else:
        im = generate_image(width, height, caption, bg_color, text_color,
                            gradient=gradient, gradient_angle=gradient_angle)
        mimetype = FORMAT_MIMETYPES.get(fmt, FORMAT_MIMETYPES["PNG"])
        img_io = image_to_bytes(im, fmt)

    response = send_file(img_io, mimetype=mimetype)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    if WHATS_NEW:
        response.headers['X-FPOImg-New'] = WHATS_NEW
    return response
