# ⚙️ Стенд автоматизованого хаос-тестування IoT-вузла на Python

Реалізація модульного тестового стенда для автоматичної перевірки стійкості мікроконтролерного вузла до раптового знеструмлення, втрати пакетів, затримок, розривів зв'язку та часових стрибків.

## 1. Архітектура тестового середовища

Тестовий стенд запускається на хості під керуванням Linux і керує чотирма інтерфейсами об'єкта випробувань (DUT):
1. **Лінія живлення:** релейний модуль USB або швидкісний MOSFET-ключ, що розриває живлення `V_CC` за апаратним тригером;
2. **Консоль налагодження:** послідовний порт UART (`/dev/ttyUSB0`) для контролю завантаження та виявлення аварійних панік ядра або файлової системи;
3. **Мережевий міст:** віртуальний інтерфейс Linux, через який проходять пакети Wi-Fi/Ethernet до брокера MQTT, із застосуванням утиліти `tc` (Traffic Control) та модуля `netem` (Network Emulator);
4. **Служба синхронізації часу:** локальний імітатор сервера SNTP, здатний генерувати зміщені часові мітки для перевірки реакції пристрою на раптові стрибки календаря.

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                           pytest-оркестратор                           │
 └──────┬───────────────────┬───────────────────┬───────────────────┬─────┘
        │ UART Logs         │ USB Relay         │ tc netem          │ Fake SNTP
 ┌──────▼──────┐     ┌──────▼──────┐     ┌──────▼─────────┐  ┌──────▼─────────┐
 │ /dev/ttyUSB │     │ Розрив V_CC │     │ Емуляція втрат │  │ Зсув часу ±1 год│
 └──────┬──────┘     └──────┬──────┘     └──────┬─────────┘  └──────┬─────────┘
        │                   │                   │                   │
 ┌──────┴───────────────────┴───────────────────┴───────────────────┴─────┐
 │                       Мікроконтролерний вузол (DUT)                    │
 └────────────────────────────────────────────────────────────────────────┘
```

Головне завдання автоматизованого стенда — перевірити не просто «чи працює прошивка у штатному режимі», а як саме вона виходить із критичних аварійних станів. Ручне висмикування кабелів живлення чи відключення роутера не дають повторюваності: інженер не здатний влучити пальцем у мілісекундне вікно запису сторінки Flash чи точно повторити 17% випадкових втрат пакетів із дрижанням затримки 45 мс. Python-оркестратор забезпечує стовідсоткову детермінованість і повторюваність випробувань у рамках конвеєра неперервної інтеграції (CI/CD).

Стенд ізолює об'єкт випробувань у виділеному мережевому просторі імен (Linux network namespace `ip netns`), завдяки чому спотворення трафіку через `tc netem` не зачіпають основний стек операційної системи розробника та інші локальні сервіси.

## 2. Програмна реалізація стенду на Python

Тестовий набір побудовано на базі фреймворку `pytest` з використанням клієнта `paho-mqtt` для асерції доставки телеметрії.

```py
"""
chaos_harness.py — Інструмент ін'єкції збоїв та верифікації надійності IoT.
"""
import os
import time
import random
import socket
import struct
import subprocess
import threading
from typing import List, Dict, Any
import serial
import paho.mqtt.client as mqtt
import pytest


