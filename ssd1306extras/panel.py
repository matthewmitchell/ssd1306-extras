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
        self._panels = []
        self._item = None

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
        for panel in self._panels:
            self._bitmap.draw_bitmap(panel.bitmap, panel.left, panel.top)

        if self._item is not None:
            self._bitmap.draw_bitmap(self._item.bitmap, 0, 0)

        return self._bitmap

    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, itm):
        self._item = itm

    def horizonal_panels(self, positions):
        """Creates sub-panels for the current panel

        Args:
            positions (list[int]): List of column positions defining the
                boundaries of the new panels

        Returns:
            List containing the new panels in left to right order.
        """
        pass

    def vertical_panels(self, positions):
        """Creates sub-panels for the current panel

        Args:
            positions (list[int]): List of row positions defining the
                boundaries of the new panels

        Returns:
            List containing the new panels in top to bottom order.
        """
        positions = sorted(positions)
        if positions[0] != 0:
            positions.insert(0, 0)

        if positions[-1] != self.height:
            positions.append(self.height)

        panels = []
        top = 0
        for i in range(len(positions)-1):
            height = positions[i+1] - positions[i]
            panel = Panel(self.ssd_display, self.width, height, top=top, left=0)
            panels.append(panel)
            top += height

        self._panels += panels

        return panels
