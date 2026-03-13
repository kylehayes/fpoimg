import logging
from flask import Flask
from flask import abort, send_file, request, render_template, redirect
from PIL import Image, ImageDraw, ImageFont
import os
import time
import datetime
import io
import textwrap
import requests
from werkzeug.exceptions import HTTPException
import json
import random
import qrcode

app = Flask(__name__)

# configure logging
logging.basicConfig(level=logging.INFO)
logger = app.logger

# --- Support CTA ---
_CTA_URL = "https://buymeacoffee.com/kylehayes"
_CTA_LABELS = [
    "Support a solo dev",
    "Built by one person — tips welcome",
    "Fuel this free tool",
    "Like it? Buy me a coffee",
    "Keep this free — tip the maker",
]
_CTA_MIN_WIDTH  = int(os.environ.get("SUPPORT_CTA_MIN_WIDTH",  "300"))
_CTA_MIN_HEIGHT = int(os.environ.get("SUPPORT_CTA_MIN_HEIGHT", "250"))
_CTA_FREQUENCY  = int(os.environ.get("SUPPORT_CTA_FREQUENCY",  "0"))

def _build_cta_qr() -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(_CTA_URL)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGBA")

_QR_SOURCE: Image.Image = _build_cta_qr()

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    # log the full exception
    logger.exception("unhandled exception: %s", str(e))
    return "Server Error", 500

@app.route("/")
def home():
  logger.info("Home page")
  return render_template('./home2.html')

@app.route('/examples')
def examples():
  logger.info("Examples page")
  return render_template('./examples.html')

@app.route('/<int:square>')
def show_image_square(square):
  return show_image_width_height(square, square)

@app.route('/<int:width>x<int:height>')
def show_image_width_height(width, height):
  caption = request.args.get('text', '')
  return show_image_width_height_caption(width, height, caption)

@app.route('/<int:width>x<int:height>/<caption>')
def show_image_width_height_caption(width, height, caption):
  width = min([max([10,width]), 5000])
  height = min([max([10,height]), 5000])

  bg_color_hex = request.args.get('bg_color', '#C7C7C7')
  text_color_hex = request.args.get('text_color', '#8F8F8F')
  logger.info("Showing image width='%d' height='%d' caption='%s' bg_color='%s' text_color='%s'", width, height, caption, bg_color_hex, text_color_hex)

  try:
    bg_color_rgb = hex_to_rgb(bg_color_hex)
  except ValueError:
    bg_color_rgb = hex_to_rgb("#C7C7C7")

  try:
    text_color_rgb = hex_to_rgb(text_color_hex)
  except ValueError:
    text_color_rgb = hex_to_rgb("#8F8F8F")

  return generate(width, height, caption, bg_color_rgb, text_color_rgb)


def serve_pil_image(pil_img):
  img_io = io.BytesIO()
  pil_img.save(img_io, 'PNG', quality=70)
  img_io.seek(0)
  response = send_file(img_io, mimetype='image/png')
  # Prevent caching so clients always get fresh images
  response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
  response.headers['Pragma'] = 'no-cache'
  return response


def hex_to_rgb(value):
  '''
  Algorithm provided by @Jeremy Cantrell on StackOverflow.com:
  http://stackoverflow.com/questions/214359/converting-hex-color-to-rgb-and-vice-versa
  '''
  if len(value.strip()) != 0:
    if value[0] == '#':
        value = value[1:]

    len_value = len(value)

    if len_value not in [3, 6]:
      raise ValueError('Incorect a value hex {}'.format(value))

    if len_value == 3:
        value = ''.join(i * 2 for i in value)
    return tuple(int(i, 16) for i in textwrap.wrap(value, 2))
  else:
    return None


