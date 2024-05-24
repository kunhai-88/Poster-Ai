import json
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import requests
from io import BytesIO
import os
import time

def hex_to_rgba(hex_color):
    """Convert hex color to RGBA."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 8:
        r, g, b, a = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4, 6))
    elif len(hex_color) == 6:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        a = 255
    else:
        raise ValueError(f"Invalid hex color format: {hex_color}")
    return (r, g, b, a)

def hex_to_rgb(hex_color):
    """Convert hex color to RGB."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 8:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    elif len(hex_color) == 6:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    else:
        raise ValueError(f"Invalid hex color format: {hex_color}")
    return (r, g, b)

# 读取JSON布局文件
layout_file = 'text_final.json'  # 替换为你的文件路径
with open(layout_file, 'r') as file:
    layout_data = json.load(file)

# 获取全局布局信息
global_layout = layout_data['global']['layout']

# 获取背景信息
background_color = global_layout.get('backgroundColor')
background_image_url = global_layout.get('backgroundImage')

# 创建空白图像
width = int(global_layout['width'])
height = int(global_layout['height'])
background_rgba = hex_to_rgba(background_color) if background_color else (255, 255, 255, 255)
image = Image.new('RGBA', (width, height), background_rgba)

# 将背景图片粘贴到图像上（如果有背景图片）
if background_image_url:
    response = requests.get(background_image_url)
    background_img = Image.open(BytesIO(response.content)).resize((width, height), Image.LANCZOS)
    image.paste(background_img, (0, 0))

# 创建绘图对象
draw = ImageDraw.Draw(image)

# 函数：绘制元素
def draw_element(element, parent_position=(0, 0)):
    elem_type = element['type']
    left = int(parent_position[0] + element['left'])
    top = int(parent_position[1] + element['top'])
    width = int(element['width'])
    height = int(element['height'])
    opacity = element.get('opacity', 1)

    if elem_type == 'image':
        url = element['url']
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img = img.resize((width, height), Image.LANCZOS)
        if img.mode == 'RGBA':
            alpha = img.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
            img.putalpha(alpha)
        else:
            img = img.convert('RGBA')
            alpha = Image.new('L', img.size, int(opacity * 255))
            img.putalpha(alpha)
        image.paste(img, (left, top), img)

    elif elem_type == 'text':
        font_size = int(element['fontSize'])
        color_hex = element['color']
        try:
            color = hex_to_rgb(color_hex)
        except ValueError as e:
            print(f"Error: {e}")
            color = (0, 0, 0)  # Default to black if color format is invalid
        font_family = element['fontFamily']
        content = element['content']

        # 检查字体文件是否存在，或者使用默认字体
        try:
            font = ImageFont.truetype(f"fonts/{font_family}.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
            print(f"Warning: Font {font_family} not found. Using default font.")

        draw.text((left, top), content, fill=color, font=font)

    elif elem_type == 'group':
        for child in element['elements']:
            draw_element(child, parent_position=(left, top))

# 遍历布局文件，绘制所有元素
for layout in layout_data['layouts']:
    try:
        bg_image_url = layout.get('background', {}).get('image', {}).get('url')
        print(f"bg_image_url: {bg_image_url}")
        if bg_image_url:  
        # Download the background image
          response = requests.get(bg_image_url)
          bg_image = Image.open(BytesIO(response.content)).convert('RGBA')
        else:
          background_rgba = hex_to_rgba(layout['background']['color'])
          print(f"background_rgba: {background_rgba}")
          bg_image = Image.new('RGBA', (width, height), background_rgba)
        image.paste(bg_image, (0, 0), bg_image)
    except KeyError:
        print("No background image or color specified.")
        pass
    
    for element in layout['elements']:
        draw_element(element)

# 保存生成的图像
output_image_path = 'poster/' + time.strftime('%Y%m%d%H%M%S', time.localtime()) + '.png'
image.save(output_image_path)

print(f"Image saved to {output_image_path}")
