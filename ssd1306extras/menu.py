import os.path

import bitmap
import util.text


class TextItem(object):
    """A single menu item
    """

    _font_size = 14
    _font_file = None
    _height = 16
    _margin = util.text.Margin(0, 0, 0, 0)

    def __init__(self, text, width, height):
        """Create a new Item instance

        Args:
            text (str): Text to be displayed
            width (int): Width of item
            height (int): Height of item
        """
        self.text = text
        self._height = height
        self._width = width
        self._bitmap = None

    @property
    def bitmap(self):
        """Reuturns a bitmap representation of the
        """
        if self._bitmap is None:
            self.create_bitmap()
        return self._bitmap

    @classmethod
    def set_font_file(cls, value):
        cls._font_file = value
        cls.adjust_margin()

    @classmethod
    def set_font_size(cls, value):
        cls._font_size = value
        cls.adjust_margin()

    @classmethod
    def set_height(cls, value):
        cls._height = value
        cls.adjust_margin()

    @classmethod
    def set_indent(cls, value):
        cls._margin = cls._margin._replace(left=value)

    def create_bitmap(self):
        img = util.text.image(self.text, self._font_file, self._font_size, self._width, self._height,
                              margin=self._margin)
        self._bitmap = img

    def ready(self):
        """Returns status of item bitmap

        Returns:
            True if bitmap is ready, False if it has not been created

        """
        return self._bitmap is not None

    def prepare(self):
        """Prepares the item to be displayed.

        This only needs to be used if you want to eagerly load the bitmap for
        the item. Bitmaps are lazy loaded during access.
        """
        if self._bitmap is None:
            self.create_bitmap()

    def clear_bitmap(self):
        """Removes the current bitmap

        This is useful if you want to change the appearance of a menu item
        with a bitmap already loaded.
        """
        self._bitmap = None

    @classmethod
    def adjust_margin(cls):
        """Calculates and sets the vertical margin for the current font
        """
        vertical_margin = util.text.find_top_margin(cls._font_file, cls._font_size, cls._height)
        cls._margin = cls._margin._replace(top=vertical_margin.top)


class TextListMenu(object):
    """Display a scrollable list of options.
    """

    def __init__(self, ssd_display, item_list):
        self.ssd_display = ssd_display
        self.item_list = item_list

        self._bitmap = bitmap.Bitmap(ssd_display.cols, ssd_display.rows)
        self._items = []

        self.item_height = 16
        self.item_width = ssd_display.cols

        self.items_per_page = ssd_display.rows / self.item_height
        self.current_page = 0

        self.selected_index = 0
        self.page_start_index = 0

        # Create a new TextItem class that can be modified without affecting other menus
        self.TextItem = type('TextItem', TextItem.__bases__, dict(TextItem.__dict__))
        self.TextItem.adjust_margin()
        self.TextItem.set_indent(5)

        self._create_items()

    def _create_items(self):
        for text in self.item_list:
            new_item = self.TextItem(text, self.item_width, self.item_height)
            self._items.append(new_item)

    def set_font(self, font_file, size):
        if not os.path.isfile(font_file):
            raise IOError('Cannot find font: {0}'.format(font_file))
        self.TextItem.set_font_file(font_file)
        self.TextItem.set_font_size(size)

    def draw(self):
        for item, start_row, selected in self._find_displayable_items():
            self._bitmap.draw_image(item.bitmap, 0, start_row, invert=selected)
        bmap = self._bitmap.get_bitmap()
        self.ssd_display.display_block(bmap, 0, 0, self._bitmap.width)

    def _find_displayable_items(self):
        """Finds the items to be rendered on the display

        Returns:
            List of 3-tuples with each containing the item, start_position (height),
            and selected status.
        """
        displayable_items = []

        # Adjust page start to ensure selected item is on page
        if self.selected_index < self.page_start_index:
            self.page_start_index = self.selected_index
        elif self.selected_index >= self.page_start_index + self.items_per_page:
            self.page_start_index = self.selected_index - (self.items_per_page - 1)

        end_index = min(self.page_start_index + self.items_per_page, len(self._items))
        start_row = 0

        for i in range(self.page_start_index, end_index):
            selected = i == self.selected_index

            displayable_items.append((self._items[i], start_row, selected))
            start_row += self._items[i]._height

        return displayable_items

    def next(self):
        if self.selected_index >= len(self._items) - 1:
            return
        self.selected_index += 1
        self.draw()

    def prev(self):
        if self.selected_index <= 0:
            return
        self.selected_index -= 1
        self.draw()

    def select(self):
        return self._items[self.selected_index].text
