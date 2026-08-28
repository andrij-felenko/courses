# Викликається веб-сервером, коли прийшла заповнена форма (метод POST).
# body — вже прочитане тіло запиту (метод POST); у MicroPython рядок
# несе власну довжину, тож нуль-термінатор дописувати не треба.
def on_credentials_post(body, respond):
    # Розбираємо поля форми ssid=...&pass=...
    fields = parse_form(body)               # {'ssid': ..., 'pass': ...}
    ssid = fields.get('ssid', '')
    passwd = fields.get('pass', '')

    # Чужому вводу не довіряй: порожня назва — не приймаємо
    if not ssid:
        respond('SSID порожній')
        return

    # Зберігаємо в NVS — щоб пережити перезавантаження й більше не питати
    import esp32
    nvs = esp32.NVS('wifi')
    nvs.set_blob('ssid', ssid.encode())
    nvs.set_blob('pass', passwd.encode())
    nvs.commit()

    respond("Прийнято. Пристрій під'єднується...")
    # Далі — погасити точку доступу й спробувати STA-підключення (див. замітку)
    schedule_switch_to_station()
