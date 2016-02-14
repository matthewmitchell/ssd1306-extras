import gaugette.ssd1306
import ssd1306extras.panel
import ssd1306extras.widget


RESET_PIN = 15
DC_PIN = 16

ssd = gaugette.ssd1306.SSD1306(reset_pin=RESET_PIN, dc_pin=DC_PIN)
ssd.begin()
ssd.flip_display()

panel = ssd1306extras.panel.Panel(ssd)
top, bottom = panel.vertical_panels([20])

top.item = ssd1306extras.widget.TextWidget(parent=top)
top.item.text = 'ABCjgpflzx'
top.item.font_size = 20
top.item.font_file = '../player/fonts/Gen-Light.otf'

bottom.item = ssd1306extras.widget.TextWidget(parent=bottom)
bottom.item.text = 'ABCjgpflzx'
bottom.item.font_size = 10
bottom.item.font_file = '../player/fonts/Gen-Light.otf'


panel.draw()
