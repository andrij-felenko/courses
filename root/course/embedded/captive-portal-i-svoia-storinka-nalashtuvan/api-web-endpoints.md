# 📋 Специфікація маршрутів та REST API вбудованого порталу

Коли мікроконтролер переходить у режим точки доступу (SoftAP), він бере на себе роль ізольованого шлюзу локальної бездротової мережі. Усі запити підключених смартфонів, планшетів та ноутбуків приходять на вбудований HTTP-сервер на стандартному TCP-порту 80. Щоб забезпечити автоматичну появу системного вікна налаштувань (Captive Network Assistant) на будь-якій операційній системі та надати надійний програмний інтерфейс для фронтенду Single Page Application (SPA), вбудований сервер мікроконтролера реалізує два рівні маршрутизації: перехоплення зондів зв'язності та службові REST API ендпоінти.

---

### 1. Маршрути перехоплення зондів зв'язності (Probe Endpoints)

Сучасні операційні системи одразу після отримання мережевих реквізитів по протоколу DHCP надсилають фонові тестові HTTP-запити на власні еталонні сервери. Якщо замість очікуваного еталонного статусу чи вмісту повертається статус перенаправлення `HTTP 302 Found` або несподівана HTML-сторінка, операційна система фіксує наявність шлюзу авторизації (Captive Portal) і відкриває спеціалізоване системне вікно WebSheet над екраном.

Завдання вбудованого веб-сервера полягає у перехопленні таких контрольних шляхів та безумовному поверненні статусу `HTTP 302 Found` із заголовком `Location: http://192.168.4.1/setup`, або в прямій віддачі HTML-сторінки майстра налаштування.

| Операційна система / Клієнт | Еталонний URL та Host | Очікувана поведінка при доступі до Інтернету | Дія вбудованого сервера для перехоплення |
|---|---|---|---|
| **Apple iOS / macOS / iPadOS** | `GET /hotspot-detect.html`<br>`Host: captive.apple.com`<br>`Host: www.apple.com` | `HTTP 200 OK`<br>Тіло містить точний рядок:<br>`<HTML><HEAD><TITLE>Success</TITLE></HEAD><BODY>Success</BODY></HTML>` | `HTTP 302 Found`<br>`Location: http://192.168.4.1/setup`<br>або `200 OK` з HTML-формою |
| **Apple Legacy Probes** | `GET /library/test/success.html`<br>`Host: www.apple.com` | `HTTP 200 OK`<br>Тіло: `Success` | `HTTP 302 Found`<br>`Location: http://192.168.4.1/setup` |
| **Google Android / ChromeOS** | `GET /generate_204`<br>`GET /gen_204`<br>`Host: connectivitycheck.gstatic.com` | `HTTP 204 No Content`<br>(Порожнє тіло, нульова довжина `Content-Length: 0`) | `HTTP 302 Found`<br>`Location: http://192.168.4.1/setup`<br>або `200 OK` з HTML-формою |
| **Google Android (Резервні зонди)** | `GET /generate_204`<br>`Host: clients3.google.com`<br>`Host: connectivitycheck.android.com`<br>`Host: play.googleapis.com` | `HTTP 204 No Content` | `HTTP 302 Found`<br>`Location: http://192.168.4.1/setup` |
| **Microsoft Windows (NCSI Active Probe)** | `GET /connecttest.txt`<br>`Host: www.msftconnecttest.com`<br>`Host: ipv6.msftconnecttest.com` | `HTTP 200 OK`<br>Тіло: точний рядок `Microsoft Connect Test` | `HTTP 302 Found`<br>`Location: http://192.168.4.1/setup`<br>або `200 OK` з HTML-формою |
| **Microsoft Windows (NCSI Legacy)** | `GET /ncsi.txt`<br>`Host: www.msftncsi.com` | `HTTP 200 OK`<br>Тіло: точний рядок `Microsoft NCSI` | `HTTP 302 Found`<br>`Location: http://192.168.4.1/setup` |
| **Mozilla Firefox (Desktop / Mobile)** | `GET /success.txt`<br>`Host: detectportal.firefox.com` | `HTTP 200 OK`<br>Тіло: точний рядок `success\n` | `HTTP 302 Found`<br>`Location: http://192.168.4.1/setup` |
| **Будь-який інший запит (Wildcard Fallback)** | `GET /*`<br>`Host: *` | Звичайне завантаження цільового сайту | `HTTP 302 Found`<br>`Location: http://192.168.4.1/setup` |

