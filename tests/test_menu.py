import pytest
from mock import MagicMock

from ssd1306extras import menu


@pytest.fixture
def ssd_display():
    ssd = MagicMock(rows=32, cols=128)
    return ssd


@pytest.fixture
def test_menu(ssd_display):
    m = menu.TextListMenu(ssd_display, ['a', 'b', 'c', 'd'])
    return m


class TestTextListMenu(object):

    def test_select_should_return_current_item(self, test_menu):
        assert test_menu.select() == 'a'

    def test_next_should_set_next_item(self, test_menu):
        test_menu.next()
        assert test_menu.select() == 'b'

    def test_prev_should_set_prev_item(self, test_menu):
        test_menu.next()
        test_menu.next()
        test_menu.prev()
        assert test_menu.select() == 'b'

    def test_prev_should_return_current_item_if_no_previous_exists(self, test_menu):
        test_menu.prev()
        assert test_menu.select() == 'a'

    def test_next_should_return_current_item_if_no_next_exists(self, test_menu):
        for _ in range(len(test_menu._items) + 1):
            test_menu.next()
        assert test_menu.select() == 'd'


class TestFindDisplayableItems(object):

    def get_item_names(self, displayable_items):
        return [item.text for item, _, _ in displayable_items]

    def test_should_have_expected_items(self, test_menu):
        items = test_menu._find_displayable_items()
        assert self.get_item_names(items) == ['a', 'b']

    def test_should_have_expected_items_if_selected_index_in_page(self, test_menu):
        test_menu.page_start_index = 0
        test_menu.selected_index = 1
        items = test_menu._find_displayable_items()
        assert self.get_item_names(items) == ['a', 'b']

    def test_should_move_up_if_selected_item_before_page(self, test_menu):
        test_menu.page_start_index = 1
        test_menu.selected_index = 0
        items = test_menu._find_displayable_items()
        assert self.get_item_names(items) == ['a', 'b']

    def test_should_move_down_if_selected_item_after_page(self, test_menu):
        test_menu.page_start_index = 0
        test_menu.selected_index = 3
        items = test_menu._find_displayable_items()
        assert self.get_item_names(items) == ['c', 'd']

    def test_should_render_one_item_if_not_enough_items_in_list(self, test_menu):
        test_menu.page_start_index = 3
        test_menu.selected_index = 3
        items = test_menu._find_displayable_items()
        assert self.get_item_names(items) == ['d']

    def test_should_return_first_item_as_selected(self, test_menu):
        items = test_menu._find_displayable_items()
        assert items[0][2], 'First item was not returned with selected=True'
        assert not items[1][2], 'Second item was not returned with selected=False'

    def test_should_return_selected_index_as_selected(self, test_menu):
        test_menu.selected_index = 1
        items = test_menu._find_displayable_items()
        assert items[1][2], 'Selected index was not returned with selected=True'

    def test_should_return_expected_start_row_for_each_item(self, test_menu):
        items = test_menu._find_displayable_items()

        assert items[0][1] == 0, 'Unexpected start_row for item'
        assert items[1][1] == 16, 'Unexpected start_row for item'

        test_menu.next()
        test_menu.next()

        items = test_menu._find_displayable_items()
        assert items[0][1] == 0, 'Unexpected start_row for item after paginng'
        assert items[1][1] == 16, 'Unexpected start_row for item after paging'


class TestTextListMenuItem(object):

    def test_modifying_internal_class_should_not_change_external(self, test_menu):
        test_menu.TextItem.set_font_size(20)
        assert menu.TextItem._font_size == 14
        assert test_menu.TextItem._font_size == 20
