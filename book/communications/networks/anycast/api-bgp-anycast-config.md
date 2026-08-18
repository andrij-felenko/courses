# 📋 Конфігурація BGP-демонів (BIRD та ExaBGP) для Anycast VIP

Цей довідник містить вичерпну специфікацію налаштування мережевого стека Linux, детальні контракти конфігурації BGP-демонів BIRD v2 та ExaBGP для динамічного анонсування віртуальних IP-адрес (Anycast VIP `/32` та `/128`), механізми захисту від ARP-колізій у ядрі, повний протокол взаємодії з агентами перевірки працездатності (Healthcheck), правила керування трафіком через BGP Communities та процедуру планового виводу серверів на обслуговування.

---

## 1. Архітектура мережевого стека Linux: ізоляція Anycast VIP та ARP Flux

Коли кілька серверів у межах одного або кількох дата-центрів налаштовуються з однаковою IP-адресою, базовий мережевий стек операційної системи Linux стикається з фундаментальною проблемою канального рівня L2 — явищем **ARP Flux** (колізією відповідей протоколу дозволу адрес).

```
[ Клієнтський L3-комутатор ] ── ARP Who-has 198.51.100.1? ──► [ Широкомовний L2-сегмент ]
                                                                   │           │
                 ┌─────────────────────────────────────────────────┴───┐       │
                 ▼                                                     ▼       ▼
       [ Сервер 1 (eth0) ]                                   [ Сервер 2 (eth0) ]
       Відповідає: MAC1!                                     Відповідає: MAC2!
       (Хаотична зміна MAC-адреси в ARP-таблиці комутатора -> Постійний розрив трафіку)
```