def layout_text(canvas_width, canvas_height, line_spacing, list_of_texts=[]):
  '''
  Layouts text on a given canvas size by adjusting font size if necessary.

  Parameters:
  canvas_width, canvas_height: Dimensions of the canvas
  line_spacing: Space between lines
  list_of_texts: List of tuples [(text1, ttf1, max_point1), (text2, ttf2, max_point2), ...]

  Returns:
  A list of tuples: [(text, font, (x, y)), ...]
  '''
  if not list_of_texts:
    return []

  target_reduction = 0.8  # reduction factor for oversized text

  # Initialize fonts and calculate dimensions
  fonts, text_sizes, text_heights, text_widths = [], [], [], []

  for text_attr in list_of_texts:
    text, ttf, max_point = text_attr
    font = ImageFont.truetype(ttf, max_point)
    fonts.append(font)

    # Get size using bounding box
    _, _, width, height = font.getbbox(text)
    text_sizes.append((width, height))
    text_heights.append(height)
    text_widths.append(width)

  total_text_height = sum(text_heights) + (len(list_of_texts) - 1) * line_spacing
  max_text_width = max(text_widths)

  # Determine the necessary reduction ratio if text doesn't fit the canvas
  height_reduction_ratio = (
                                     canvas_height * target_reduction) / total_text_height if total_text_height > canvas_height else 1.0
  width_reduction_ratio = (canvas_width * target_reduction) / max_text_width if max_text_width > canvas_width else 1.0

  # Apply the maximum reduction ratio
  reduction_ratio = min(height_reduction_ratio, width_reduction_ratio, 1.0)

  # Recalculate font sizes and text dimensions after reduction
  if reduction_ratio < 1.0:
    fonts, text_sizes, text_heights, text_widths = [], [], [], []

    for text_attr in list_of_texts:
      text, ttf, max_point = text_attr
      # Ensure new_font_size is at least 1
      new_font_size = max(1, int(reduction_ratio * max_point))
      new_font = ImageFont.truetype(ttf, new_font_size)
      fonts.append(new_font)

      _, _, width, height = new_font.getbbox(text)
      text_sizes.append((width, height))
      text_heights.append(height)
      text_widths.append(width)

    total_text_height = sum(text_heights) + (len(list_of_texts) - 1) * line_spacing

  # Center the text vertically in the canvas
  first_top = (canvas_height - total_text_height) / 2

  # Generate layout positions for each text
  layouts = []
  top = first_top
  for idx, (text, ttf, max_point) in enumerate(list_of_texts):
    width, height = text_sizes[idx]
    x_position = (canvas_width - width) / 2
    layouts.append((text, fonts[idx], (x_position, top)))
    top += height + line_spacing

  return layouts

def should_show_cta(width: int, height: int, nosupport: bool) -> bool:
    if nosupport or _CTA_FREQUENCY <= 0:
        return False
    if width < _CTA_MIN_WIDTH or height < _CTA_MIN_HEIGHT:
        return False
    return random.randint(1, _CTA_FREQUENCY) == 1


def render_cta_layout(im: Image.Image, width: int, height: int, dim_text: str, text_color: tuple) -> None:
    """Render CTA image: phrase at top, QR code centered, dim label at bottom."""
    phrase = random.choice(_CTA_LABELS)

    # QR size: 50% of shorter dimension, min 100px
    qr_size = max(100, int(min(width, height) * 0.50))
    qr_img = _QR_SOURCE.resize((qr_size, qr_size), Image.LANCZOS).convert("RGB")

    # Font sizes
    phrase_font_size = max(14, min(27, int(width * 0.06)))
    dim_font_size = max(16, min(36, int(min(width, height) * 0.12)))
    try:
        phrase_font = ImageFont.truetype("Arial.ttf", phrase_font_size)
    except IOError:
        phrase_font = ImageFont.load_default()
    try:
        dim_font = ImageFont.truetype("ArialBlack.ttf", dim_font_size)
    except IOError:
        dim_font = ImageFont.load_default()

    draw = ImageDraw.Draw(im)

    # Measure texts
    pb = draw.textbbox((0, 0), phrase, font=phrase_font)
    phrase_w, phrase_h = pb[2] - pb[0], pb[3] - pb[1]
    db = draw.textbbox((0, 0), dim_text, font=dim_font)
    dim_w, dim_h = db[2] - db[0], db[3] - db[1]

    # Center all three elements as a group
    phrase_qr_gap = 30
    qr_dim_gap = 4
    total_h = phrase_h + phrase_qr_gap + qr_size + qr_dim_gap + dim_h
    start_y = (height - total_h) // 2

    phrase_x = (width - phrase_w) // 2
    phrase_y = start_y

    qr_x = (width - qr_size) // 2
    qr_y = phrase_y + phrase_h + phrase_qr_gap

    dim_x = (width - dim_w) // 2
    dim_y = qr_y + qr_size + qr_dim_gap

    draw.text((phrase_x, phrase_y), phrase, fill=text_color, font=phrase_font)
    draw.text((dim_x, dim_y), dim_text, fill=text_color, font=dim_font)
    del draw

    if qr_x >= 0 and qr_y >= 0:
        im.paste(qr_img, (qr_x, qr_y))


def generate(width, height, caption="", bg_color=(100,100,100), text_color=(200,200,200)):
  size = (width,height)       # size of the image to create
  im = Image.new('RGB', size, bg_color) # create the image

  dim_text = str(width) + u"\u00D7" + str(height) # \u00D7 is multiplication sign

  nosupport = request.args.get('nosupport', '0') == '1'
  if should_show_cta(width, height, nosupport):
    render_cta_layout(im, width, height, dim_text, text_color)
  else:
    draw = ImageDraw.Draw(im)
    text_lines = [(dim_text, "ArialBlack.ttf", 50)]
    if(caption):
      text_lines += [(caption, "Arial.ttf", 30)]
    text_layouts = layout_text(width, height, 0, text_lines)
    for text_layout in text_layouts:
      text, font, pos = text_layout
      draw.text(pos, text, fill=text_color, font=font)
    del draw

  return serve_pil_image(im)


if __name__ == "__main__":
  port = int(os.environ.get('PORT', 3000))
  if port == 3000:
    app.debug = True
  app.run(host='0.0.0.0', port=port)
