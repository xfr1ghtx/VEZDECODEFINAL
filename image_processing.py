import textwrap
from io import BytesIO
from typing import Tuple, List

import cv2
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont
from image_similarity_measures.quality_metrics import ssim

import random as rng

rng.seed(12345)

VK_COLORS = [
    (0, 119, 255),
    (128, 36, 192),
    (255, 57, 133),
    (0, 234, 255),
    (190, 182, 174),
    (23, 214, 133),
    (222, 222, 222)
]


def thresh_callback(src_gray):
    canny_output = cv2.Canny(src_gray, 0, 255)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    dilated = cv2.dilate(canny_output, kernel)
    cnts, _ = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

    drawing = np.full((canny_output.shape[0], canny_output.shape[1], 3), VK_COLORS[0], dtype=np.uint8)

    for i in range(len(cnts)):
        color = VK_COLORS[(1 + i) % len(VK_COLORS[1:])]
        cv2.drawContours(drawing, cnts, contourIdx=i, color=color, thickness=-1)
        cv2.drawContours(drawing, cnts, contourIdx=i, color=color, thickness=1)

    drawing = cv2.cvtColor(drawing, cv2.COLOR_RGB2BGR)
    return drawing


def draw_vk_colors(img: Image):
    src_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    blr_ker = (3, 3)
    thresh = 190
    src_gray = cv2.blur(src_gray, blr_ker)
    # src_gray = cv2.bilateralFilter(src_gray, 11, 17, 17)

    return thresh_callback(src_gray)


def draw_pattern(img: Image):
    img2 = cv2.imread('p3.jpg')
    img2 = cv2.resize(img2, (img.shape[1], img.shape[0]))

    patterns = [img2]

    fill_color = [127, 256, 32]  # any BGR color value to fill with
    mask_value = 255  # 1 channel white (can be any non-zero uint8 value)

    canny_output = cv2.Canny(img, 0, 255)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    dilated = cv2.dilate(canny_output, kernel)
    contours, _ = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    # our stencil - some `mask_value` contours on black (zeros) background,
    # the image has same height and width as `img`, but only 1 color channel

    for i, c in enumerate(contours[:1]):
        stencil = np.zeros(img.shape[:-1]).astype(np.uint8)
        cv2.fillPoly(stencil, [c], mask_value)
        sel = stencil != mask_value  # select everything that is not mask_value
        img[sel] = ~patterns[0][sel]

    return img


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
    np_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    np_img = draw_pattern(np_img)
    np_img = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(np_img)

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
