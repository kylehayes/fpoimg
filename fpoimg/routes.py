"""Flask route definitions — thin layer that parses params and delegates."""
import logging
from flask import Blueprint, request, render_template, send_file

from .utils.colors import parse_color, is_color_value, NAMED_COLORS, COLOR_FAMILIES
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


@routes_bp.route('/colors')
def colors():
    """Named color reference page with swatches grouped by family."""
    logger.info("Colors page")
    return render_template('./colors.html',
                           families=COLOR_FAMILIES,
                           named_colors=NAMED_COLORS)


# --- Image routes ---

# Square
@routes_bp.route('/<int:square>')
def show_image_square(square):
    return _generate_response(square, square)


@routes_bp.route('/<int:square>.<ext>')
def show_image_square_ext(square, ext):
    return _generate_response(square, square, fmt=_resolve_format(ext))


# Square with one path segment: color or caption
@routes_bp.route('/<int:square>/<first>')
def show_image_square_first(square, first):
    if is_color_value(first):
        return _generate_response(square, square, bg_color_override=first)
    return _generate_response(square, square, caption=first)


# Square with two path segments: bg + text color
@routes_bp.route('/<int:square>/<bg>/<text_c>')
def show_image_square_colors(square, bg, text_c):
    return _generate_response(square, square, bg_color_override=bg,
                              text_color_override=text_c)


# Width x Height
@routes_bp.route('/<int:width>x<int:height>')
def show_image_width_height(width, height):
    return _generate_response(width, height)


@routes_bp.route('/<int:width>x<int:height>.<ext>')
def show_image_width_height_ext(width, height, ext):
    return _generate_response(width, height, fmt=_resolve_format(ext))


# Width x Height with one path segment: color or caption
@routes_bp.route('/<int:width>x<int:height>/<first>')
def show_image_width_height_first(width, height, first):
    if is_color_value(first):
        return _generate_response(width, height, bg_color_override=first)
    return _generate_response(width, height, caption=first)


@routes_bp.route('/<int:width>x<int:height>.<ext>/<caption>')
def show_image_width_height_ext_caption(width, height, ext, caption):
    return _generate_response(width, height, caption, fmt=_resolve_format(ext))


# Width x Height with two path segments: bg + text color
@routes_bp.route('/<int:width>x<int:height>/<bg>/<text_c>')
def show_image_width_height_colors(width, height, bg, text_c):
    return _generate_response(width, height, bg_color_override=bg,
                              text_color_override=text_c)


def _resolve_format(ext):
    """Resolve a file extension to a format name, defaulting to PNG."""
    return EXTENSION_MAP.get(ext.lower(), "PNG")


def _generate_response(width, height, caption=None, fmt="PNG",
                       bg_color_override=None, text_color_override=None):
    """Parse request params, generate image, and return HTTP response."""
    width = clamp_dimension(width)
    height = clamp_dimension(height)

    if caption is None:
        caption = request.args.get('text', '')

    # Colors: URL path overrides take priority, then query params, then defaults
    if bg_color_override:
        bg_color = parse_color(bg_color_override, DEFAULT_BG_COLOR)
    else:
        bg_color = parse_color(request.args.get('bg_color', DEFAULT_BG_COLOR),
                               DEFAULT_BG_COLOR)

    if text_color_override:
        text_color = parse_color(text_color_override, DEFAULT_TEXT_COLOR)
    else:
        text_color = parse_color(request.args.get('text_color', DEFAULT_TEXT_COLOR),
                                 DEFAULT_TEXT_COLOR)

    # Dims toggle (show dimension text by default)
    show_dims = request.args.get('dims', 'true').lower() != 'false'

    # Gradient support
    gradient = parse_gradient_param(request.args.get('gradient', ''))
    gradient_angle = request.args.get('gradient_angle', None, type=int)

    logger.info("Showing image width='%d' height='%d' caption='%s' fmt='%s' "
                "bg_color='%s' text_color='%s' gradient='%s'",
                width, height, caption, fmt, bg_color, text_color,
                request.args.get('gradient', ''))

    # SVG is a completely different path
    if fmt == "SVG":
        img_io = generate_svg(width, height, caption, bg_color, text_color,
                              gradient=gradient, gradient_angle=gradient_angle,
                              show_dims=show_dims)
        mimetype = FORMAT_MIMETYPES["SVG"]
    else:
        im = generate_image(width, height, caption, bg_color, text_color,
                            gradient=gradient, gradient_angle=gradient_angle,
                            show_dims=show_dims)
        mimetype = FORMAT_MIMETYPES.get(fmt, FORMAT_MIMETYPES["PNG"])
        img_io = image_to_bytes(im, fmt)

    response = send_file(img_io, mimetype=mimetype)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    if WHATS_NEW:
        response.headers['X-FPOImg-New'] = WHATS_NEW
    return response
