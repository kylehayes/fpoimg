"""Flask route definitions — thin layer that parses params and delegates."""
import logging
from flask import Blueprint, request, render_template, send_file

from .utils.colors import parse_color
from .utils.params import clamp_dimension, DEFAULT_BG_COLOR, DEFAULT_TEXT_COLOR
from .generators.image import generate_image
from .generators.formats import image_to_bytes, FORMAT_MIMETYPES
from .generators.gradient import parse_gradient_param, PRESETS
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


@routes_bp.route('/<int:square>')
def show_image_square(square):
    return _generate_response(square, square)


@routes_bp.route('/<int:width>x<int:height>')
def show_image_width_height(width, height):
    return _generate_response(width, height)


@routes_bp.route('/<int:width>x<int:height>/<caption>')
def show_image_width_height_caption(width, height, caption):
    return _generate_response(width, height, caption)


def _generate_response(width, height, caption=None):
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

    logger.info("Showing image width='%d' height='%d' caption='%s' bg_color='%s' text_color='%s' gradient='%s'",
                width, height, caption, bg_color, text_color, request.args.get('gradient', ''))

    im = generate_image(width, height, caption, bg_color, text_color,
                        gradient=gradient, gradient_angle=gradient_angle)

    # Serialize
    fmt = "PNG"
    mimetype = FORMAT_MIMETYPES[fmt]
    img_io = image_to_bytes(im, fmt)

    response = send_file(img_io, mimetype=mimetype)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    if WHATS_NEW:
        response.headers['X-FPOImg-New'] = WHATS_NEW
    return response
