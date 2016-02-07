from bitarray import bitarray
import gaugette.ssd1306

# x = col = width
# y = row = height


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

        # Calculate the number of columns that fit on the bitmap
        draw_cols = image_width if image_width + x < self.width else (self.width - x)

        # Calculate the number of rows that fit on the bitmap
        draw_rows = image_height if image_height + y < self.height else (self.height - y)

        image_col_start = 0
        # Adjust image start position and number of columns if negative horizontal position
        if x < 0:
            image_col_start = abs(x)
            draw_cols = image_width - image_col_start
            x = 0

        image_row_start = 0
        # Adjust image starting row for negative vertical position
        if y < 0:
            image_row_start = abs(y)

        start_row = (y * self.width) + x

        for i in range(image_row_start, draw_rows):
            image_start = (i * image_width) + image_col_start
            image_end = image_start + draw_cols

            start = (i * self.width) + start_row
            end = start + draw_cols

            self.bits[start:end] = image_bit_array[image_start:image_end]

    def draw_bitmap(self, bitmap, x=0, y=0):
        """Adds a Bitmap to the bitmap

        Args:
            bitmap (Bitmap): Bitmap to add to the current bitmap
            x (int): Horizontal start position for image
            y (int): Vertical start position for image
        """
        pass

    def invert(self):
        """Inverts the bitmap
        """
        self.bits.invert()

    def clear_block(self, x, y, col_count, row_count):
        """Clears a block from the bitmap

        Args:
            x (int): Starting column to clear
            y (int): Starting row to clear
            col_count (int): Number of columns to clear
            row_count (int): Number of rows to be cleared
        """
        if x >= self.width or y >= self.height:
            return

        if x < 0:
            x = 0

        if y < 0:
            y = 0

        if col_count + x > self.width:
            col_count = self.width - x

        if row_count + y > self.height:
            row_count = self.height - y

        for row in range(y, y + row_count):
            start = (row * self.width) + y
            end = start + col_count
            self.bits[start:end] = False

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
        gaug_bitmap = gaugette.ssd1306.SSD1306.Bitmap(self.width, self.height)
        page_length = self.width * 8
        total_pages = (self.width * self.height) / page_length

        gaug_bytes = []

        for col in range(self.width):
            for page in range(total_pages):
                page_start = page * page_length
                start = page_start + col
                byte = 0
                for bit in reversed(self.bits[start:page_start+page_length:self.width]):
                    byte = (byte << 1) | bit
                gaug_bytes.append(byte)

        gaug_bitmap.data = gaug_bytes
        return gaug_bitmap
