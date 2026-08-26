# Стенд протоколу: емулятор, фазинг, тест сумісності

<preknowlist>
- [Свій кадр між двома платами](root:embedded/svii-kadr-mizh-dvoma-platamy) — проєктування власного кадру, маркери початку, поля довжини та контрольні суми.
- [Версія протоколу](root:embedded/versiia-protokolu) — правила еволюції двійкових структур, пряма й зворотна сумісність, прапорці розширення.
- [Підтвердження й повтор: ARQ](root:embedded/pidtverdzhennia-i-povtor) — механізми надійного доставляння, тайм-аути квитанцій і віконні протоколи.
- [Контрольна сума і CRC](root:com-modulation/crc) — алгоритми виявлення спотворень байтів у фізичному середовищі передачі.
- [Кадрування: маркер, стафінг, COBS, SLIP](root:com-transport/cobs-framing) — виділення меж пакетів у безперервному потоці байтів без помилкових спрацювань.
- [Таймаут як частина протоколу](root:sf-distributed/timeouts-deadlines) — обробка затримок, відступ і виявлення обриву зв'язку.
</preknowlist>

Коли дві налагоджувальні плати з'єднані півметровим дротом UART на столі інженера, будь-який протокол зв'язку здається бездоганним. Пакети надходять зі стабільною затримкою 2 мілісекунди, контрольні суми сходяться у 100% випадків, а буфери ніколи не переповнюються. Але коли ту саму прошивку завантажують у партію з п'яти тисяч польових промислових контролерів, система стикається з реальною фізикою: електромагнітні наведенки від пускачів двигунів спотворюють окремі біти в заголовках, радіомодеми RS-485 або LoRa втрачають пачки по 10 пакетів поспіль через інтерференцію, а мережевий шлюз раптово отримує шквал із сотень одночасних запитів після відновлення електроживлення на підстанції.

У таких умовах польові мікроконтролери починають масово зависати в нескінченних циклах розбору пошкодженого кадру, скидати пам'ять через апаратні винятки `HardFault` при невирівняному читанні зміщених полів, або переповнювати черги повторних відправок (ARQ), перетворюючи цілу мережу на заблокований розподілений затор. Знайти такі дефекти ручним тестуванням або звичайними модульними тестами на стаціонарних даних неможливо: простір комбінацій пошкоджених байтів, плаваючих затримок і черговості подій перевищує мільярди варіантів.

Єдиний інженерний спосіб гарантувати безвідмовність зв'язку — побудова **автоматизованого випробувального стенду протоколу (Protocol Testbed)**. Такий стенд ізолює логіку протоколу від фізичного заліза, моделює всі можливі аномалії каналу (ін'єкція збоїв), піддає парсери агресивному фазингу мільйонами мутованих пакетів і автоматично верифікує сумісність різних релізів прошивок у конвеєрі неперервної інтеграції (CI/CD).

## Архітектура випробувального стенду протоколу

Випробувальний стенд — це програмно-апаратний комплекс, який стає посередником між тестованим пристроєм (*Device Under Test*, DUT) та зовнішнім світом. Замість підключення до реального промислового датчика чи хмарного сервера, тестована прошивка підключається до керованого тестового середовища, яке здатне детерміновано керувати часом, затримками та кожним окремим байтом у каналі.

![Архітектура випробувального стенду протоколу](/root/course/embedded/stend-protokolu/img/protocol-testbed-architecture.svg)
*Ізольоване середовище тестування протоколу: оркестратор сценаріїв на Python, проміжний ін'єктор несправностей та тестований вузол прошивки (нативний бінарник або HIL-плата).*

Стенд складається з чотирьох ключових рівнів:

1. **Тестовий оркестратор (Test Orchestrator)**: Керуюча програма (зазвичай на Python на базі фреймворку `pytest`), що запускає тестові сценарії, генерує бінарні транзакції, контролює проксі-канал і перевіряє дотримання інваріантів протоколу (наприклад: «після відправки запиту `0x01` відповідь `0x81` зобов'язана надійти не пізніше ніж через 50 мс»).
2. **Керований проксі-ін'єктор завад (Fault Injection Proxy)**: Програмний міст, через який проходять усі байти між оркестратором та тестованим пристроєм. Проксі може прозоро пропускати дані, спотворювати окремі біти, затримувати кадри, відкидати пакети або змінювати їхню черговість.
3. **Емулятор вузлів / сервера (Peer Mock)**: Програмна модель віддаленої сторони, здатна симулювати як нормальну поведінку сервера, так і девіантну (надсилання некоректних кодів помилок, замовкання на середині сесії, відповіді з непідтримуваними номерами версій).
4. **Тестований об'єкт (DUT)**: Виконуваний код протокольного стека, запущений в одному з двох режимів:
   - **Host-Native Build (POSIX/Windows бінарник)**: Код протоколу компілюється нативним компілятором GCC або Clang для x86/x64 або ARM хост-машини. Введення/виведення UART/SPI підміняється на сокети `TCP/UDP`, `UNIX domain sockets` або віртуальні COM-порти (`PTY` у Linux або `com0com` у Windows).
   - **Hardware-in-the-Loop (HIL)**: Реальна плата мікроконтролера, підключена до стендового ПК через міст USB-UART, USB-CAN або адаптер Ethernet.

### Переваги компіляції прошивки під хост (Host-Native Testing)

Хоча тестування на реальному залізі (HIL) необхідне на фінальній стадії для перевірки апаратних таймінгів драйверів, понад 90% логічних дефектів та вразливостей пам'яті значно ефективніше знаходити у нативній хост-збірці:

- **Швидкодія**: Обмін даними через пам'ять або локальні сокети на процесорі хоста сягає 50 000 – 200 000 пакетів на секунду, тоді як фізичний UART на швидкості 115 200 біт/с обмежений фізичною стелею близько 500–800 невеликих пакетів на секунду.
- **Динамічні санітайзери пам'яті**: Компіляція за допомогою Clang із прапорцями `-fsanitize=address,undefined` дозволяє миттєво спіймати вихід за межі масиву на 1 байт або читання неініціалізованої пам'яті в момент виконання інструкції, доки помилка не затерла сусідні структури.
- **Детермінізм віртуального часу**: Стенд може прискорювати або зупиняти віртуальний годинник прошивки, перевіряючи таймаути тривалістю в години за частки секунди.

### Інтерфейси віртуального транспорту для прошивки

Під час портування коду зв'язку з мікроконтролера на хост-комп'ютер апаратні виклики периферії ізолюються за допомогою абстрактного інтерфейсу драйвера каналу (*Hardware Abstraction Layer*). Для передачі байтів на хості використовуються три стандартні транспортні механізми:

1. **Віртуальні послідовні порти (PTY / Pseudo-terminals)**:
   У системі Linux створюється пара віртуальних терміналів `/dev/pts/X`. Тестована прошивка відкриває свій кінець як звичайний файл пристрою POSIX (`open`, `read`, `write`), а тестовий стенд підключається до іншого кінця, повністю імітуючи поведінку фізичного контролера UART.
2. **Віртуальна шина CAN (Linux SocketCAN `vcan0`)**:
   Для автомобільних та промислових протоколів ядро Linux надає драйвер `vcan`. Прошивка взаємодіє з віртуальною шиною через стандартний інтерфейс сокетів `AF_CAN`, що дозволяє запускати десятки незалежних вузлів на одній машині без жодного фізичного трансивера CAN.
3. **Локальні UNIX Domain сокети або TCP-петля (Loopback `127.0.0.1`)**:
   Найшвидший варіант для високонавантажених стрес-тестів та фазингу, що забезпечує прямий обмін блоками пам'яті між процесами.

## Ін'єкція аномалій у канал зв'язку (Fault Injection Engine)

У реальних лініях зв'язку помилки не виникають рівномірно. Одиночний імпульс завади від зварювального апарата або іскріння щіток колекторного мотора здатний знищити послідовність із 5–15 байтів, тоді як наступні 10 секунд лінія працює ідеально.

Щоб протокольний стенд створював адекватне навантаження, двигун ін'єкції несправностей повинен підтримувати три класи моделей.

![Конвеєр ін'єкції несправностей каналу зв'язку](/root/course/embedded/stend-protokolu/img/fault-injection-pipeline.svg)
*Етапи спотворення каналу: марковська модель втрат пачок, побітові мутації полів кадру та черга з гаусовим джитером і перестановкою повідомлень.*

### 1. Моделі втрати пакетів (Packet Loss Models)

- **Бернуллівська модель (Uniform Random Drop)**: Кожен пакет відкидається незалежно з фіксованою ймовірністю `p` (наприклад, `p = 0.05` для 5% втрат). Підходить для базового тестування таймаутів, але не відтворює затяжні обриви зв'язку.
- **Модель Гілберта-Елліотта (Gilbert-Elliott Markov Model)**: Двостанова марковська модель, яка чергує гарний стан каналу (**Good**) та стан пачки завад (**Bad**):
  - У стані **Good** ймовірність втрати пакета мізерна (наприклад, `P_G = 0.001`).
  - У стані **Bad** ймовірність втрати висока (наприклад, `P_B = 0.85`).
  - Переходи між станами задаються ймовірностями `P(G → B) = r` та `P(B → G) = q`.

Середня тривалість перебування каналу в стані аварійної пачки завад становить:

```
Burst_Length = 1 / q   [середня кількість пакетів у стані завади]
```

Стаціонарна ймовірність того, що канал перебуває у стані пачки завад, розраховується як:

```
P_bad_state = r / (r + q)   [частка часу каналу в аварійному стані]
```

Це дозволяє точно налаштувати стенд на моделювання проїзду пристрою під мостом, завад від реле або тимчасового затінення антени перешкодою.

### 2. Моделі спотворення байтів і бітів (Corruption Models)

- **Одиночний переворот біта (Single Bitflip)**: Інверсія випадкового біта в тілі кадру за допомогою операції XOR:
  
:::tabs
```c
/* Інверсія випадкового біта в C */
void inject_bitflip(uint8_t *buffer, size_t len) {
    if (len == 0) return;
    size_t byte_idx = (size_t)rand() % len;
    uint8_t bit_idx = (uint8_t)(rand() % 8);
    buffer[byte_idx] ^= (1U << bit_idx);
}
```
```cpp
/* Індіоматична інверсія біта в C++ */
void inject_bitflip(std::span<uint8_t> buffer) noexcept {
    if (buffer.empty()) return;
    const size_t byte_idx = static_cast<size_t>(std::rand()) % buffer.size();
    const uint8_t bit_idx = static_cast<uint8_t>(std::rand() % 8);
    buffer[byte_idx] ^= static_cast<uint8_t>(1U << bit_idx);
}
```
:::

  Тестує здатність алгоритму CRC-16 або CRC-32 виявляти поодинокі спотворення.
- **Псування поля довжини (Length Tampering)**: Заміна поля `payload_len` на 0, на максимально можливе `0xFF`, або на значення, більше за фактичний розмір буфера. Перевіряє, чи не призведе це до переповнення буфера або виходу покажчика парсера за межі виділеної пам'яті.
- **Обрізання кадру (Packet Truncation)**: Відкидання другої половини пакета разом із CRC. Перевіряє поведінку автомата станів кадрувальника: чи не зависне він в очікуванні кінця повідомлення, блокуючи наступні кадри.
- **Склеювання потоків (Stream Glitching)**: Передача двох валідних кадрів підряд без паузи або з випадковим «сміттям» між ними. Перевіряє коректність ресинхронізації парсера за маркером початку.

### 3. Таймінгові спотворення: джитер і перестановка (Jitter & Reordering)

- **Гаусовий джитер**: Додавання випадкової затримки `t_delay = t_base + N(μ, σ²)`, де `μ` — середня затримка лінії, а `σ` — середньоквадратичне відхилення.
- **Перестановка пакетів (Packet Reordering)**: Пакет затримується в буфері черги, доки наступний за ним пакет відправляється вперед. Це провокує ситуації, коли старий пакет телеметрії приходить після нового, перевіряючи алгоритми обробки порядкових номерів (`sequence number`).

### Реалізація асинхронного ін'єктора несправностей

Розгляньмо практичну реалізацію проксі-каналу на Python з використанням бібліотеки `asyncio`, який приймає пакети від тестового раннера, піддає їх завадам та транслює в сокет тестованої прошивки.

```python
import asyncio
import random
import struct
from typing import Optional

class FaultInjectorConfig:
    def __init__(self):
        self.drop_prob: float = 0.05            # Ймовірність втрати пакета (0..1)
        self.bitflip_prob: float = 0.03         # Ймовірність спотворення біта
        self.min_delay_ms: float = 5.0          # Мінімальна затримка каналу
        self.max_delay_ms: float = 45.0         # Максимальна затримка каналу
        self.reorder_prob: float = 0.02         # Ймовірність затримки для перестановки
        self.truncate_prob: float = 0.01        # Ймовірність обрізання пакета

class FaultInjectionProxy:
    def __init__(self, config: FaultInjectorConfig):
        self.cfg = config
        self._reorder_buffer: Optional[bytes] = None

    def mutate_packet(self, data: bytes) -> Optional[bytes]:
        """Застосовує правила мутації до вхідного двійкового кадру."""
        if not data:
            return data

        # 1. Перевірка на втрату пакета (Drop)
        if random.random() < self.cfg.drop_prob:
            return None

        packet = bytearray(data)

        # 2. Обрізання пакета (Truncation)
        if len(packet) > 4 and random.random() < self.cfg.truncate_prob:
            cut_point = random.randint(2, len(packet) - 1)
            packet = packet[:cut_point]
            return bytes(packet)

        # 3. Спотворення випадкового біта (Bitflip)
        if random.random() < self.cfg.bitflip_prob:
            byte_idx = random.randint(0, len(packet) - 1)
            bit_idx = random.randint(0, 7)
            packet[byte_idx] ^= (1 << bit_idx)

        return bytes(packet)

    async def forward_stream(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Асинхронно зчитує кадри, застосовує затримки та відправляє адресату."""
        while not reader.at_eof():
            try:
                # Зчитуємо сирий блок даних із сокета
                data = await reader.read(512)
                if not data:
                    break

                mutated = self.mutate_packet(data)
                if mutated is None:
                    # Пакет втрачено в каналі
                    continue

                # Розрахунок випадкової затримки каналу (Jitter)
                delay_sec = random.uniform(self.cfg.min_delay_ms, self.cfg.max_delay_ms) / 1000.0

                # Моделювання перестановки (Reordering)
                if random.random() < self.cfg.reorder_prob and self._reorder_buffer is None:
                    self._reorder_buffer = mutated
                    continue

                await asyncio.sleep(delay_sec)
                writer.write(mutated)
                await writer.drain()

                # Якщо є відкладений пакет для перестановки — відправляємо його слідом
                if self._reorder_buffer is not None:
                    writer.write(self._reorder_buffer)
                    await writer.drain()
                    self._reorder_buffer = None

            except asyncio.CancelledError:
                break
            except Exception as ex:
                print(f"[Proxy Error] {ex}")
                break
```

## Фазинг вбудованих парсерів (Protocol Fuzzing)

Звичайні позитивні та негативні тести перевіряють лише ті випадки, про які інженер подумав заздалегідь: «передати пустий пакет», «передати пакет із неправильним CRC», «передати пакет максимального розміру». Проте вразливості нульового дня та критичні зависання виникають на стиках непередбачуваних умов: наприклад, коли після валідного заголовка з довжиною 60 байтів надходить маркер нового кадру через 12 байтів, а поле контрольної суми інтерпретується як новий заголовок.

**Фазинг (Fuzzing)** — це методика тестування, за якої програма бомбардується сотнями мільйонів автоматично згенерованих аномальних входів із метою виклику аварійного завершення (`Crash`), зависання (`Hang`) або порушення інваріантів пам'яті.

![Цикл фазингу парсера з контролем покриття](/root/course/embedded/stend-protokolu/img/fuzzing-coverage-feedback.svg)
*Еволюційний цикл фазингу: мутатор генерує вхідні вектори, санітайзери ASan/UBSan фіксують аварії пам'яті, а нові гілки коду повертаються в корпус тестів.*

### Чому сліпий випадковий фазинг неефективний для бінарних протоколів

Якщо подавати абсолютно випадковий потік байтів (`/dev/urandom`) у бінарний парсер, перша ж перевірка заголовка:

:::tabs
```c
if (frame[0] != PROTOCOL_MAGIC_BYTE) {
    return ERR_BAD_MAGIC;
}
```
```cpp
if (frame[0] != PROTOCOL_MAGIC_BYTE) {
    return std::unexpected(ParseError::BadMagic);
}
```
:::

відкине 255 з 256 згенерованих байтів (99.6%). А наступна перевірка 16-бітної контрольної суми CRC-16 відкине 65 535 з 65 536 пакетів, які випадково пройшли магічний байт. У результаті фазер мільярди разів виконає перші три рядки функції і ніколи не досягне логіки розбору корисного навантаження.

Сучасний фазинг базується на двох фундаментальних технологіях:

1. **Керування за покриттям коду (Coverage-Guided Graybox Fuzzing)**: Інструменти **LLVM LibFuzzer** та **AFL++** компілюють код парсера зі спеціальною трасувальною інструментацією. Коли чергова мутація відкриває нову гілку коду (`New Basic Block / Edge`), цей вхідний пакет зберігається в **корпус (Corpus)** як успішний предок, і наступні мутації будуються вже на його основі.
2. **Структурна обізнаність (Structure-Aware Mutations & Dictionaries)**: Фазеру надається словник магічних чисел протоколу або кастомний мутатор, який після кожної мутації перераховує CRC, дозволяючи фазеру миттєво проходити вхідні фільтри.

Повний робочий приклад автономного стенду LibFuzzer із кастомним мутатором CRC наведено в практичному керівництві: [автономний фазинг-харнес для перевірки бінарного кадрувальника](root:embedded/stend-protokolu/proj-fuzz-harness.md).

### Типові дефекти парсерів, що виявляються фазингом

Під час фазинг-тестування вбудованого коду санітайзери Clang знаходять п'ять найпоширеніших критичних помилок:

1. **Переповнення буфера на стеку (*Stack Buffer Overflow*)**:
:::tabs
```c
/* Вразливий код: копіювання довжини з пакета без перевірки ліміту */
uint8_t temp_buf[32];
memcpy(temp_buf, &payload[offset], payload_len); /* Якщо payload_len > 32 -> затерання стека! */
```
```cpp
// Безпечний аналог на C++ з перевіркою меж
std::array<uint8_t, 32> temp_buf{};
if (payload.size() <= temp_buf.size()) {
    std::memcpy(temp_buf.data(), payload.data(), payload.size());
}
```
:::

2. **Невирівняний доступ до пам'яті (*Unaligned Memory Access*)**:
:::tabs
```c
/* Небезпечний кастинг на непарній адресі: HardFault на ARM Cortex-M0 */
uint32_t val = *(const uint32_t*)(&payload[1]);
```
```cpp
// Безпечне читання через побайтові зсуви або memcpy
uint32_t val = static_cast<uint32_t>(payload[1]) |
               (static_cast<uint32_t>(payload[2]) << 8) |
               (static_cast<uint32_t>(payload[3]) << 16) |
               (static_cast<uint32_t>(payload[4]) << 24);
```
:::

3. **Нескінченний цикл розбору (*Infinite Loop Hang*)**:
   Виникає в циклах розбору записів TLV, якщо черговий елемент має нульову довжину `len == 0`, а покажчик зміщення не пересувається вперед:
:::tabs
```c
/* Вразливий цикл розбору TLV */
while (offset < total_len) {
    uint8_t tag = buf[offset++];
    uint8_t len = buf[offset++];
    /* Якщо len == 0 і тіло не зсуває offset, цикл стає нескінченним */
    offset += len; 
}
```
```cpp
// Безпечний цикл розбору з контролем прогресу покажчика
while (offset < total_len) {
    const uint8_t tag = buf[offset++];
    const uint8_t len = buf[offset++];
    if (offset + len > total_len) {
        break; // Вихід за межі кадру
    }
    offset += len;
}
```
:::

4. **Цілочисельне переповнення (*Integer Overflow*)**:
:::tabs
```c
/* Переповнення у виразі підрахунку розміру */
uint8_t total_alloc = user_len + 4; /* Якщо user_len == 255 -> total_alloc = 3 */
```
```cpp
// Безпечний підрахунок у ширшому цілочисельному типі
size_t total_alloc = static_cast<size_t>(user_len) + 4;
```
:::

5. **Розіменування нульового покажчика (*Null Pointer Dereference*)** при виклику таблиці функцій зворотного виклику (колбеків) для незареєстрованого ідентифікатора повідомлення.

## Тестування сумісності версій: Матриця взаємодії

У промислових системах та інтернеті речей пристрої не оновлюються одночасно. Коли випускається нова версія сервера v2.1, у полях продовжують працювати тисячі контролерів із версіями прошивок v1.0, v1.1 та v2.0.

Регресійне матричне тестування (*Cross-Version Matrix Testing*) автоматично перевіряє всі можливі пари взаємодії між різними поколіннями коду.

![Матриця крос-версійної сумісності протоколу](/root/course/embedded/stend-protokolu/img/compatibility-matrix-ci.svg)
*Матриця верифікації сумісності: автоматична перевірка того, що оновлені сервери розуміють старі пристрої, а старі вузли безпечно ігнорують нові поля без збоїв.*

### Правила верифікації в матриці

Для кожної комбінації `(Версія Вузла, Версія Сервера)` тестовий стенд перевіряє виконання трьох обов'язкових контрактів:

1. **Зворотна сумісність (Backward Compatibility, V_server > V_node)**:
   - Сервер v2.1 отримує пакет v1.0, у якому відсутні нові поля (наприклад, тиск або діагностичні прапорці).
   - **Вимога**: Сервер зобов'язаний успішно розібрати базові поля (напругу, ідентифікатор), підставити безпечні значення за замовчуванням (*defaults*) для нових полів і не повертати помилку клієнту.
2. **Пряма сумісність (Forward Compatibility, V_node < V_server)**:
   - Старий вузол v1.0 отримує пакет конфігурації від нового сервера v2.1 із додатковими TLV-тегами або розширеним хвостом.
   - **Вимога**: Вузол v1.0 зобов'язаний зчитати відомі йому поля, безпечно пропустити невідомі теги за полем довжини і продовжувати штатне функціонування без перезавантаження.
3. **Обробка несумісних мажорних змін (Major_server ≠ Major_node)**:
   - Вузол v1.0 отримує пакет v2.0 із принципово зміненим форматом кадрування або шифрування.
   - **Вимога**: Вузол зобов'язаний детерміновано відкинути пакет на рівні перевірки поля мажорної версії `ver_major` або прапорців `incompat_flags`, зафіксувати діагностичний лічильник помилок і не входити в аварійний стан.

### Реалізація матричного тестового раннера на Python

```python
import subprocess
import pytest
import socket
import time

# Перелік версій бінарників, зібраних у процесі релізів
SUPPORTED_VERSIONS = ["v1.0", "v1.1", "v2.0", "v2.1"]

class BinaryNodeInstance:
    """Керує життєвим циклом скомпільованого бінарника прошивки конкретної версії."""
    def __init__(self, version: str, port: int):
        self.version = version
        self.port = port
        self.process = None

    def start(self):
        binary_path = f"./bin/firmware_node_{self.version}"
        self.process = subprocess.Popen(
            [binary_path, "--port", str(self.port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(0.05) # Очікування відкриття сокета

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()

@pytest.mark.parametrize("node_ver", SUPPORTED_VERSIONS)
@pytest.mark.parametrize("server_ver", SUPPORTED_VERSIONS)
def test_cross_version_compatibility(node_ver: str, server_ver: str):
    """
    Матричний тест: запускає клієнт версії node_ver та перевіряє 
    обмін із сервером версії server_ver.
    """
    port = 19000 + int(node_ver.replace("v", "").replace(".", "")) * 10
    node = BinaryNodeInstance(node_ver, port)
    node.start()

    try:
        # 1. Підключаємо тестовий стенд як сервер версії server_ver
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", port))
        sock.settimeout(1.0)

        # 2. Формуємо кадр опитування стану згідно зі специфікацією server_ver
        request_packet = build_status_request(version=server_ver)
        sock.sendall(request_packet)

        # 3. Отримуємо відповідь від вузла
        response_raw = sock.recv(512)
        assert len(response_raw) > 0, f"Node {node_ver} dropped connection for server {server_ver}"

        # 4. Валідуємо семантику відповіді з урахуванням мажорних версій
        node_major = int(node_ver[1])
        server_major = int(server_ver[1])

        if node_major == server_major:
            parsed = parse_telemetry_response(response_raw, expected_version=server_ver)
            assert parsed.is_valid, f"Failed parsing {node_ver} response on {server_ver} server"
            assert parsed.voltage_mv > 0
        else:
            # При мажорній розбіжності вузол повинен відкинути запит або відповісти кодом несумісності
            assert is_incompatibility_rejected(response_raw), \
                f"Node {node_ver} accepted incompatible major frame from server {server_ver}"

        sock.close()
    finally:
        node.stop()
```

## Навантажувальне тестування та емуляція масових вузлів (Scale Testing)

Багато протоколів чудово працюють з одним пристроєм, але катастрофічно руйнуються, коли на один концентратор або брокер одночасно виходять сотні або тисячі вузлів.

Типові системні колапси, що виявляються стрес-тестуванням стенду:

1. **Ефект «громового стада» (*Thundering Herd Effect*)**:
   Після скидання живлення мікрорайону 2 000 лічильників одночасно вмикаються і в ту саму секунду починають процедуру реєстрації в мережі. Якщо прошивка не має рандомізованого початкового відступу (*Startup Random Delay*), шлюз захлинається у колізіях пакетів, жоден пристрій не отримує підтвердження, і всі 2 000 пристроїв одночасно переходять на повторну спробу через 5 секунд, вводячи мережу у вічний шторм.
2. **Лавина повторів (*Retry Storm*)**:
   Коли час відповіді сервера через перевантаження зростає з 50 мс до 600 мс, а таймаут очікування клієнта фіксований на рівні 500 мс, клієнти починають дублювати запити до того, як сервер встигне відповісти на перші. Навантаження на сервер подвоюється, затримка зростає до 2 секунд, що викликає третю хвилю повторів і повний параліч каналу.

### Архітектура емулятора 1 000 віртуальних пристроїв

Для навантажувального тестування створюють асинхронний емулятор, який підтримує тисячі незалежних автоматів станів у межах одного системного процесу:

```python
import asyncio
import time

class VirtualDeviceNode:
    def __init__(self, node_id: int, host: str, port: int):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.seq_num = 0
        self.tx_count = 0
        self.rx_count = 0
        self.errors = 0

    async def run(self):
        # Рандомізований старт для уникнення Thundering Herd
        await asyncio.sleep(random.uniform(0.1, 5.0))

        while True:
            try:
                reader, writer = await asyncio.open_connection(self.host, self.port)
                
                while True:
                    self.seq_num += 1
                    # Формуємо телеметричний бінарний кадр
                    payload = struct.pack("<HII", self.node_id, self.seq_num, int(time.time()))
                    frame = build_cobs_frame(msg_type=0x02, payload=payload)

                    t_start = time.monotonic()
                    writer.write(frame)
                    await writer.drain()
                    self.tx_count += 1

                    # Очікуємо підтвердження ACK
                    response = await asyncio.wait_for(reader.read(128), timeout=2.0)
                    rtt_ms = (time.monotonic() - t_start) * 1000.0
                    
                    if verify_ack(response, self.seq_num):
                        self.rx_count += 1
                    else:
                        self.errors += 1

                    # Пауза між вимірюваннями з експоненційним джитером
                    await asyncio.sleep(random.uniform(0.8, 1.2))

            except (asyncio.TimeoutError, ConnectionResetError, OSError):
                self.errors += 1
                # Експоненційний відступ при збої з джитером
                await asyncio.sleep(random.uniform(1.0, 3.0))

async def run_scale_test(total_nodes: int = 500):
    print(f"[*] Запуск навантажувального тесту з {total_nodes} віртуальними вузлами...")
    nodes = [VirtualDeviceNode(i, "127.0.0.1", 8080) for i in range(total_nodes)]
    await asyncio.gather(*(n.run() for n in nodes))
```

## Реалізація тестованого стека на C та C++

Щоб продемонструвати взаємодію стенду з реальним кодом прошивки, реалізуємо ядро протокольного автомата на C та ідіоматичному C++, яке включає кадрування, валідацію CRC, обробку таймаутів та безпечний розбір повідомлень.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define PROTOCOL_MAGIC_BYTE 0x5A
#define MAX_PAYLOAD_LEN     128
#define HEADER_OVERHEAD     4 /* Magic(1B) + Seq(1B) + Type(1B) + Len(1B) */

/* Стани кінцевого автомата приймача */
typedef enum {
    RX_STATE_WAIT_MAGIC = 0,
    RX_STATE_READ_HEADER,
    RX_STATE_READ_PAYLOAD,
    RX_STATE_READ_CRC
} RxState_t;

typedef struct {
    uint8_t seq_num;
    uint8_t msg_type;
    uint8_t payload_len;
    uint8_t payload[MAX_PAYLOAD_LEN];
    uint16_t crc16;
} ProtocolPacket_t;

typedef struct {
    RxState_t state;
    uint8_t   rx_buf[HEADER_OVERHEAD + MAX_PAYLOAD_LEN + 2];
    size_t    bytes_needed;
    size_t    bytes_read;
    ProtocolPacket_t current_packet;
    uint32_t  stat_crc_errors;
    uint32_t  stat_len_overflows;
    uint32_t  stat_valid_frames;
} ProtocolReceiver_t;

/* Обчислення CRC-16 (поліном 0x1021) */
static uint16_t calc_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

void protocol_receiver_init(ProtocolReceiver_t *rx) {
    memset(rx, 0, sizeof(ProtocolReceiver_t));
    rx->state = RX_STATE_WAIT_MAGIC;
}

/*
 * Побайтова обробка вхідного потоку кінцевим автоматом.
 * Повертає true, коли успішно зібрано та перевірено повний кадр.
 */
bool protocol_receiver_feed_byte(ProtocolReceiver_t *rx, uint8_t byte, ProtocolPacket_t *out_pkt) {
    switch (rx->state) {
        case RX_STATE_WAIT_MAGIC:
            if (byte == PROTOCOL_MAGIC_BYTE) {
                rx->rx_buf[0] = byte;
                rx->bytes_read = 1;
                rx->bytes_needed = HEADER_OVERHEAD;
                rx->state = RX_STATE_READ_HEADER;
            }
            break;

        case RX_STATE_READ_HEADER:
            rx->rx_buf[rx->bytes_read++] = byte;
            if (rx->bytes_read == rx->bytes_needed) {
                rx->current_packet.seq_num = rx->rx_buf[1];
                rx->current_packet.msg_type = rx->rx_buf[2];
                rx->current_packet.payload_len = rx->rx_buf[3];

                if (rx->current_packet.payload_len > MAX_PAYLOAD_LEN) {
                    /* Захист від переповнення буфера: скид автомата */
                    rx->stat_len_overflows++;
                    rx->state = RX_STATE_WAIT_MAGIC;
                    break;
                }

                if (rx->current_packet.payload_len > 0) {
                    rx->bytes_needed += rx->current_packet.payload_len;
                    rx->state = RX_STATE_READ_PAYLOAD;
                } else {
                    rx->bytes_needed += 2; /* Тільки CRC-16 */
                    rx->state = RX_STATE_READ_CRC;
                }
            }
            break;

        case RX_STATE_READ_PAYLOAD:
            rx->rx_buf[rx->bytes_read++] = byte;
            if (rx->bytes_read == rx->bytes_needed) {
                memcpy(rx->current_packet.payload, &rx->rx_buf[HEADER_OVERHEAD], rx->current_packet.payload_len);
                rx->bytes_needed += 2; /* Переходимо до читання 2 байтів CRC */
                rx->state = RX_STATE_READ_CRC;
            }
            break;

        case RX_STATE_READ_CRC:
            rx->rx_buf[rx->bytes_read++] = byte;
            if (rx->bytes_read == rx->bytes_needed) {
                size_t crc_offset = rx->bytes_read - 2;
                uint16_t received_crc = (uint16_t)rx->rx_buf[crc_offset] |
                                        ((uint16_t)rx->rx_buf[crc_offset + 1] << 8);

                uint16_t expected_crc = calc_crc16(&rx->rx_buf[1], crc_offset - 1);

                if (received_crc == expected_crc) {
                    rx->current_packet.crc16 = received_crc;
                    *out_pkt = rx->current_packet;
                    rx->stat_valid_frames++;
                    rx->state = RX_STATE_WAIT_MAGIC;
                    return true;
                } else {
                    rx->stat_crc_errors++;
                    rx->state = RX_STATE_WAIT_MAGIC;
                }
            }
            break;
    }

    return false;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <optional>
#include <array>
#include <expected>

namespace embedded_protocol {

constexpr uint8_t MAGIC_BYTE = 0x5A;
constexpr size_t MAX_PAYLOAD = 128;
constexpr size_t HEADER_LEN  = 4; // Magic(1B) + Seq(1B) + Type(1B) + Len(1B)
constexpr size_t CRC_LEN     = 2;

enum class RxState {
    WaitMagic,
    ReadHeader,
    ReadPayload,
    ReadCrc
};

enum class ParseError {
    BadMagic,
    LengthOverflow,
    CrcMismatch,
    IncompleteFrame
};

struct Packet {
    uint8_t seq_num{0};
    uint8_t msg_type{0};
    uint8_t payload_len{0};
    std::array<uint8_t, MAX_PAYLOAD> payload{};
    uint16_t crc16{0};
};

class StreamReceiver {
public:
    StreamReceiver() noexcept {
        reset();
    }

    void reset() noexcept {
        state_ = RxState::WaitMagic;
        bytes_read_ = 0;
        bytes_needed_ = 0;
    }

    [[nodiscard]] constexpr static uint16_t calculate_crc16(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (const uint8_t byte : data) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc = crc << 1;
                }
            }
        }
        return crc;
    }

    std::optional<Packet> feed_byte(uint8_t byte) noexcept {
        switch (state_) {
            case RxState::WaitMagic:
                if (byte == MAGIC_BYTE) {
                    raw_buf_[0] = byte;
                    bytes_read_ = 1;
                    bytes_needed_ = HEADER_LEN;
                    state_ = RxState::ReadHeader;
                }
                break;

            case RxState::ReadHeader:
                raw_buf_[bytes_read_++] = byte;
                if (bytes_read_ == bytes_needed_) {
                    current_pkt_.seq_num = raw_buf_[1];
                    current_pkt_.msg_type = raw_buf_[2];
                    current_pkt_.payload_len = raw_buf_[3];

                    if (current_pkt_.payload_len > MAX_PAYLOAD) {
                        ++stat_len_overflows_;
                        reset();
                        break;
                    }

                    if (current_pkt_.payload_len > 0) {
                        bytes_needed_ += current_pkt_.payload_len;
                        state_ = RxState::ReadPayload;
                    } else {
                        bytes_needed_ += CRC_LEN;
                        state_ = RxState::ReadCrc;
                    }
                }
                break;

            case RxState::ReadPayload:
                raw_buf_[bytes_read_++] = byte;
                if (bytes_read_ == bytes_needed_) {
                    std::memcpy(current_pkt_.payload.data(), &raw_buf_[HEADER_LEN], current_pkt_.payload_len);
                    bytes_needed_ += CRC_LEN;
                    state_ = RxState::ReadCrc;
                }
                break;

            case RxState::ReadCrc:
                raw_buf_[bytes_read_++] = byte;
                if (bytes_read_ == bytes_needed_) {
                    const size_t crc_offset = bytes_read_ - CRC_LEN;
                    const uint16_t received_crc = static_cast<uint16_t>(raw_buf_[crc_offset]) |
                                                  (static_cast<uint16_t>(raw_buf_[crc_offset + 1]) << 8);

                    const auto crc_span = std::span<const uint8_t>(&raw_buf_[1], crc_offset - 1);
                    const uint16_t expected_crc = calculate_crc16(crc_span);

                    if (received_crc == expected_crc) {
                        current_pkt_.crc16 = received_crc;
                        ++stat_valid_frames_;
                        Packet result = current_pkt_;
                        reset();
                        return result;
                    } else {
                        ++stat_crc_errors_;
                        reset();
                    }
                }
                break;
        }

        return std::nullopt;
    }

    [[nodiscard]] uint32_t crc_errors() const noexcept { return stat_crc_errors_; }
    [[nodiscard]] uint32_t len_overflows() const noexcept { return stat_len_overflows_; }
    [[nodiscard]] uint32_t valid_frames() const noexcept { return stat_valid_frames_; }

private:
    RxState state_{RxState::WaitMagic};
    std::array<uint8_t, HEADER_LEN + MAX_PAYLOAD + CRC_LEN> raw_buf_{};
    size_t bytes_needed_{0};
    size_t bytes_read_{0};
    Packet current_pkt_{};
    uint32_t stat_crc_errors_{0};
    uint32_t stat_len_overflows_{0};
    uint32_t stat_valid_frames_{0};
};

} // namespace embedded_protocol
```
:::

## Порівняльний аналіз рівнів випробування протоколу

Для побудови надійної стратегії забезпечення якості протоколу інженерна команда повинна розуміти межі застосування кожного рівня випробувань:

| Рівень випробувань | Що перевіряє | Швидкість виконання | Виявлені класи дефектів | Де запускається |
|---|---|---|---|---|
| **Модульні тести (Unit Tests)** | Окремі детерміновані функції розбору та кодування | >100 000 тестів/с | Базові помилки логіки, неправильний розрахунок CRC, граничні розміри | Робоча станція, кожен коміт |
| **Фазинг (LibFuzzer / ASan)** | Стійкість парсера до мільйонів непередбачуваних мутацій | 50 000–300 000 входів/с | Переповнення буферів, зависання, витоки пам'яті, UB, небезпечні касти | CI/CD (Pull Request), нічні збірки |
| **Проксі-ін'єктор стенду** | Автомат станів в умовах брудного каналу та затримок | 5 000–20 000 пакетів/с | Гонки станів (Race Conditions), дедлоки ARQ, таймаути, перестановки | CI/CD, регресійне тестування |
| **Матриця сумісності** | Взаємодію різних поколінь клієнтів і серверів | 1 000–5 000 пакетів/с | Порушення прямої/зворотної сумісності, некоректні дефолти полів | Етап підготовки релізу |
| **Стенд заліза (HIL)** | Реальні апаратні драйвери, таймери, DMA та живлення | 50–500 пакетів/с | Апаратні переривання, просідання живлення при передачі, біти UART | Фізичний тестовий стенд у лабораторії |

## Формальні інваріанти протоколу та перевірка автоматів станів

У процесі виконання тривалого стрес-тестування оркестратор випробувального стенду здійснює безперервну перевірку **формальних інваріантів** — умов, які зобов'язані виконуватися за будь-яких обставин, незалежно від кількості втрачених чи спотворених пакетів:

1. **Інваріант монотонності порядкових номерів**: Якщо передавач відправив пакети з номерами послідовності `Seq = 1, 2, 3`, приймач ніколи не повинен передати на прикладний рівень пакет `Seq = 2` після того, як уже передано `Seq = 3`.
2. **Інваріант обмеженості черги повторів**: Розмір черги ретрансмісій передавача не повинен перевищувати наперед заданий ліміт буфера `MAX_QUEUE_LEN`. При повному обриві зв'язку найстаріші низькопріоритетні телеметричні кадри повинні скидатися без блокування критичних аварійних сповіщень.
3. **Інваріант відсутності мертвого блокування (Deadlock-freedom)**: Автомат станів не має права залишатися в проміжному стані очікування квитанції ACK нескінченно довго. Якщо таймер очікування `ACK_TIMEOUT` сплив, а кількість повторів перевищила `MAX_RETRIES`, сесія зобов'язана перейти в стан скидання `DISCONNECTED` або `RECONNECTING` з генерацією діагностичної події.
4. **Інваріант збереження пам'яті (Leak-freedom)**: Кількість виділеної динамічної пам'яті або зайнятих статичних дескрипторів буферів після 1 000 000 відхилених некоректних кадрів повинна точно дорівнювати початковому значенню.

## Інтеграція стенду в CI/CD конвеєр

Тестовий стенд протоколу приносить максимальну користь, коли він повністю інтегрований у систему неперервної інтеграції (GitHub Actions, GitLab CI) і автоматично блокує злиття гілок (Pull Request), якщо новий коміт порушує сумісність або вразливий до фазингу.

Типовий конвеєр перевірки протоколу складається з чотирьох послідовних етапів (*stages*):

```yaml
# Приклад конфігурації .github/workflows/protocol_testbed.yml
name: Protocol Verification Pipeline