#### Формат відповіді перенаправлення (HTTP 302 Redirect)

```http
HTTP/1.1 302 Found
Location: http://192.168.4.1/setup
Content-Type: text/html; charset=utf-8
Content-Length: 0
Connection: close
Cache-Control: no-cache, no-store, must-revalidate
Pragma: no-cache
Expires: 0
```

#### Заголовки заборони кешування та їхня роль

Сучасні браузери агресивно кешують відповіді сервера для оптимізації мережевого трафіку. Для порталу авторизації кешування є критичним ризиком:
- Якщо клієнт закешує відповідь `302 Found` для домену `captive.apple.com`, при наступному підключенні до робочого домашнього роутера телефон може знову перенаправляти користувача на локальну адресу `192.168.4.1`, вважаючи, що доступу до інтернету немає.
- Якщо клієнт закешує відповідь `200 OK` для ендпоінта `/api/scan`, сторінка конфігурації показуватиме застарілий список Wi-Fi мереж навіть після зміни оточення або переміщення пристрою.

Щоб запобігти кешуванню на всіх рівнях (браузер, системний мережевий стек, проміжний проксі), сервер додає наступну тріаду заголовків до кожної відповіді:
1. `Cache-Control: no-cache, no-store, must-revalidate, max-age=0` — забороняє збереження копії відповіді на диску або у пам'яті та вимагає безумовної повторної валідації.
2. `Pragma: no-cache` — забезпечує сумісність зі старими клієнтами протоколу HTTP/1.0.
3. `Expires: 0` — встановлює термін придатності ресурсу у минулому часі.

---

### 2. Сучасні стандарти RFC 8908 та RFC 8910 (Captive-Portal API)

Окрім класичного методу перехоплення DNS та HTTP 302 редиректів, Інженерна рада інтернету (IETF) стандартизувала механізми прямої сигналізації про наявність порталу без підміни трафіку:

1. **DHCP Option 114 (RFC 8910):** DHCP-сервер мікроконтролера під час роздачі адрес у пакеті `DHCPOFFER` та `DHCPACK` може передавати додаткову опцію `114` (Captive-Portal Identification), яка містить прямий URL у форматі рядка `http://192.168.4.1/setup` або `http://192.168.4.1/api/captive-portal`.
2. **Captive-Portal JSON API (RFC 8908):** клієнт за вказаною адресою надсилає запит `GET` з заголовком `Accept: application/captive+json` та отримує статусний JSON:
   ```json
   {
     "captive": true,
     "user-portal-url": "http://192.168.4.1/setup",
     "venue-info-url": "http://192.168.4.1/api/status",
     "seconds-remaining": 300,
     "can-extend-session": false
   }
   ```

Хоча підтримка RFC 8908/8910 з'явилася в нових версіях Android 11+ та iOS 14+, класичний механізм DNS Catch-all та HTTP 302 залишається обов'язковим базовим фундаментом, оскільки сотні мільйонів застарілих клієнтських пристроїв та ноутбуків спираються виключно на аналіз невдалих зондів перевірки зв'язку.

---

### 3. Крайові випадки: DoH, DoT та HTTPS-перехоплення

Поширення технологій захищеного DNS (DNS-over-HTTPS на порту 443 та DNS-over-TLS на порту 853) ускладнює роботу класичних перехоплювачів. Якщо на смартфоні користувача увімкнено функцію «Приватний DNS» (Private DNS у налаштуваннях Android або Profile у iOS), пристрій намагається відправити DNS-запит не на локальний UDP-порт 53, а безпосередньо через шифрований TCP-канал до серверів Cloudflare (`1.1.1.1`) чи Google (`8.8.8.8`).

