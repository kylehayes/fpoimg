from flask import Flask
from flask import abort, send_file, request, render_template, redirect
from PIL import Image, ImageDraw, ImageFont
import os
import time
import datetime
# import boto3
# import logging
# import csv
import io
import textwrap
import requests
# from botocore.exceptions import ClientError
# from flask_s3 import FlaskS3

app = Flask(__name__)

GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID')
app.config['FLASKS3_BUCKET_NAME'] = os.environ.get('FPOIMG_AWS_BUCKET')
app.config['FLASKS3_FILEPATH_HEADERS'] = {
    r'.css$': {
        'Content-Type': 'text/css',
    },
    r'.js$': {
        'Content-Type': 'text/javascript',
    }
}
# s3 = Flask(app)


def track_event(category, action, label=None, value=0, referrer=555):
    data = {
        'v': '1',  # API Version.
        'tid': GA_TRACKING_ID,  # Tracking ID / Property ID.
        # Anonymous Client Identifier. Ideally, this should be a UUID that
        # is associated with particular user, device, or browser instance.
        'cid': referrer,
        't': 'event',  # Event hit type.
        'ec': category,  # Event category.
        'ea': action,  # Event action.
        'el': label,  # Event label.
        'ev': value,  # Event value, must be an integer
    }

    response = requests.post(
        'https://www.google-analytics.com/collect', data=data)

    # If the request fails, this will raise a RequestException. Depending
    # on your application's needs, this may be a non-error and can be caught
    # by the caller.
    # print(data)
    response.raise_for_status()

@app.route("/")
def home():
  return render_template('./home.html')

@app.route('/examples')
def examples():
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
  return send_file(img_io, mimetype='image/png')


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
      new_font_size = int(reduction_ratio * max_point)
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


# def writeAndUploadCSV(data="", fieldnames=['name', 'category']):
#   if False:
#     new_csvfile = io.StringIO()
#     wr = csv.DictWriter(new_csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
#     wr.writeheader()
#     wr.writerow(data)
#     buffer = io.BytesIO(new_csvfile.getvalue().encode())
#     ts = datetime.datetime.now().timestamp()
#     now = datetime.datetime.now()
#     upload_file(
#       buffer,
#       os.environ['FPOIMG_AWS_BUCKET'],
#       "logs/queries/year={year}/month={month}/day={day}/hour={hour}/{ts}.csv".format(year=now.year, month=now.month, day=now.day, hour=now.hour, ts=ts)
#     )


# def upload_file(file, bucket, object_name):
#   access_key_id = os.environ.get('FPOIMG_AWS_ACCESS_KEY_ID', '')
#   access_key = os.environ.get('FPOIMG_AWS_SECRET_ACCESS_KEY', '')
#   if access_key and access_key_id:
#     s3_client = boto3.resource(
#       's3',
#       aws_access_key_id=access_key_id,
#       aws_secret_access_key=access_key,
#     )
#     try:
#       s3_client.Object(bucket, object_name).put(Body=file.getvalue())
#     except ClientError as e:
#       logging.error(e)
#       return False
#     return True


def generate(width, height, caption="", bg_color=(100,100,100), text_color=(200,200,200)):
  size = (width,height)       # size of the image to create
  im = Image.new('RGB', size, bg_color) # create the image
  draw = ImageDraw.Draw(im)   # create a drawing object
  DEFAULT_DIM_SIZE = 50
  DEFAULT_CAPTION_SIZE = 30

  text_line_pad = 0

  dim_text = str(width) + u"\u00D7" + str(height) # \u00D7 is multiplication sign

  text_lines = [(dim_text, "ArialBlack.ttf", DEFAULT_DIM_SIZE)]

  if(caption):
    text_lines += [(caption, "Arial.ttf", DEFAULT_CAPTION_SIZE)]

  text_layouts = layout_text(width, height, 0, text_lines)

  for text_layout in text_layouts:
    text, font, pos = text_layout
    draw.text(pos, text, fill=text_color, font=font)

  del draw # I'm done drawing so I don't need this anymore
  
  ts = time.time()
  timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

  logData = {
    "timestamp": timestamp,
    "width": width,
    "height": height,
    "caption": caption,
    "bg_color": bg_color,
    "text_color": text_color,
    "referrer": request.referrer,
    "user_agent": request.user_agent
  }

  event_data = {
    "width": width,
    "height": height,
    "caption": caption,
    "bg_color": bg_color,
    "text_color": text_color,
    "referrer": request.referrer,
  }

  track_event(
    'Image',
    'generate',
    label=",".join(['%s:%s'% (v,event_data[v]) for v in event_data]),
    referrer=request.referrer
  )

  # writeAndUploadCSV(logData, ["timestamp", "width", "height", "caption", "bg_color", "text_color", "referrer", "user_agent"])

  return serve_pil_image(im)


if __name__ == "__main__":
  port = int(os.environ.get('PORT', 5000))
  if port == 3000:
    app.debug = True
  app.run(host='0.0.0.0', port=port)
