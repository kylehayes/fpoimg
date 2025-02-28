# FPOimg

A simple, flexible placeholder image generator service for developers and designers.

## Overview

FPOimg (For Placement Only Image) is a lightweight Flask-based web service that dynamically generates placeholder images on demand. Perfect for mockups, wireframes, and prototypes where you need consistently sized visual elements.

## Features

- **Simple URL-based API**: Generate images using straightforward URL patterns
- **Custom Dimensions**: Specify exact width and height for your placeholders
- **Text Overlays**: Add dimension information and custom captions
- **Color Customization**: Control both background and text colors
- **Responsive Design**: Works with images from 10px to 5000px in size
- **Lightweight**: No external analytics dependencies, just simple logging

## Usage

### Basic Examples

```
/300            → 300×300 square image
/800x600        → 800×600 rectangular image
/500x200/Hello  → 500×200 image with "Hello" caption
```

### URL Parameters

Customize your images with query parameters:

```
/500x300?bg_color=#FF5733&text_color=#FFFFFF  → Orange background with white text
/400x200?text=Custom+Caption                  → Image with custom caption text
```

### Parameter Reference

| Parameter    | Description                      | Default  |
|--------------|----------------------------------|----------|
| `bg_color`   | Background color (hex)           | #C7C7C7  |
| `text_color` | Text color (hex)                 | #8F8F8F  |
| `text`       | Caption text (alternative method)| None     |

## Self-Hosting

### Requirements

- Python 3.12
- Flask
- Pillow (PIL Fork)
- Required fonts: Arial.ttf, ArialBlack.ttf

### Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/fpoimg.git
   cd fpoimg
   ```

2. Install dependencies
   ```
   pip install -r requirements.txt
   ```

3. Configure environment variables (optional)
   ```
   export PORT=8080  # Optional: Set custom port (defaults to 3000)
   ```

4. Run the server
   ```
   python main.py
   ```

### Deployment

FPOimg is designed to work with Google App Engine, but can be deployed to any platform that supports Python web applications.

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.