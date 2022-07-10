import textwrap
from io import BytesIO
from typing import Tuple, List

import cv2
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont
from image_similarity_measures.quality_metrics import ssim


def generate_meme(url: str, top_text: str, bottom_text: str, meme_id: int) -> Tuple[str, str]:
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = img.convert('RGB')
    src_path = get_meme_src_path(meme_id)
    img.save(src_path)

    img = draw_meme(img, top_text, bottom_text)

    path = get_meme_path(meme_id)
    img.save(path)
    return src_path, path


def draw_meme_from_path(img_path: str, top_text: str, bottom_text: str) -> Image:
    img = Image.open(img_path)
    return draw_meme(img, top_text, bottom_text)


def draw_meme(img: Image, top_text: str, bottom_text: str) -> Image:
    draw = ImageDraw.Draw(img)
    font_size = max(img.size) / 10

    font = ImageFont.truetype("fonts/impact.ttf", int(font_size))
    # draw.text((x, y),"Sample Text",(r,g,b))
    char_in_row = calc_char_in_row(draw, top_text, img.size[0], font, max(1, int(font_size / 40)))
    draw.multiline_text((img.size[0] / 2, 1), "\n".join(textwrap.wrap(top_text, width=char_in_row)),
                        fill=(255, 255, 255), stroke_fill=(0, 0, 0),
                        stroke_width=max(1, int(font_size / 40)),
                        font=font, anchor='ma', align='center')
    char_in_row = calc_char_in_row(draw, bottom_text, img.size[0], font, max(1, int(font_size / 40)))
    draw.multiline_text((img.size[0] / 2, img.size[1] - 2), "\n".join(textwrap.wrap(bottom_text, width=char_in_row)),
                        fill=(255, 255, 255), stroke_fill=(0, 0, 0),
                        stroke_width=max(1, int(font_size / 40)),
                        font=font, anchor='md', align='center')
    return img


def img2buf(img: Image) -> BytesIO:
    imgio = BytesIO()
    img.save(imgio, 'JPEG')
    imgio.seek(0)
    return imgio


def calc_closest_val(measures):
    result = []
    closest = max(measures.values())

    for key, value in measures.items():
        if value == closest:
            result.append(key)

    return result


def search_similar(url: str, images: List[Tuple[int, str]]) -> List[int]:
    img = Image.open(BytesIO(requests.get(url).content))
    test_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    scale_percent = 100  # percent of original img size
    width = int(img.size[0] * scale_percent / 100)
    height = int(img.size[1] * scale_percent / 100)
    dim = (width, height)
    ssim_measures = {}
    for image in images:
        data_img = cv2.imread(image[1])
        resized_img = cv2.resize(data_img, dim, interpolation=cv2.INTER_AREA)
        ssim_measures[image[0]] = ssim(test_img, resized_img)

    return calc_closest_val(ssim_measures)


def calc_char_in_row(draw: ImageDraw, text: str, width: int, font: ImageFont, stroke_width: int):
    low = 1
    high = width
    mid = 0

    while low < high - 1:
        mid = (high + low) // 2
        x = draw.multiline_textsize('\n'.join(textwrap.wrap(text, width=mid)), font=font, stroke_width=stroke_width)[0]

        if x >= width:
            high = mid - 1
        else:
            low = mid

    return low


def get_meme_path(meme_id: int):
    return f'memes/meme_{meme_id}.jpg'


def get_meme_src_path(meme_id: int):
    return f'memes/meme_src_{meme_id}.jpg'