Оскільки мікроконтролер не має дійсного сертифіката TLS для публічних доменів шифрованого DNS, спроби підміни таких запитів призводять до помилок рукостискання (TLS Handshake Failure). Поведінка системи в таких умовах будується наступним чином:
- Мережевий стек мікроконтролера скидає спроби встановлення TCP-з'єднань на порт 853 (надсилає `TCP RST` або ігнорує пакети `SYN`).
- Після 2–3 невдалих спроб встановити DoT/DoH з'єднання мобільна операційна система автоматично переходить у резервний режим (Fallback) і надсилає стандартний відкритий UDP-запит на локальний порт 53 шлюзу `192.168.4.1`.
- Запит потрапляє в DNS Catch-all сервер, і процес відкриття порталу успішно продовжується.

---

### 4. Маршрути інтерфейсу користувача (UI Endpoints)

Ці маршрути обслуговують завантаження веб-додатка Single Page Application (SPA), упакованого у стиснений GZIP-масив у Flash-пам'яті мікроконтролера.

#### `GET /` або `GET /setup`

* **Призначення:** Віддача головної сторінки майстра первинної конфігурації.
* **Заголовки запиту від клієнта:** `Accept-Encoding: gzip, deflate` (підтримується всіма мобільними браузерами).
* **Заголовки відповіді сервера:**
  ```http
  HTTP/1.1 200 OK
  Content-Type: text/html; charset=utf-8
  Content-Encoding: gzip
  Content-Length: 4128
  Connection: close
  Cache-Control: no-cache, no-store, must-revalidate
  Pragma: no-cache
  Expires: 0
  ```
* **Тіло відповіді:** Бінарний стиснений потік `index_html_gz`, що містить розмітку HTML5, вбудовані стилі CSS3 та JavaScript логіку взаємодії з REST API.

---

### 5. Службові REST API ендпоінти

Усі динамічні операції (сканування радіоефіру, отримання стану вузла, валідація та збереження параметрів, плановий перезапуск) виконуються веб-інтерфейсом асинхронно через виклики `fetch()` до ендпоінтів `/api/*`. Обмін даними здійснюється у форматі JSON (`Content-Type: application/json`).

```
                              ┌─────────────────────────────┐
                              │     Вбудований REST API     │
                              └──────────────┬──────────────┘
                     ┌───────────────────────┼───────────────────────┐
                     ▼                       ▼                       ▼
            GET /api/scan           POST /api/save          GET /api/status
          (Список Wi-Fi мереж)    (Збереження в NVS)      (Діагностика вузла)
```

---

#### `GET /api/scan` — Сканування доступних Wi-Fi мереж

Ініціює активне або пасивне сканування радіоефіру бездротовим радіомодулем мікроконтролера та повертає список виявлених точок доступу.

* **Метод:** `GET`
* **Параметри запиту:** Немає.
* **Заголовки відповіді:**
  ```http
  HTTP/1.1 200 OK
  Content-Type: application/json; charset=utf-8
  Connection: close
  Cache-Control: no-cache, no-store, must-revalidate
  ```
* **Тіло успішної відповіді (JSON):**
  ```json
  {
    "status": "ok",
    "count": 3,
    "networks": [
      {
        "ssid": "Home_Router_2G",
        "rssi": -52,
        "auth": "WPA2_PSK",
        "channel": 6
      },
      {
        "ssid": "Office_Guest",
        "rssi": -68,
        "auth": "OPEN",
        "channel": 1
      },
      {
        "ssid": "IoT_Sensors_Net",
        "rssi": -81,
        "auth": "WPA3_PSK",
        "channel": 11
      }
    ]
  }
  ```

| Поле об'єкта `networks` | Тип | Опис та діапазон значень |
|---|---|---|
| `ssid` | String | Назва бездротової мережі (до 32 байтів). Приховані мережі відображаються як `"[Hidden]"` |
| `rssi` | Integer | Рівень сигналу в децибел-міліватах (дБм, значення від `-100` до `-30`) |
| `auth` | String | Тип автентифікації: `"OPEN"`, `"WEP"`, `"WPA_PSK"`, `"WPA2_PSK"`, `"WPA_WPA2_PSK"`, `"WPA2_ENTERPRISE"`, `"WPA3_PSK"` |
| `channel` | Integer | Номер радіоканалу Wi-Fi у діапазоні 2.4 ГГц (`1`–`13`) |

