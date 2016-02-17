import pytest
from ssd1306extras import bitmap
from PIL import Image


@pytest.fixture
def small_rec():
    """Creates a rectangle with a border

    Dump of image::
    |*****|
    |*   *|
    |*****|
    """
    width, height = (5, 3)
    image = Image.new('1', (width, height))

    for x in range(width):
        image.putpixel((x, 0), 255)
        image.putpixel((x, height-1), 255)

    for y in range(height):
        image.putpixel((0, y), 255)
        image.putpixel((width-1, y), 255)

    return image


@pytest.fixture
def bmap():
    return bitmap.Bitmap(8, 8)


def assert_bits_set(bmap, expected):
    assert len(bmap.bits) == bmap.width * bmap.height, 'Unexpect bitarray length'
    set_bits = [i for i, bit in enumerate(bmap.bits) if bit]

    try:
        assert set_bits == expected
    except AssertionError as e:
        message = get_visual_output(bmap, expected)
        raise(AssertionError('{0} {1}'.format(message, e)))


def get_visual_output(bmap, expected):
    """Renders a visual representation of expected, set and missing bits
    """
    visual_output = ['\nO = Unexpected bit\nX = Missing bit\n* = Correct bit\n']
    row_info = '|'
    for i in range(len(bmap.bits)):
        value = ' '
        if bmap.bits[i]:
            value = 'O' if i not in expected else '*'
        elif not bmap.bits[i] and i in expected:
            value = 'X'

        row_info += value
        if not (i+1) % bmap.width:
            visual_output.append(row_info + '|')
            row_info = '|'
    return '\n'.join(visual_output) + '\n'


class TestDrawImage(object):

    def test_should_contain_image_without_offset(self, bmap, small_rec):
        bmap.draw_image(small_rec)
        assert_bits_set(bmap, expected=[0, 1, 2, 3, 4, 8, 12, 16, 17, 18, 19, 20])

    def test_should_contain_image_with_offset(self, bmap, small_rec):
        bmap.draw_image(small_rec, 2, 3)
        assert_bits_set(bmap, expected=[26, 27, 28, 29, 30, 34, 38, 42, 43, 44, 45, 46])

    def test_should_contain_image_with_horizontal_overflow(self, bmap, small_rec):
        bmap.draw_image(small_rec, 5, 0)
        assert_bits_set(bmap, expected=[5, 6, 7, 13, 21, 22, 23])

    def test_should_contain_image_with_vertical_overflow(self, bmap, small_rec):
        bmap.draw_image(small_rec, 0, 6)
        assert_bits_set(bmap, expected=[48, 49, 50, 51, 52, 56, 60])

    def test_should_contain_image_with_negative_margins(self, bmap, small_rec):
        bmap.draw_image(small_rec, -2, -1)
        assert_bits_set(bmap, expected=[2, 8, 9, 10])

    def test_should_contain_multiple_images(self, bmap, small_rec):
        expected = [0, 1, 2, 3, 4, 8, 12, 16, 17, 18, 19, 20, 24, 25, 26, 27, 28, 32, 36, 40, 41, 42, 43, 44]
        bmap.draw_image(small_rec, 0, 0)
        bmap.draw_image(small_rec, 0, 3)
        assert_bits_set(bmap, expected=expected)

    def test_should_contain_inverted_image(self, bmap, small_rec):
        bmap.draw_image(small_rec, 0, 0, invert=True)
        assert_bits_set(bmap, expected=[9, 10, 11])


class TestGetBitmap(object):

    def test_should_return_valid_bitmap(self, small_rec):
        expected = [7, 5, 5, 5, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 7, 5, 5, 229, 167, 160, 160, 224]

        bmap = bitmap.Bitmap(16, 16)
        bmap.draw_image(small_rec, 0, 0)
        bmap.draw_image(small_rec, 8, 8)
        bmap.draw_image(small_rec, 11, 13)
        gaugette_bitmap = bmap.get_bitmap()

        assert gaugette_bitmap.data == expected


class TestInvert(object):

    def test_should_invert_empty_bitmap(self, bmap):
        expected = [i for i in range(bmap.width * bmap.height)]
        bmap.invert()
        assert_bits_set(bmap, expected)

    def test_should_invert_bitmap_with_image(self, bmap, small_rec):
        expected = [5, 6, 7, 9, 10, 11, 13, 14, 15, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
                    36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
                    59, 60, 61, 62, 63]

        bmap.draw_image(small_rec, 0, 0)
        bmap.invert()
        assert_bits_set(bmap, expected=expected)


class TestClear(object):

    def test_should_clear_empty_bitmap(self, bmap):
        bmap.clear()
        assert_bits_set(bmap, expected=[])

    def test_should_clear_bitmap_with_image(self, bmap, small_rec):
        bmap.draw_image(small_rec, 0, 0)
        bmap.clear()
        assert_bits_set(bmap, expected=[])


class TestClearBlock(object):

    def test_should_clear_block_from_empty_bitmap(self, bmap):
        bmap.clear_block(0, 0, 2, 2)
        assert_bits_set(bmap, expected=[])

    def test_should_clear_part_of_image(self, bmap, small_rec):
        bmap.draw_image(small_rec, 0, 0)
        bmap.clear_block(0, 0, 4, 2)
        assert_bits_set(bmap, expected=[4, 12, 16, 17, 18, 19, 20])

    def test_should_clear_full_image(self, bmap):
        bmap.invert()
        bmap.clear_block(0, 0, 8, 8)
        assert_bits_set(bmap, expected=[])

    def test_should_clear_only_bits_within_image(self, bmap, small_rec):
        bmap.draw_image(small_rec, 0, 0)
        bmap.clear_block(1, 1, 1000, 1000)
        assert_bits_set(bmap, expected=[0, 1, 2, 3, 4, 8, 16])