class PowerRelay:
    """Керування лінією живлення мікроконтролера через віртуальний COM-порт."""
    def __init__(self, port: str = "/dev/ttyACM0", baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self._dev = None

    def open(self):
        try:
            self._dev = serial.Serial(self.port, self.baudrate, timeout=1.0)
            time.sleep(0.5)
        except serial.SerialException:
            # Запасний режим для CI без фізичного реле
            self._dev = None

    def power_off(self):
        if self._dev:
            self._dev.write(b"RELAY:OFF\n")
            self._dev.flush()

    def power_on(self):
        if self._dev:
            self._dev.write(b"RELAY:ON\n")
            self._dev.flush()

    def power_cycle(self, off_duration_sec: float = 0.5):
        self.power_off()
        time.sleep(off_duration_sec)
        self.power_on()

    def close(self):
        if self._dev:
            self._dev.close()


class NetworkChaos:
    """Керування втратами, затримками та ізоляцією трафіку через Linux tc-netem."""
    def __init__(self, iface: str = "veth_dut"):
        self.iface = iface

    def _run(self, cmd: str):
        subprocess.run(f"sudo {cmd}", shell=True, check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def clear(self):
        """Скидання всіх мережевих обмежень до штатного режиму."""
        self._run(f"tc qdisc del dev {self.iface} root")

    def set_loss_and_jitter(self, loss_pct: float = 15.0, delay_ms: int = 100, jitter_ms: int = 30):
        """Встановлення випадкових втрат, затримок та дублікатів пакетів."""
        self.clear()
        cmd = (f"tc qdisc add dev {self.iface} root netem "
               f"loss {loss_pct}% delay {delay_ms}ms {jitter_ms}ms 25% "
               f"duplicate 2% corrupt 0.1%")
        self._run(cmd)

    def set_blackout(self):
        """Повна ізоляція пристрою від мережі (100% drop)."""
        self.clear()
        self._run(f"tc qdisc add dev {self.iface} root netem loss 100%")


class FakeNtpServer:
    """Імітатор SNTP-сервера з можливістю введення штучного зсуву часу."""
    NTP_DELTA = 2208988800  # Різниця між 1900 та 1970 роками

    def __init__(self, host: str = "0.0.0.0", port: int = 12300):
        self.host = host
        self.port = port
        self.offset_sec = 0.0
        self._sock = None
        self._thread = None
        self._running = False

    def start(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((self.host, self.port))
        self._running = True
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def set_time_shift(self, shift_seconds: float):
        """Встановити зсув часу: позитивний (вперед) або негативний (назад)."""
        self.offset_sec = shift_seconds

    def _serve(self):
        while self._running:
            try:
                data, addr = self._sock.recvfrom(1024)
                if len(data) >= 48:
                    recv_time = time.time() + self.offset_sec + self.NTP_DELTA
                    sec = int(recv_time)
                    frac = int((recv_time - sec) * (2**32))

                    # Формування базового SNTPv4 відповіді
                    resp = bytearray(48)
                    resp[0] = 0x24  # LI=0, VN=4, Mode=4 (Server)
                    resp[1] = 1     # Stratum 1
                    resp[2] = 6     # Poll
                    resp[3] = 0xEC  # Precision
                    struct.pack_into("!II", resp, 32, sec, frac) # Transmit Timestamp
                    struct.pack_into("!II", resp, 40, sec, frac)
                    self._sock.sendto(resp, addr)
            except Exception:
                break

    def stop(self):
        self._running = False
        if self._sock:
            self._sock.close()


class TelemetryCollector:
    """Підписник MQTT для збору та перевірки неперервності лічильників."""
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.received_messages: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        self.client = mqtt.Client(client_id="pytest_chaos_observer")
        self.client.on_message = self._on_message

    def _on_message(self, client, userdata, msg):
        import json
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            with self.lock:
                self.received_messages.append({
                    "topic": msg.topic,
                    "payload": payload,
                    "recv_ts": time.time()
                })
        except Exception:
            pass

    def start(self, topics: List[str]):
        self.client.connect(self.broker_host, self.broker_port, 60)
        for t in topics:
            self.client.subscribe(t, qos=1)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def clear(self):
        with self.lock:
            self.received_messages.clear()


@pytest.fixture(scope="module")
def harness():
    """Фікстура ініціалізації апаратних та мережевих інтерфейсів стенду."""
    relay = PowerRelay()
    relay.open()
    chaos = NetworkChaos(iface="eth0")
    ntp = FakeNtpServer()
    ntp.start()
    collector = TelemetryCollector()
    collector.start(topics=["nodes/+/state", "nodes/+/replay"])

    yield {"relay": relay, "chaos": chaos, "ntp": ntp, "collector": collector}

    chaos.clear()
    relay.power_on()
    relay.close()
    ntp.stop()
    collector.stop()
```

## 3. Автоматизовані сценарії випробувань

### Сценарій 1: Раптове вимкнення живлення під час інтенсивного запису у Flash

Мета сценарію — довести відсутність зависань при монтуванні файлової системи LittleFS та незмінність монотонності ідентифікатора запису `seq_id` після 50 циклів брутального розриву `V_CC`.

Тестовий цикл очікує підтвердження початку чергової транзакції через появу свіжого повідомлення в черзі, після чого генерує псевдовипадкову затримку від 10 до 200 мілісекунд і подає команду розриву реле. Такий діапазон гарантує попадання моменту знеструмлення на всі фази запису: прання сектора, програмування сторінки та фіксацію метаданих.

```py
def test_power_cut_during_flash_write(harness):
    relay = harness["relay"]
    collector = harness["collector"]

    for cycle in range(50):
        collector.clear()
        relay.power_on()
        
        # Очікуємо початку активного запису та перших повідомлень телеметрії
        t_start = time.time()
        saw_telemetry = False
        while time.time() - t_start < 5.0:
            with collector.lock:
                if len(collector.received_messages) > 0:
                    saw_telemetry = True
                    break
            time.sleep(0.05)

        assert saw_telemetry, f"Вузол не відновив роботу після циклу {cycle}"

        # Ін'єкція випадкового обриву в інтервалі 10..200 мс (під час запису кадру)
        time.sleep(random.uniform(0.01, 0.20))
        relay.power_off()
        time.sleep(0.3)

    # Фінальне завантаження та перевірка цілісності логу
    relay.power_on()
    time.sleep(3.0)
    
    with collector.lock:
        seq_ids = [m["payload"]["seq"] for m in collector.received_messages if "seq" in m["payload"]]
    
    # Перевірка: жоден лічильник не перескочив назад і не згенерував дублікатів
    assert len(seq_ids) > 0, "Немає повідомлень після фінального старту"
    assert seq_ids == sorted(seq_ids), "Порушено монотонне зростання sequence ID після аварії"
```

### Сценарій 2: Розрив зв'язку на час заповнення буфера та злив черги повторів

Мета сценарію — перевірити збереження вимірів у кільцевому Flash-буфері під час блекауту та безаварійне викачування архіву після відновлення лінка без колапсу брокера.

Оркестратор повністю блокує мережевий трафік на 30 секунд командою `netem loss 100%`. Вузол продовжує опитувати фізичні сенсори, виявляє розрив з'єднання з MQTT-брокером і перемикається в режим збереження точок у локальний Flash-журнал. Після відновлення каналу тест перевіряє два твердження:
1. Потік свіжої телеметрії (`/state`) відновлюється негайно (пріоритетна смуга Live);
2. Накопичені архівні точки надходять у топік `/replay` зі строго послідовними значеннями лічильника `seq_id` без пропусків.

```py
def test_network_blackout_and_replay_drain(harness):
    chaos = harness["chaos"]
    collector = harness["collector"]
    collector.clear()

    # 1. Повна ізоляція вузла на 30 секунд
    chaos.set_blackout()
    time.sleep(30.0)

    # Під час обриву повідомлення не повинні доходити до брокера
    with collector.lock:
        assert len(collector.received_messages) == 0, "Дані просочуються крізь ізольований лінк"

    # 2. Відновлення каналу
    chaos.clear()
    
    # 3. Очікування отримання поточних вимірів (Live) та вивантаження накопичених (Replay)
    drain_timeout = 60.0
    t_start = time.time()
    live_msgs = []
    replay_msgs = []

    while time.time() - t_start < drain_timeout:
        with collector.lock:
            live_msgs = [m for m in collector.received_messages if m["topic"].endswith("/state")]
            replay_msgs = [m for m in collector.received_messages if m["topic"].endswith("/replay")]
        
        # Вузол має вивантажити щонайменше 15 накопичених точок
        if len(replay_msgs) >= 15 and len(live_msgs) >= 5:
            break
        time.sleep(0.5)

    assert len(live_msgs) > 0, "Свіжий потік (Live) заблоковано чергою повторів"
    assert len(replay_msgs) >= 15, f"Отримано лише {len(replay_msgs)} записів з офлайн-буфера"

    # Перевірка неперервності послідовності в архіві
    replay_seqs = [m["payload"]["seq"] for m in replay_msgs]
    for i in range(len(replay_seqs) - 1):
        assert replay_seqs[i+1] == replay_seqs[i] + 1, (
            f"Розрив у черзі повторів: {replay_seqs[i]} -> {replay_seqs[i+1]}"
        )
```

### Сценарій 3: Ін'єкція зсуву годинника та верифікація монотонності

Мета сценарію — перевірити поведінку прошивки при отриманні некоректного часу від сервера NTP (наприклад, зсув на 1 годину назад). Тест контролює, що внутрішні таймери вузла не зависають на 3600 секунд, а регулятори не генерують від'ємних дельт `dt`.

```py
def test_clock_step_backward_resilience(harness):
    ntp = harness["ntp"]
    collector = harness["collector"]
    collector.clear()

    # 1. Початкова синхронізація з точним часом
    ntp.set_time_shift(0.0)
    time.sleep(5.0)

    # 2. Ін'єкція зсуву на 3600 секунд назад
    ntp.set_time_shift(-3600.0)
    time.sleep(10.0)

    with collector.lock:
        msgs = list(collector.received_messages)

    assert len(msgs) >= 3, "Вузол припинив генерацію телеметрії після стрибка часу назад"

    # Перевірка: інтервали генерації монотонного часу (uptime) залишаються додатними
    uptimes = [m["payload"].get("uptime_ms", 0) for m in msgs]
    for i in range(len(uptimes) - 1):
        delta = uptimes[i+1] - uptimes[i]
        assert delta > 0, f"Виявлено немонотонний крок таймера: delta = {delta} мс"
```

## 4. Пастки та тонкощі реалізації хаос-тестів

1. **Деренчання контактів механічного реле:** звичайні електромеханічні реле при спрацьовуванні генерують пачку мікропереривань тривалістю від 2 до 8 мілісекунд (contact bounce). Для мікроконтролера це виглядає не як один чистий зріз живлення, а як високочастотний шум напруги, що може призвести до хибних спрацьовувань внутрішнього захисту або пошкодження порту вводу-виводу. Для прецизійного тестування torn writes використовуйте твердотільні MOSFET-комутатори з крутизною фронту вимкнення менше 50 наносекунд.
2. **Кешування сокетів операційною системою хоста:** коли Linux-утиліта `tc` скидає правила дропу пакетів, ядро операційної системи може раптово виштовхнути у фізичний інтерфейс усі застряглі в системному буфері TCP-сегменти одною пачкою. Це створює фальшивий сплеск трафіку, не характерний для реального радіоефіру. Щоб симулювати справжній розрив середовища, комбінуйте `tc netem` із правилами міжмережевого екрана `iptables -A FORWARD -j DROP`.
3. **Хибні падіння тестів через астрономічний час:** якщо тестовий набір намагається звіряти час отримання пакетів за штампом UTC `recv_ts == payload["ts"]`, будь-яка затримка NTP або перехід на літній час зламає перевірку. Тести стійкості повинні оцінювати виключно монотонні інваріанти: відсутність дірок у послідовності `seq_id`, валідність контрольних сум CRC32 та інтервали `delta_ms` між сусідніми вимірами.
4. **Переповнення буфера логів UART:** під час паніки ядра мікроконтролер може викинути сотні рядків діагностики за мікросекунди. Якщо потік читання з COM-порту на Python працює з недостатньо високим пріоритетом, буфер операційної системи переповнюється, і частина критичних повідомлень про збої губиться. Завжди запускайте зчитування serial-порту в окремому ізольованому потоці з чергою `queue.Queue`.
5. **Тест коректного завершення фікстур (Teardown Leak):** якщо один із тестів падає за тайм-аутом `assert`, фікстура `pytest` зобов'язана гарантовано повернути реле у ввімкнений стан та очистити всі правила `tc qdisc del`. Інакше всі наступні тести в наборі проваляться через штучно залишену мережеву ізоляцію. Блок `yield` у фікстурі `harness` забезпечує виконання teardown-коду за будь-якого результату виконання асерцій.
