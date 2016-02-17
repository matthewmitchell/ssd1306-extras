import bitmap


class Panel(object):
    """Panel that can contain other panels
    """

    def __init__(self, ssd_display, width=None, height=None, top=0, left=0):
        self.ssd_display = ssd_display
        self.width = width if width is not None else ssd_display.cols
        self.height = height if height is not None else ssd_display.rows

        self._bitmap = bitmap.Bitmap(self.width, self.height)
        self.top = top
        self.left = left
        self._item = None
        self._items = []

    def draw(self, refresh=False):
        bitmap = self.bitmap
        self.ssd_display.clear_display()

        if refresh:
            self.ssd_display.display()

        self.ssd_display.display_block(bitmap.get_bitmap(), self.top, self.left, self.width)

    @property
    def bitmap(self):
        """Returms the bitmap for the panel
        """
        for item in self._items:
            self._bitmap.draw_bitmap(item['obj'].bitmap, item['x'], item['y'])

        return self._bitmap

    def add_widget(self, widget, x=0, y=0):
        """Adds a widget to be rendered at the given location
        """
        item = {'obj': widget, 'x': x, 'y': y}
        self._items.append(item)
