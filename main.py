import json
import os

from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askopenfilenames

BACKGROUND_HEIGHT = 978
BACKGROUND_WIDTH = 600
DEFAULT_SIZE = 140
SMALL_SIZE = 60


def read_image(path):
    return Image.open(path).convert('RGBA')


def get_dominant_color(image):
    color_count = {}
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            pixel = image.getpixel((x, y))
            # check if the pixel is mostly white
            if pixel[0] > 200 and pixel[1] > 200 and pixel[2] > 200:
                continue
            if pixel == (0, 0, 0, 0):
                continue
            if pixel in color_count:
                color_count[pixel] += 1
            else:
                color_count[pixel] = 1
    return max(color_count, key=color_count.get)


def resize_image(image: Image, size: int = DEFAULT_SIZE):
    x = image.size[0]
    y = image.size[1]
    if x > y:
        pct = size / x
        x = int(x * pct)
        y = int(y * pct)
    else:
        pct = size / y
        x = int(x * pct)
        y = int(y * pct)
    return image.resize((x, y))


def paste_at(background: Image, image: Image, x: int, y: int):
    background.paste(image, (x - int(image.size[0] / 2), y - int(image.size[1] / 2)), image)


def centered_x(background: Image, image: Image):
    return int((background.size[0] - image.size[0]) / 2)


def paste_rotated_at(background: Image, image: Image, x: int, y: int, angle: int = 180):
    image = image.rotate(angle)
    paste_at(background, image, x, y)


def main():
    system_fonts = font_manager.findSystemFonts()
    Tk().withdraw()
    font_path = askopenfilename(initialdir='\\'.join(system_fonts[0].split('\\')[0:-1])) or system_fonts[0]
    font = ImageFont.truetype(font_path, size=100)
    with open('preset/sizes.json', 'r') as f:
        settings = json.load(f)

    Tk().withdraw()
    files = askopenfilenames(filetypes=[('Image files', '.png .jpg .jpeg .gif')])

    for file in files:
        print(f'Processing {file}...')
        for setting in settings:
            background = read_image('preset/blank_card.png')
            folder_name = f"output/{file.split('/')[-1].split('.')[0]}"
            icon = read_image(file)

            config = settings[setting]
            icon = resize_image(icon, (config['size'] if 'size' in config else DEFAULT_SIZE))
            for position in config['positions']:
                paste_rotated_at(background, icon, position['x'], position['y'],
                                 (180 if 'rotate' in position and position['rotate'] else 0))
            img_txt = Image.new('RGBA', font.getsize(config['symbol']))
            ImageDraw.Draw(img_txt).text((0, 0), config['symbol'], font=font, fill=get_dominant_color(icon))
            x = 65
            y = 70
            paste_at(background, img_txt, x, y)
            paste_rotated_at(background, img_txt, BACKGROUND_WIDTH - x, BACKGROUND_HEIGHT - y)

            icon = read_image(file)
            icon = resize_image(icon, SMALL_SIZE)
            paste_at(background, icon, x, y + img_txt.size[1] - 10)
            paste_rotated_at(background, icon, BACKGROUND_WIDTH - x, BACKGROUND_HEIGHT - y - img_txt.size[1] + 10)
            if not os.path.exists(folder_name):
                os.mkdir(folder_name)

            background.save(f"{folder_name}/{setting}.png")


if __name__ == '__main__':
    if not os.path.exists('output'):
        os.mkdir('output')
    main()