on: [push, pull_request]

jobs:
  fast-tests:
    name: 1. Unit Tests & Sanitizers
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Compile Native Host Build with ASan/UBSan
        run: |
          clang++ -O2 -g -fsanitize=address,undefined -Wall -Wextra \
            tests/host_runner.cpp src/protocol.cpp -o test_runner
      - name: Run Deterministic Unit Tests
        run: ./test_runner

  fuzzing:
    name: 2. Coverage-Guided Fuzzing (5 min)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Fuzz Target
        run: |
          clang++ -O2 -g -fsanitize=fuzzer,address,undefined \
            tests/fuzz_harness.cpp src/protocol.cpp -o fuzzer_bin
      - name: Run LibFuzzer in CI
        run: |
          ./fuzzer_bin corpus/ -max_total_time=300 -artifact_prefix=artifacts/
      - name: Upload Crash Artifacts on Failure
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: fuzzer-crashes
          path: artifacts/

  matrix-compatibility:
    name: 3. Cross-Version Matrix
    runs-on: ubuntu-latest
    needs: fast-tests
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Pytest & Asyncio
        run: pip install pytest pytest-asyncio
      - name: Run Cross-Version Testbed
        run: pytest tests/test_matrix_compatibility.py -v

  load-and-faults:
    name: 4. Fault Injection & Scale Test
    runs-on: ubuntu-latest
    needs: matrix-compatibility
    steps:
      - uses: actions/checkout@v3
      - name: Run 500-Node Stress Test with Packet Drops
        run: |
          python3 tests/scale_fault_testbed.py --nodes 500 --drop-rate 0.05 --duration 60
```

### Принцип відтворюваності аварій (Deterministic Seeds)

Будь-який випадковий збій, знайдений генератором завад або фазером під час нічного тестування, марний для команди розробників, якщо його не можна повторити на комп'ютері інженера.

Щоб стенд забезпечував 100% відтворюваність:
1. Генератор псевдовипадкових чисел раннера ініціалізується фіксованим зерном:
   ```python
   SEED = int(os.getenv("TEST_SEED", random.randint(1, 1000000)))
   random.seed(SEED)
   print(f"[CI] Test Run Random Seed: {SEED}")
   ```
2. Якщо тест падає, у журналі CI друкується точне значення `TEST_SEED=482914`. Інженер вводить `TEST_SEED=482914 pytest` на робочій станції й отримує ту саму точну послідовність завад, переставлянь та обривів зв'язку, що й у хмарі.
3. Кожен аварійний пакет фазера зберігається як мінімальний двійковий файл (`crash-minimized`), який автоматично додається до тестового набору регресій для запобігання повторній появі вразливості в майбутньому.
