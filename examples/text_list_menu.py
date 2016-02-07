import gaugette.ssd1306
import ssd1306extras.menu

RESET_PIN = 15
DC_PIN = 16

ssd = gaugette.ssd1306.SSD1306(reset_pin=RESET_PIN, dc_pin=DC_PIN)
ssd.begin()
ssd.flip_display()

grocery_list = ['apples', 'bananas', 'milk', 'eggs', 'cereal', 'ice cream', 'cheese']

menu = ssd1306extras.menu.TextListMenu(ssd, grocery_list)

menu.draw()
for _ in range(len(grocery_list)):
    menu.next()

for _ in range(len(grocery_list)):
    menu.prev()

print menu.select()
