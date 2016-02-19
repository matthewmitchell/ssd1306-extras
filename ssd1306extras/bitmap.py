from PIL import Image
from bitarray import bitarray

import ssd1306extras.ssd1306


class Bitmap(object):

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.bits = bitarray(width * height)
        self.bits.setall(False)

    def draw_image(self, image, x=0, y=0, invert=False):
        """Adds a PIL Image file to the bitmap

        Args:
            image (Image): Mode 1 PIL Image
            x (int): Horizontal start position for image
            y (int): Vertical start position for image
        """
        image_width, image_height = image.size
        image_bit_array = bitarray([byte for byte in image.getdata()])

        if invert:
            image_bit_array.invert()

        self.draw_bit_array(image_bit_array, x, y, image_width, image_height)

    def draw_bitmap(self, bitmap, x=0, y=0):
        """Adds a Bitmap to the bitmap

        Args:
            bitmap (Bitmap): Bitmap to add to the current bitmap
            x (int): Horizontal start position for image
            y (int): Vertical start position for image
        """
        self.draw_bit_array(bitmap.bits, x, y, bitmap.width, bitmap.height)

    def draw_bit_array(self, bit_array, x, y, array_width, array_height):

        # Calculate the number of columns that fit on the bitmap
        draw_cols = array_width if array_width + x < self.width else (self.width - x)

        # Calculate the number of rows that fit on the bitmap
        draw_rows = array_height if array_height + y < self.height else (self.height - y)

        image_col_start = 0
        # Adjust image start position and number of columns if negative horizontal position
        if x < 0:
            image_col_start = abs(x)
            draw_cols = array_width - image_col_start
            x = 0

        image_row_start = 0
        # Adjust image starting row for negative vertical position
        if y < 0:
            image_row_start = abs(y)

        start_row = (y * self.width) + x

        for i in range(image_row_start, draw_rows):
            image_start = (i * array_width) + image_col_start
            image_end = image_start + draw_cols

            start = (i * self.width) + start_row
            end = start + draw_cols

            self.bits[start:end] = bit_array[image_start:image_end]

    def draw_rect(self, x, y, width, height):
        self.set_pixels(x, y, width, height, True)

    def clear_block(self, x, y, width, height):
        """Clears a block from the bitmap

        Args:
            x (int): Starting column to clear
            y (int): Starting row to clear
            width (int): Number of columns to clear
            height (int): Number of rows to be cleared
        """
        self.set_pixels(x, y, width, height, False)

    def set_pixels(self, x, y, width, height, status):
        if x >= self.width or y >= self.height:
            return

        if x < 0:
            width += x
            x = 0

        if y < 0:
            height += y
            y = 0

        if width + x > self.width:
            width = self.width - x

        if height + y > self.height:
            height = self.height - y

        for row in range(y, y + height):
            start = (row * self.width) + y
            end = start + width
            self.bits[start:end] = status

    def copy(self):
        """Returns a copy of this bitmap
        """
        new_bitmap = Bitmap(self.width, self.height)
        new_bitmap.bits = self.bits.copy()
        return new_bitmap

    def invert(self):
        """Inverts the bitmap
        """
        self.bits.invert()

    def clear(self):
        """Clears the bitmap
        """
        self.bits.setall(False)

    def dump(self):
        """Outputs a visual representation for the bitmap
        """
        for row in range(self.height):
            line = ''
            for col in range(self.width):
                bit = self.bits[(row*self.width)+col]
                line += '*' if bit else ' '
            print '|{0}|'.format(line)

    def get_bitmap(self):
        """Creates a gaugette Bitmap
        """
        mode = ssd1306extras.ssd1306.SSD1306.MEMORY_MODE_HORIZ
        width = self.width
        height = self.height
        page_size = width * 8
        gaug_bytes = bytearray(width * height / 8)

        for i, bit in enumerate(self.bits):
            if bit:
                page = i/page_size
                bit_shift = (i % page_size) / width
                byte_pos = i % width + (page * width)
                gaug_bytes[byte_pos] = gaug_bytes[byte_pos] | (0x01 << bit_shift)

        gaug_bitmap = ssd1306extras.ssd1306.SSD1306.Bitmap(width, height, list(gaug_bytes), mode)
        return gaug_bitmap


def image_to_bitmap(image_path):
    img = Image.open(image_path)
    img = img.convert(mode='1')
    width, height = img.size

    bitmap = Bitmap(width, height)
    bitmap.draw_image(img)

    return bitmap
