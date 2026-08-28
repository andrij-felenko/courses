# «Екран»: поточне число живе прямо у віджеті-полі. Модель? Її нема.
screen_target = 22          # ← джерело правди — саме поле на екрані
bar_widget = ""             # намальована смужка

def on_plus_clicked():
    global screen_target, bar_widget
    # 1) ВВІД+ЧИТАННЯ: беремо поточне число з ПОЛЯ на екрані
    current = screen_target
    # 2) ПРАВИЛО предметної області: підняти на 1, але не вище 30
    current = current + 1
    if current > 30:
        current = 30
    # 3) РЕНДЕР: вписати назад у поле і перемалювати смужку
    screen_target = current
    filled = round((current - 5) / (30 - 5) * 20)
    bar_widget = "█" * filled + "·" * (20 - filled)
    # 4) ЗБЕРЕЖЕННЯ: записати на диск
    with open("target.txt", "w") as fp:
        fp.write(str(current))

def on_minus_clicked():
    global screen_target, bar_widget
    current = screen_target
    current = current - 1
    if current < 5:                 # ← та сама логіка, лише межа інша
        current = 5
    screen_target = current
    filled = round((current - 5) / (30 - 5) * 20)   # ← і рендер скопійовано
    bar_widget = "█" * filled + "·" * (20 - filled)
    with open("target.txt", "w") as fp:             # ← і збереження скопійовано
        fp.write(str(current))
