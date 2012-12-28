from flask import Flask
from flask import abort, send_file, request, render_template
from PIL import Image, ImageDraw, ImageFont
from StringIO import StringIO
import os

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

def serve_pil_image(pil_img):
  img_io = StringIO()
  pil_img.save(img_io, 'PNG', quality=70)
  img_io.seek(0)
  return send_file(img_io, mimetype='image/png')


def hex_to_rgb(value):
  '''
  Algorithm provided by @Jeremy Cantrell on StackOverflow.com:
  http://stackoverflow.com/questions/214359/converting-hex-color-to-rgb-and-vice-versa
  '''
  if len(value.strip()) != 0:
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))
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


def generate(width, height, caption="", bg_color=(100,100,100), text_color=(200,200,200)):
  size = (width,height)       # size of the image to create
  im = Image.new('RGB', size, bg_color) # create the image
  draw = ImageDraw.Draw(im)   # create a drawing object
  text_line_pad = 0

  font = ImageFont.truetype("Arial.ttf", 35) # set the font

  dim_text = str(width) + "x" + str(height)

  text_lines = [(dim_text, "ArialBlack.ttf", 78)]

  if(caption):
    text_lines += [(caption, "Arial.ttf", 35,)]

  text_layouts = layout_text(width, height, 0, text_lines)

  for text_layout in text_layouts:
    text, font, pos = text_layout
    draw.text(pos, text, fill=text_color, font=font)

  del draw # I'm done drawing so I don't need this anymore
  
  return serve_pil_image(im)


@app.route('/<int:width>x<int:height>')
def show_image_width_height(width, height):
  caption = request.args.get('text', '')
  bg_color = hex_to_rgb(request.args.get('bg_color', '#666666'))
  text_color = hex_to_rgb(request.args.get('text_color', '#cccccc'))

  return generate(width, height, caption, bg_color, text_color)


@app.route('/<int:width>x<int:height>/<caption>')
def show_image_width_height_caption(width, height, caption):
  bg_color = hex_to_rgb(request.args.get('bg_color', '#666666'))
  text_color = hex_to_rgb(request.args.get('text_color', '#cccccc'))

  return generate(width, height, caption, bg_color, text_color)


@app.route('/test')
def test():
  return render_template('./test.html')


if __name__ == "__main__":
  port = int(os.environ.get('PORT', 5000))
  if port == 5000:
    app.debug = True
  app.run(host='0.0.0.0', port=port)