* **Коди помилок:**
  * `500 Internal Server Error` — помилка виклику апаратного драйвера Wi-Fi сканування:
    ```json
    {
      "status": "error",
      "code": "SCAN_FAILED",
      "message": "Wi-Fi scan driver timeout or radio busy"
    }
    ```

---

#### `POST /api/save` — Збереження конфігурації в NVS

Приймає облікові дані обраної Wi-Fi мережі та системні параметри пристрою для валідації та збереження у розділ Non-Volatile Storage (NVS) Flash-пам'яті.

* **Метод:** `POST`
* **Заголовки запиту:** `Content-Type: application/json`
* **Схема вхідного JSON:**
  ```json
  {
    "ssid": "Home_Router_2G",
    "password": "SecretPassword123",
    "devname": "Sensor-Node-LivingRoom",
    "dhcp": true,
    "static_ip": "",
    "netmask": "",
    "gateway": ""
  }
  ```

| Поле | Тип | Обов'язкове | Обмеження | Опис |
|---|---|---|---|---|
| `ssid` | String | Так | 1–32 байти, ASCII/UTF-8 | Назва цільової точки доступу |
| `password` | String | Ні | 0 або 8–63 байти ASCII | Пароль WPA2/WPA3 (порожній для відкритих мереж) |
| `devname` | String | Ні | 1–32 байти (латиниця, цифри, дефіс) | Мережеве ім'я хоста (mDNS/DHCP hostname) |
| `dhcp` | Boolean | Так | `true` або `false` | Режим автоматичного отримання IP-адреси |
| `static_ip` | String | Ні | IPv4 адреса (наприклад, `"192.168.1.150"`) | Обов'язкове, якщо `dhcp: false` |
| `netmask` | String | Ні | IPv4 маска (наприклад, `"255.255.255.0"`) | Обов'язкове, якщо `dhcp: false` |
| `gateway` | String | Ні | IPv4 шлюз (наприклад, `"192.168.1.1"`) | Обов'язкове, якщо `dhcp: false` |

* **Заголовки відповіді:**
  ```http
  HTTP/1.1 200 OK
  Content-Type: application/json; charset=utf-8
  Connection: close
  ```
* **Тіло успішної відповіді (JSON):**
  ```json
  {
    "status": "ok",
    "message": "Configuration successfully saved to NVS. Rebooting in 2 seconds...",
    "reboot_delay_ms": 2000
  }
  ```

* **Можливі коди помилок валідації:**
  * `400 Bad Request` — невалідні параметри у вхідному JSON (неправильна довжина SSID або некоректний формат пароля):
    ```json
    {
      "status": "error",
      "code": "INVALID_PARAM",
      "field": "password",
      "message": "WPA2 password must be between 8 and 63 ASCII characters"
    }
    ```
  * `500 Internal Server Error` — апаратна помилка збереження у Flash-пам'ять / NVS:
    ```json
    {
      "status": "error",
      "code": "NVS_WRITE_ERROR",
      "message": "Failed to commit transaction to non-volatile storage partition"
    }
    ```

---

#### `GET /api/status` — Діагностика та стан вузла

Надає базову телеметрію та системну інформацію мікроконтролера для відображення у підвалі діалогового вікна.

* **Метод:** `GET`
* **Заголовки відповіді:** `Content-Type: application/json; charset=utf-8`
* **Тіло відповіді (JSON):**
  ```json
  {
    "status": "ok",
    "chip_model": "ESP32-S3",
    "firmware_version": "v1.4.2",
    "mac_address": "C4:4F:33:1A:8B:20",
    "free_heap_bytes": 194560,
    "min_free_heap_bytes": 182300,
    "uptime_seconds": 42,
    "ap_connected_clients": 1,
    "nvs_configured": false
  }
  ```

---

#### `POST /api/reboot` — Примусове перезавантаження вузла

Ініціює плановий рестарт мікроконтролера з таймером затримки для коректного закриття мережевих сокетів та завершення активних сесій.

* **Метод:** `POST`
* **Тіло запиту (опціонально):**
  ```json
  {
    "delay_ms": 1500
  }
  ```
* **Тіло відповіді:**
  ```json
  {
    "status": "ok",
    "message": "Device will reboot in 1500 ms"
  }
  ```