За замовчуванням стек TCP/IP ядра Linux реалізує модель «слабкого хоста» (*Weak Host Model*). Якщо ядро бачить ARP-запит щодо IP-адреси, яка належить **будь-якому** локальному інтерфейсу системи (навіть інтерфейсу зворотного зв'язку `lo`), воно відповідає на цей запит через фізичний інтерфейс `eth0`, надсилаючи його апаратну MAC-адресу. Якщо 10 серверів у стійці мають однакову Anycast VIP, комутатор Top-of-Rack отримує 10 одночасних суперечливих відповідей ARP, що призводить до безперервного переписування CAM-таблиці комутатора та повної втрати зв'язку.

### Створення ізольованого інтерфейсу Dummy

Для запобігання колізіям Anycast VIP призначається не на фізичні інтерфейси і не на системний `lo` (де адреса може конфліктувати з локальними сокетами системи `127.0.0.1`), а на спеціальний віртуальний інтерфейс типу `dummy`.

```bash
# Завантаження модуля ядра Linux
modprobe dummy

# Створення виділеного Anycast-інтерфейсу dummy0
ip link add dummy0 type dummy

# Призначення віртуальних адрес Anycast (/32 для IPv4 та /128 для IPv6)
ip addr add 198.51.100.1/32 dev dummy0
ip -6 addr add 2001:db8:any::1/128 dev dummy0

# Активація інтерфейсу
ip link set dummy0 up
```

### Придушення ARP-відповідей через параметри ядра sysctl

Щоб ядро повністю ігнорувало ARP-запити щодо Anycast VIP на зовнішніх портах, у конфігурацію `/etc/sysctl.d/99-anycast.conf` вносяться обов'язкові системні параметри:

```ini
# Ігнорувати ARP-запити, якщо цільова IP не налаштована на вхідному фізичному інтерфейсі
net.ipv4.conf.all.arp_ignore = 1
net.ipv4.conf.default.arp_ignore = 1
net.ipv4.conf.dummy0.arp_ignore = 1

# Використовувати як джерело в ARP-відповідях лише первинну IP-адресу вихідного фізичного інтерфейсу
net.ipv4.conf.all.arp_announce = 2
net.ipv4.conf.default.arp_announce = 2
net.ipv4.conf.dummy0.arp_announce = 2

# Вимкнення зворотної фільтрації шляху (RPFilter) для асиметричного трафіку Anycast
net.ipv4.conf.all.rp_filter = 0
net.ipv4.conf.default.rp_filter = 0
net.ipv4.conf.eth0.rp_filter = 0
net.ipv4.conf.dummy0.rp_filter = 0
```

Застосування налаштувань виконується командою:

```bash
sysctl --system
```

Пояснення прапорців ядра:
- `arp_ignore=1`: ядро відповідає на ARP-запит лише в тому разі, якщо запитувана IP-адреса фізично сконфігурована саме на тому мережевому інтерфейсі, через який надійшов запит. Оскільки адреса `198.51.100.1` живе на `dummy0`, запити, що приходять на `eth0`, безмовно відкидаються.
- `arp_announce=2`: ядро завжди підставляє локальну адресу вихідного інтерфейсу (наприклад, реальну Unicast IP `10.0.1.10` інтерфейсу `eth0`) у поле джерела ARP-повідомлень, унеможливлюючи витік Anycast VIP у широкомовний домен.
- `rp_filter=0`: вимикає сувору перевірку зворотного шляху (*Reverse Path Filtering*), що критично для схем із прямим поверненням від сервера (DSR) або асиметричною маршрутизацією BGP.

---

## 2. Конфігураційний контракт BIRD v2

BIRD (англ. *BIRD Internet Routing Daemon*) — це галузевий стандарт маршрутизуючого програмного забезпечення для дата-центрів і точок обміну трафіком IXP. У схемі *BGP to the Host* сервер підтримує eBGP-сесії з двома надлишковими комутаторами стійки (Leaf-1 та Leaf-2) і протокол субсекундного моніторингу лінків BFD (англ. *Bidirectional Forwarding Detection*).

### Протокол BFD (RFC 5880 / RFC 5881) та субсекундна збіжність

Стандартний таймер підтримки зв'язку BGP (BGP Keepalive) становить 30 секунд, а таймер утримання маршруту (Hold Time) — 90 секунд. Якщо фізичний лінк або мережевий демон на сервері зазнає збою без повного падіння L1-сигналу порту, комутатор продовжуватиме надсилати 50% трафіку на мертвий сервер протягом півтори хвилини.

Протокол BFD вирішує цю проблему через надсилання легких контрольних мікропакетів UDP на порт `3784` з інтервалом 250 мілісекунд. Якщо 3 пакети поспіль втрачено (загальний час `3 × 250 мс = 750 мс`), BFD миттєво генерує внутрішнє переривання в BIRD, і демон розриває BGP-сесію, змушуючи комутатор стійки вилучити сервер з апаратної таблиці ECMP менш ніж за одну секунду.

### Структура конфігураційного файлу `/etc/bird/bird.conf`

```
# Глобальний ідентифікатор маршрутизатора (Unicast IP фізичного інтерфейсу)
router id 10.0.1.10;

# Журналювання подій через стандартний демон syslog
log syslog all;

# Моніторинг стану мережевих адаптерів ядра
protocol device {
    scan time 2;
}

# Імпорт Anycast VIP з інтерфейсу dummy0 у внутрішню таблицю BIRD
protocol direct anycast_vip {
    ipv4 {
        import filter {
            # Приймаємо суто наш /32 префікс Anycast
            if net = 198.51.100.1/32 then accept;
            reject;
        };
        export none;
    };
    interface "dummy0";
}

# Протокол надшвидкого виявлення збоїв каналу зв'язку BFD (RFC 5880)
protocol bfd {
    interface "eth0" {
        interval 250 ms;        # Інтервал контрольних пакетів
        multiplier 3;           # 3 пропущені пакети (750 мс) -> миттєвий обрив BGP
    };
    interface "eth1" {
        interval 250 ms;
        multiplier 3;
    };
}

# Базовий шаблон eBGP-сесії до комутаторів стійки (Leaf Switches)
template bgp leaf_switch {
    local as 65010;             # Приватний ASN поточного сервера
    neighbor as 65001;          # Приватний ASN комутатора стійки
    direct;                     # Пряме з'єднання в межах L2/L3 підмережі (TTL=1)
    bfd on;                     # Прив'язка сесії до BFD-моніторингу
    graceful restart on;        # Підтримка планового перезапуску демона

    ipv4 {
        # Сервер є кінцевою точкою сервісу і не приймає маршрути від комутатора
        import none;

        # Експорт Anycast VIP з додаванням керуючих атрибутів BGP
        export filter {
            if net = 198.51.100.1/32 then {
                # Додавання стандартної BGP Community для ідентифікації сервісу
                bgp_community.add((65001, 100));
                
                # Встановлення пріоритету виходу MED (Multi-Exit Discriminator)
                bgp_med = 10;
                
                accept;
            }
            reject;
        };
    };
}

# Активна BGP-сесія до першого комутатора стійки (Leaf-1)
protocol bgp to_leaf1 from leaf_switch {
    neighbor 10.0.1.1 as 65001;
}

# Активна BGP-сесія до другого комутатора стійки (Leaf-2)
protocol bgp to_leaf2 from leaf_switch {
    neighbor 10.0.1.2 as 65001;
}
```

### Корисні команди налагодження в інтерфейсі CLI `birdc`

Для перевірки стану BGP-сесій та анонсованих маршрутів використовується утиліта керування `birdc`:

```bash
# Перевірка статусу BGP-сусідів
birdc show protocols

# Перевірка активних BFD-сесій та виміряної затримки
birdc show bfd sessions

# Перегляд експортованих маршрутів до конкретного комутатора
birdc show route export to_leaf1

# Детальна інформація про маршрут з усіма BGP-атрибутами
birdc show route for 198.51.100.1/32 all

# Динамічне перечитування конфігурації без переривання сесій
birdc configure
```

---

## 3. Конфігурація ExaBGP та протокол взаємодії з Healthcheck

ExaBGP — це легкий BGP-рушій, розроблений компанією Exa Networks спеціально для створення програмно-визначених мереж (SDN) та динамічного балансування Anycast. На відміну від класичних демонів, ExaBGP передає повне керування маршрутами зовнішньому процесу моніторингу працездатності через стандартні потоки введення-виведення (`stdin` / `stdout`).

### Архітектура взаємодії компонентів

```
[ Веб-сервіс / Nginx (Port 443) ]
       ▲
       │ HTTP GET /healthz (кожні 1000 мс)
       │
[ Healthcheck Python Daemon ]
       │
       │ stdout: "announce route 198.51.100.1/32 next-hop self"
       ▼ (Unix IPC Pipe)
[ ExaBGP Process ] ── eBGP UPDATE ──► [ Top-of-Rack Switch (ECMP Pool) ]
```

### Файл `/etc/exabgp/exabgp.conf`

```
# Визначення зовнішнього процесу перевірки працездатності
process healthcheck-agent {
    run /usr/local/bin/anycast-healthcheck.py;
    encoder text;
}

# Шаблон сусідства для комутаторів стійки
neighbor 10.0.1.1 {
    router-id 10.0.1.10;
    local-address 10.0.1.10;
    local-as 65010;
    peer-as 65001;

    api {
        processes [ healthcheck-agent ];
    }
}

neighbor 10.0.1.2 {
    router-id 10.0.1.10;
    local-address 10.0.1.10;
    local-as 65010;
    peer-as 65001;

    api {
        processes [ healthcheck-agent ];
    }
}
```

### Специфікація команд текстового протоколу ExaBGP

Агент перевірки працездатності записує в потік `stdout` спеціальні текстові директиви, які ExaBGP негайно транслює у вихідні BGP-повідомлення `UPDATE`:

| Команда | Дія у протоколі BGP | Приклад виклику |
|---|---|---|
| `announce route <prefix> next-hop self` | Надсилає BGP UPDATE про доступність префікса. Комутатор додає сервер до ECMP-пулу. | `announce route 198.51.100.1/32 next-hop self` |
| `withdraw route <prefix>` | Надсилає BGP UPDATE з полями *Withdrawn Routes*. Комутатор негайно вилучає сервер із пулу. | `withdraw route 198.51.100.1/32` |
| `announce route ... as-path [ ... ]` | Оголошує префікс зі штучним подовженням AS-Path (Prepending) для плавної деградації. | `announce route 198.51.100.1/32 next-hop self as-path [ 65010 65010 ]` |
| `announce route ... community [ ... ]` | Додає числові мітки BGP Communities для керування політикою маршрутизації. | `announce route 198.51.100.1/32 next-hop self community [ 65535:65281 ]` |

---

## 4. Еталонний скрипт перевірки працездатності (Healthcheck Agent)

Нижче наведено повнофункціональний скрипт `/usr/local/bin/anycast-healthcheck.py`, який реалізує кінцевий автомат моніторингу, захист від брязкоту стану (*Flapping Damping*) та плавне зняття навантаження (*Graceful Shutdown*).

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Агент перевірки працездатності для Anycast VIP через ExaBGP.
Вимоги: Python 3.8+
"""
import sys
import time
import signal
import urllib.request

VIP_PREFIX = "198.51.100.1/32"
HEALTH_URL = "http://127.0.0.1:8080/healthz"
CHECK_INTERVAL_SEC = 1.0
TIMEOUT_SEC = 0.5
RISE_THRESHOLD = 3   # Кількість успіхів поспіль для переходу в UP
FALL_THRESHOLD = 2   # Кількість помилок поспіль для переходу в DOWN

class AnycastHealthchecker:
    def __init__(self):
        self.state = "INIT"
        self.consecutive_successes = 0
        self.consecutive_failures = 0
        self.running = True

        # Коректне завершення роботи при отриманні сигналів SIGTERM/SIGINT
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        self.running = False
        self._withdraw()
        sys.exit(0)

    def _announce(self):
        sys.stdout.write(f"announce route {VIP_PREFIX} next-hop self\n")
        sys.stdout.flush()

    def _withdraw(self):
        sys.stdout.write(f"withdraw route {VIP_PREFIX}\n")
        sys.stdout.flush()

    def _check_service(self) -> bool:
        try:
            req = urllib.request.Request(HEALTH_URL, headers={"User-Agent": "Anycast-Probe/1.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
                return resp.status == 200
        except Exception:
            return False

    def run(self):
        while self.running:
            is_healthy = self._check_service()

            if is_healthy:
                self.consecutive_failures = 0
                self.consecutive_successes += 1
                if self.consecutive_successes >= RISE_THRESHOLD and self.state != "UP":
                    self.state = "UP"
                    self._announce()
            else:
                self.consecutive_successes = 0
                self.consecutive_failures += 1
                if self.consecutive_failures >= FALL_THRESHOLD and self.state != "DOWN":
                    self.state = "DOWN"
                    self._withdraw()

            time.sleep(CHECK_INTERVAL_SEC)

if __name__ == "__main__":
    checker = AnycastHealthchecker()
    checker.run()
```

### Механіка захисту від брязкоту стану (Flapping Damping)

Коли бекенд зазнає перевантаження (наприклад, утилізація CPU сягає 100%), час відповіді ендпоінта `/healthz` починає коливатися біля порогу таймауту. Без фільтрації агент генерував би команди `announce` та `withdraw` щосекунди.

Це викликає катастрофічний стан брязкоту (Route Flapping) на комутаторі стійки: комутатор безперервно скидає апаратні групи ECMP і перераховує хеш-таблиці ASIC, що призводить до падіння продуктивності всього дата-центру.

Конфігурація `RISE_THRESHOLD = 3` та `FALL_THRESHOLD = 2` реалізує гістерезис: сервіс вважається відновленим лише після 3 успішних перевірок поспіль (3 секунди стабільності), а вимикається після 2 послідовних збоїв.

---

## 5. Довідник стандартних BGP Communities для Traffic Engineering

Під час анонсування префіксів Anycast мережевий інженер може передавати стандартні та призначені для користувача мітки BGP Communities:

### Стандартні загальновідомі мітки (Well-Known Communities за RFC 1997 / RFC 8326)

1. **`65535:65281` (`NO_EXPORT`):** маршрутизатор провайдера, отримавши префікс із цією міткою, зобов'язаний обслуговувати його локально й категорично не передавати за межі своєї автономної системи. Це ідеально підходить для розгортання локальних Anycast-вузлів DNS у точках обміну трафіком IXP без ризику стягнути трафік сусідніх країн.
2. **`65535:65282` (`NO_ADVERTISE`):** маршрутизатор не передає маршрут жодному іншому BGP-піру (навіть усередині тієї самої автономної системи).
3. **`65535:0` (`GRACEFUL_SHUTDOWN`, RFC 8326):** сигналізує транзитним вузлам про плановий вивід сервера з експлуатації. Провайдери автоматично виставляють такому маршруту найнижчий локальний пріоритет `LOCAL_PREF=0`, що змушує клієнтські сесії плавно перетекти на сусідні PoP без миттєвого обриву з'єднань.

### Типові приватні мітки керування трафіком у мережах Tier-1 провайдерів

| Шаблон Community | Дія в магістральній мережі оператора (Tier-1 ISP) |
|---|---|
| `<ISP_ASN>:100` | Встановити максимальний локальний пріоритет `LOCAL_PREF = 100` (основний PoP). |
| `<ISP_ASN>:70` | Встановити знижений `LOCAL_PREF = 70` для зняття пікового навантаження. |
| `<ISP_ASN>:0` | Заборонити анонс префікса у певний географічний регіон (наприклад, у Північну Америку). |
| `<ISP_ASN>:pre_1` | Дописати один ASN до `AS_PATH` на зовнішніх транзитних стиках провайдера. |

---

## 6. Регламент планового обслуговування (Zero-Downtime Drain Procedure)

Для виведення Anycast-сервера на оновлення операційної системи або заміну обладнання без втрати активних TCP-сесій застосовується триетапний регламент плавного дренажу трафіку (*Traffic Draining*):

1. **Етап 1 (Попереднє попередження, Graceful Shutdown):**
   Агент перевірки виставляє BGP Community `65535:0` (`GRACEFUL_SHUTDOWN`) або збільшує AS-Path Prepending на 3 хопи:
   ```
   announce route 198.51.100.1/32 next-hop self community [ 65535:0 ]
   ```
   Усі нові TCP-з'єднання починають відкриватися на сусідніх балансувальниках або в сусідніх дата-центрах.
2. **Етап 2 (Очікування завершення активних сесій, Drain Timeout):**
   Сервер продовжує обробляти активні з'єднання протягом встановленого таймауту (зазвичай 60–120 секунд для веб-сервісів HTTP/HTTPS). Кількість відкритих сокетів відстежується через `ss -s` або метрики Nginx/Envoy `active_connections`.
3. **Етап 3 (Повне зняття маршруту, BGP Withdraw):**
   Коли кількість активних сесій знижується до нуля, виконується фінальне зняття анонсу:
   ```
   withdraw route 198.51.100.1/32
   ```
   Після цього сервер повністю ізольований від мережевого трафіку і може бути безпечно перезавантажений або зупинений.
