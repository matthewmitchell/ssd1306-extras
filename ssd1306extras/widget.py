import bitmap
import util.text


class TextWidget(object):

    def __init__(self, parent):
        self._parent = parent
        self._bitmap = None
        self._text = ''

        self._font_size = 14
        self._font_file = None
        self._margin = util.text.Margin(0, 0, 0, 0)

        self._width = parent.width
        self._height = parent.height

    @property
    def bitmap(self):
        if self._bitmap is None:
            self.create_bitmap()
        return self._bitmap

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        self._bitmap = None

    @property
    def font_file(self):
        return self.font_file

    @font_file.setter
    def font_file(self, value):
        self._font_file = value
        self.adjust_margin()

    @property
    def font_size(self):
        return self._font_size

    @font_size.setter
    def font_size(self, value):
        self._font_size = value
        self.adjust_margin()

    def adjust_margin(self):
        """Calculates and sets the vertical margin for the current font
        """
        vertical_margin = util.text.find_top_margin(self._font_file, self._font_size, self._height)
        self._margin = self._margin._replace(top=vertical_margin.top)

    def create_bitmap(self):
        image = util.text.image(self._text, self._font_file, self._font_size, self._width, self._height,
                                expand=True, margin=self._margin)
        self._bitmap = bitmap.Bitmap(*image.size[:])
        self._bitmap.draw_image(image)


class ProgressWidget(object):

    def __init__(self, parent):
        self.parent = parent
        self._width = parent.width
        self._height = parent.height

        self._bitmap = bitmap.Bitmap(self._width, self._height)
        self._percent = 0.0

    @property
    def bitmap(self):
        return self._bitmap

    @property
    def percent(self):
        return self._percent

    @percent.setter
    def percent(self, value):
        value = float(value)
        if value > 1.0 or value < 0.0:
            raise ValueError('Percent must be a float between 0.0 and 1.0')

        self._percent = value
        self.update_bitmap()

    def update_bitmap(self):
        self._bitmap.clear()
        width = int(self._width * self._percent)
        self._bitmap.draw_rect(0, 0, width, self._height)


class IconOptionWidget(object):

    class Icon(object):
        def __init__(self, id, bitmap, label, option):
            self.id = id
            self.label = label
            self.bitmap = bitmap
            self.selected_bitmap = bitmap.copy()
            self.selected_bitmap.invert()
            self.option = option
            self.selected = False
            self.enabled = True

        @property
        def width(self):
            return self.bitmap.width

        @property
        def height(self):
            return self.bitmap.height

    def __init__(self, parent):
        self.parent = parent
        self._width = parent.width
        self._height = parent.height

        self._bitmap = bitmap.Bitmap(self._width, self._height)
        self._icons = []
        self.selected = None

    @property
    def bitmap(self):
        self._bitmap.clear()
        x = y = 0
        for icon in self._icons:
            if not icon.enabled:
                continue
            self._draw_icon(icon, x, y)
            x += icon.width
        return self._bitmap

    def add_icon(self, image_path, label, id, option):
        bitmap_img = bitmap.image_to_bitmap(image_path)
        icon = IconOptionWidget.Icon(id, bitmap_img, label, option)
        self._icons.append(icon)

    def select_first(self):
        if not len(self._icons):
            raise IndexError('Cannot select first icons when icon list is empty')

        self.clear_selected()
        self._icons[0].selected = True
        self.selected = 0
        return self._icons[0].label

    def select_next(self):
        self.clear_selected()

        for i in range(self.selected+1, len(self._icons)):
            if self._icons[i].enabled:
                self.selected = i
                break

        self._icons[self.selected].selected = True

        return self._icons[self.selected].label

    def select_prev(self):
        self.clear_selected()

        for i in range(self.selected-1, -1, -1):
            if self._icons[i].enabled:
                self.selected = i
                break
        self._icons[self.selected].selected = True

        return self._icons[self.selected].label

    def find_selected(self):
        """Returns the index of the currently selected icon
        """
        for i, icon in enumerate(self._icons):
            if icon.selected:
                return i

    def clear_selected(self):
        for icon in self._icons:
            icon.selected = False

    def _draw_icon(self, icon, x, y):
        icon_bitmap = icon.selected_bitmap if icon.selected else icon.bitmap
        self._bitmap.draw_bitmap(icon_bitmap, x, y)

    def disable_icon(self, id):
        icon = self._find_icon(id)
        icon.enabled = False

    def enable_icon(self, id):
        icon = self._find_icon(id)
        icon.enabled = True

    def get_current(self):
        index = self.find_selected()
        return self._icons[index].option

    def _find_icon(self, id):
        icon = filter(lambda icon: icon.id == id, self._icons)
        if not len(icon):
            raise KeyError('Icon was not found')
        return icon[0]
