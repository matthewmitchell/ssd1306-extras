import collections

from PIL import Image, ImageDraw, ImageFont


Margin = collections.namedtuple('Margin', ['top', 'right', 'bottom', 'left'])


def image(text, font_file, size, width=None, height=None, expand=False, margin=None):
    """Creates a text image

    Args:
        text (str): Text to be rendered on image
        font_file (str): Path to the font file
        size (int): Font size of the text
        width (int): Width of the image
        height (int): Height of the image
        expand (bool): If True, image will be horizontally expanded to fit text
        h_align (Align type): Horizontal alignment of text
        v_align (Align type): Vertical alignment of text
        margin (int): Placement for text

    Returns:
        PIL Image containing the rendered text
    """
    font = _create_font(font_file, size)
    image = Image.new('1', (width, height))

    if margin is None:
        margin = Margin(0, 0, 0, 0)

    image_draw = ImageDraw.Draw(image)

    if expand:
        text_width, text_height = image_draw.textsize(text, font=font)
        text_width += (margin.left + margin.right)
        if text_width > width:
            image = image.resize((text_width, height))
            image_draw = ImageDraw.Draw(image)

    image_draw.text((margin.left, margin.top), text, font=font, fill=255)

    return image


def find_top_margin(font_file, size, height):
    """Finds the top margin that will visually center the font vertically

    Args:
        font_file (str): Path to the font file being centered
        size (int): Size of the font
        height (int): Height of the image text is being centered on

    Returns:
        Margin namedtuple containing a top margin
    """
    font = _create_font(font_file, size)

    ascender_bbox = _get_bounding_box('ATP', font)
    descender_bbox = _get_bounding_box('gpj', font)

    top_padding = ascender_bbox[3] - (ascender_bbox[3] - ascender_bbox[1])
    visual_height = descender_bbox[3] - ascender_bbox[1]

    vertical_margin = height - visual_height

    if not vertical_margin % 2:
        vertical_margin += 1

    top_margin = (vertical_margin / 2) - top_padding + 1

    return Margin(top=top_margin, right=0, bottom=0, left=0)


def _get_bounding_box(text, font):
    """Finds the bounding box for the rendered text

    Args:
        text (str): String to get the bounding box for
        font (ImageFont): Font to use when rendering text

    Retruns:
        4-tuple defining the left, upper, right, and bottom pixel
        for the bounding box.
    """
    image = Image.new('1', (1, 1))
    image_draw = ImageDraw.Draw(image)

    text_width, text_height = image_draw.textsize(text, font=font)

    image = image.resize((text_width, text_height))
    image_draw = ImageDraw.Draw(image)

    image_draw.text((0, 0), text, font=font, fill=255)

    return image.getbbox()


def _create_font(font_file=None, size=14):
    font = None

    if font_file is not None:
        font = ImageFont.truetype(filename=font_file, size=size)

    return font
