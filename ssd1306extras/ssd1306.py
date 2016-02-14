import gaugette.ssd1306


class SSD1306(gaugette.ssd1306.SSD1306):

    def display_block(self, bitmap, row, col, col_count, col_offset=0):
        mode = self.MEMORY_MODE_VERT

        try:
            if bitmap.mode is not None:
                mode = bitmap.mode
        except AttributeError:
            pass

        page_count = bitmap.rows >> 3
        page_start = row >> 3
        page_end = page_start + page_count - 1
        col_start = col
        col_end = col + col_count - 1
        self.command(self.SET_MEMORY_MODE, mode)
        self.command(self.SET_PAGE_ADDRESS, page_start, page_end)
        self.command(self.SET_COL_ADDRESS, col_start, col_end)
        start = col_offset * page_count
        length = col_count * page_count
        self.data(bitmap.data[start:start+length])

    class Bitmap(gaugette.ssd1306.SSD1306.Bitmap):

        def __init__(self, cols, rows, data=None, mode=None):
            """Creates a bitmap without initializing a data list
            """
            self.mode = mode
            self.rows = rows
            self.cols = cols
            self.bytes_per_col = rows / 8
            self.data = data

            if self.data is None:
                self.data = [0] * (self.cols * self.bytes_per_col)
