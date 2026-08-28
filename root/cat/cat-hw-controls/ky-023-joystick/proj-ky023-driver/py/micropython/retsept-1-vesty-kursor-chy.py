cursor_x, cursor_y = 64, 32             # поточна позиція (напр. пікселі дисплея)

def move_cursor():
    global cursor_x, cursor_y
    vx = read_axis(horizontal)          # −100..+100
    vy = read_axis(vertical)

    # швидкість у «пікселів за крок»: 100 на осі → 5 пікселів за виклик
    cursor_x += int(vx / 20)
    cursor_y += int(vy / 20)

    # не давати курсору втекти за межі екрана 128×64
    cursor_x = max(0, min(127, cursor_x))
    cursor_y = max(0, min(63,  cursor_y))
