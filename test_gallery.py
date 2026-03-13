"""Test gallery route — visual QA tool, not part of production app."""
import random
from flask import Blueprint, request, render_template

test_gallery_bp = Blueprint('test_gallery', __name__)


@test_gallery_bp.route('/test')
def test_gallery():
  count = request.args.get('count', 12, type=int)
  count = min(max(1, count), 200)

  random.seed(42)  # deterministic so refreshes look consistent
  widths = [100, 150, 200, 250, 300, 350, 400, 450, 500, 600, 800, 1024]
  heights = [100, 150, 200, 250, 300, 350, 400, 450, 500, 600, 800, 768]
  bg_colors = ['C7C7C7', 'FF5733', '33FF57', '3357FF', 'FF33A8', 'FFD700',
               '00CED1', '8B00FF', 'FF4500', '2E8B57', '1E90FF', 'DC143C']
  text_colors = ['8F8F8F', 'FFFFFF', '000000', 'FFFF00', '333333', '0000FF']
  captions = ['', 'Hero', 'Banner', 'Thumbnail', 'Avatar', 'Logo',
              'Card Image', 'Profile Pic', 'Header', 'Sidebar', 'Footer', 'Ad Unit',
              'Buy One Get Free', 'Click Here For More', 'Sign Up For Newsletter',
              'Limited Time Only Today']

  images = []
  for i in range(count):
    w = random.choice(widths)
    h = random.choice(heights)
    bg = random.choice(bg_colors)
    tc = random.choice(text_colors)
    caption = random.choice(captions)

    params = []
    params.append(f'bg_color={bg}')
    params.append(f'text_color={tc}')

    if caption:
      path = f'/{w}x{h}/{caption}'
    else:
      path = f'/{w}x{h}'

    url = path + '?' + '&'.join(params)
    images.append({'url': url, 'width': w, 'height': h, 'bg_color': bg,
                   'text_color': tc, 'caption': caption})

  return render_template('./test_gallery.html', images=images, count=count)
