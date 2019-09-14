from flask import Flask
from flask import abort, send_file, request, render_template, redirect
from PIL import Image, ImageDraw, ImageFont
import os
import datetime
import boto3
import logging
import csv
import io
import textwrap
from botocore.exceptions import ClientError

app = Flask(__name__)

@app.route("/")
def home():
  return render_template('./home.html')


@app.route('/generator')
def generator():
  return render_template('./generator.html')

@app.route('/configurator')
def configurator():
  return redirect('/generator', 301)

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
  width = min([width, 5000])
  height = min([height, 5000])
  bg_color_hex = request.args.get('bg_color', '#C7C7C7')
  text_color = hex_to_rgb(request.args.get('text_color', '#8F8F8F'))
  text_color_hex = request.args.get('text_color', '#8F8F8F')
  return generate(width, height, caption, hex_to_rgb(bg_color_hex), hex_to_rgb(text_color_hex))


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
  This method is most likely _not_ optimized. I certainly welcome any refactoring that
  will either make it faster or do it better

  given canvas_width, canvas_height, line_spacing, [(text1, ttf1, max_point1), (text2, ttf2, max_point2), ...]
  return [(font1, pos1), (font2, pos2), ...]
  '''
  target_reduction = 0.8 # the amount to reduce by if the text is too large


  if len(list_of_texts):
    ratios = []
    text_heights = []
    text_widths = []
    fonts = []
    text_sizes = []
    for text_attr in list_of_texts:
      text, ttf, max_point = text_attr
      font = ImageFont.truetype(ttf, max_point)
      fonts += [font]
      text_size = font.getsize(text)
      width, height = text_size
      text_sizes += [tuple(text_size)]
      
      #pdb.set_trace()

      text_heights += [float(height)]
      text_widths += [float(width)]

    total_text_height = sum(text_heights)
    max_text_width = max(text_widths)

    ratios = [h/total_text_height for h in text_heights]


    # the height needs to be reduced because it won't fit in the current canvas
    if (total_text_height * ((1-target_reduction)+1) ) > canvas_height:
      target_height = canvas_height * target_reduction
      total_reduction = target_height / total_text_height # this is what the point size needs to be reduced by
      text_heights = []
      fonts = []
      text_sizes = []
      
      for idx, text_attr in enumerate(list_of_texts):
        text, ttf, max_point = text_attr
        new_font = ImageFont.truetype(ttf, int( total_reduction * max_point) )
        fonts += [new_font]
        text_size = new_font.getsize(text)
        width, height = text_size
        text_sizes += [text_size]
        text_heights += [height]

    # the width needs to be reduced because it won't fit in the current canvas
    if (max_text_width * ((1-target_reduction)+1) ) > canvas_width:
      target_width = canvas_width * target_reduction
      total_reduction = target_width / max_text_width # this is what the point size needs to be reduced by
      text_heights = []
      fonts = []
      text_sizes = []
      
      for idx, text_attr in enumerate(list_of_texts):
        text, ttf, max_point = text_attr
        new_font = ImageFont.truetype(ttf, int( total_reduction * max_point) )
        fonts += [new_font]
        text_size = new_font.getsize(text)
        width, height = text_size
        text_sizes += [text_size]
        text_heights += [height]


    total_text_height = sum(text_heights)

    first_top = (canvas_height - total_text_height)/2

    layouts = []
    top = 0
    for idx, text_attr in enumerate(list_of_texts):
      if idx == 0:
        top = first_top
      layouts += [(text_attr[0], fonts[idx], ( ( (canvas_width/2) - (text_sizes[idx][0]/2) ), top) )]
      top += text_heights[idx]

    return layouts

  else:
    return []

def writeAndUploadCSV(data="", fieldnames=['name', 'category']):
  new_csvfile = io.StringIO()
  wr = csv.DictWriter(new_csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
  wr.writeheader()
  wr.writerow(data)
  buffer = io.BytesIO(new_csvfile.getvalue().encode())
  today = datetime.date.today()
  year = today.year
  month = today.month
  day = today.day
  ts = datetime.datetime.now().timestamp()
  upload_file(buffer, os.environ['FPOIMG_AWS_BUCKET_LOGS'], f"queries/year={year}/month={month}/day={day}/{ts}.csv")


def upload_file(file, bucket, object_name):
  s3_client = boto3.resource(
    's3',
    aws_access_key_id=os.environ['FPOIMG_AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['FPOIMG_AWS_SECRET_ACCESS_KEY'],
  )
  try:
    s3_client.Object(bucket, object_name).put(Body=file.getvalue())
  except ClientError as e:
    logging.error(e)
    return False
  return True


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
  
  logData = {
    "width": width,
    "height": height,
    "caption": caption,
    "bg_color": bg_color,
    "text_color": text_color,
    "referrer": request.referrer,
    "user_agent": request.user_agent
  }
  writeAndUploadCSV(logData, ["width", "height", "caption", "bg_color", "text_color", "referrer", "user_agent"])

  return serve_pil_image(im)


if __name__ == "__main__":
  port = int(os.environ.get('PORT', 5000))
  if port == 5000:
    app.debug = True
  app.run(host='0.0.0.0', port=port)
