# --- keypad_begin / keypad_scan_raw / keypad_char / keypad_read — з кроків 1..4 ---

keypad_begin()          # ніжки: рядки PULL_UP, стовпці OUT=HIGH

while True:
    key = keypad_read()     # з'явився свіжий натиск?
    if key:
        print("натиснуто:", key)
        # тут — своя реакція: додати цифру до PIN, зрушити меню, ввести число…
    # цикл крутиться швидко й вільно; скан коштує лічені мікросекунди на прохід
