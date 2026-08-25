# ⚙️ Кастомізація конвеєра збірки через Python SCons-хуки

Стандартний конвеєр збірки мікроконтролерного коду завершується генерацією базових двійкових файлів: образу ELF із символьною інформацією та сирого двійкового образу Flash-пам'яті (`.bin` або `.hex`). Проте у реальних виробничих проєктах цього недостатньо. Інженерам необхідно автоматизувати супутні технологічні операції: динамічно генерувати файл версії з міткою часу та хешем Git-коміту, підміняти скрипт лінкера для специфічного виділення буферів DMA чи областей RAM швидкого доступу, аналізувати карту секцій пам'яті через `nm` та `size`, а також розраховувати й дописувати контрольну суму CRC32 безпосередньо в кінець бінарника для апаратної верифікації завантажувачем. Цей проєкт розбирає створення та інтеграцію комплексного сценарію розширення `extra_scripts` мовою Python на базі програмного API середовища SCons.

---

## Архітектурний задум та схема інтеграції

У системі PlatformIO сценарії розширення виконуються безпосередньо всередині рантайму рушія збірки SCons. Це забезпечує повний програмний доступ до внутрішнього об'єкта `env` (*Construction Environment*), який містить таблицю всіх шляхів, прапорців компілятора, визначень макросів, правил генерації об'єктних файлів та списку цільових артефактів.

Наш практичний комплекс складається з трьох ключових блоків:
1. **Модуль попередньої обробки (`scripts/generate_version.py`)**: перехоплює конвеєр до старту трансляції файлів C/C++ і генерує заголовок `include/generated_version.h`. Якщо вміст файлу не змінився з попередньої збірки, фізичний запис на диск блокується, що запобігає каскадній перекомпіляції проєкту через зміну часової мітки файлу (`mtime`).
2. **Модуль підміни скрипта лінкера (`scripts/inject_custom_ld.py`)**: динамічно перевіряє наявність спеціальних секцій швидкої пам'яті (CCM RAM або ITCM) та модифікує шлях до скрипта компонування в середовищі SCons до початку формування лінкувального графа.
3. **Модуль пост-обробки, аналізу карти пам'яті та ін'єкції контрольної суми (`scripts/post_build_toolchain.py`)**: підписується на завершення створення бінарного образу `firmware.bin`. Він запускає утиліту `arm-none-eabi-size`, витягує розміри секцій `.text`, `.data` та `.bss`, обчислює 32-бітний поліном CRC32 (за стандартом IEEE 802.3), дописує 4 байти чексуми у форматі Little-Endian у хвіст файлу та створює підписаний OTA-артефакт.

Підключення сценаріїв здійснюється у файлі `platformio.ini` через директиву `extra_scripts`:

```ini
[env:stm32_production]
platform = ststm32 @ 17.3.0
board = nucleo_f401re
framework = stm32cube
extra_scripts =
    pre:scripts/generate_version.py
    pre:scripts/inject_custom_ld.py
    post:scripts/post_build_toolchain.py
build_flags =
    -D CUSTOM_FIRMWARE_HEADER=1
    -O2
```

---

## Реалізація сценаріїв SCons

### 1. Модуль генерації компіляційних метаданих (Pre-build)

Сценарій виконується перед обробкою першого вихідного файлу. Через системну функцію `Import("env")` скрипт імпортує активний контекст цільового середовища:

```python
# scripts/generate_version.py
import subprocess
import os
from datetime import datetime

# Отримання середовища SCons з контексту PlatformIO
Import("env")

def get_git_revision():
    """Витягування короткого хешу та стану репозиторію."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=env.get("PROJECT_DIR")
        ).strip().decode("utf-8")
        
        # Перевірка наявності незакомічених змін у робочому дереві
        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=env.get("PROJECT_DIR")
        ).strip().decode("utf-8")
        
        dirty_flag = "-dirty" if len(status) > 0 else ""
        return f"{commit}{dirty_flag}"
    except Exception:
        return "v1.0.0-release"

def generate_header():
    """Створення C/C++ заголовка з метаданими збірки."""
    project_dir = env.get("PROJECT_DIR")
    include_dir = os.path.join(project_dir, "include")
    os.makedirs(include_dir, exist_ok=True)
    
    header_path = os.path.join(include_dir, "generated_version.h")
    git_hash = get_git_revision()
    build_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    env_name = env.get("PIOENV", "unknown_env")
    mcu = env.get("BOARD_MCU", "unknown_mcu")
    
    content = f"""#pragma once
// Цей файл згенеровано автоматично скриптом scripts/generate_version.py.
// Будь-які ручні правки буде перезаписано під час наступної збірки.

#define BUILD_GIT_HASH "{git_hash}"
#define BUILD_TIMESTAMP "{build_time}"
#define BUILD_ENVIRONMENT "{env_name}"
#define BUILD_TARGET_MCU "{mcu}"
"""
    
    # Критична перевірка: запобігаємо зміні mtime, якщо зміст не змінився
    if os.path.exists(header_path):
        with open(header_path, "r", encoding="utf-8") as f:
            if f.read() == content:
                return
                
    with open(header_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[PRE-BUILD] Оновлено файл заголовка: {header_path} (git: {git_hash})")

# Запуск генерації метаданих
generate_header()
```

### 2. Модуль динамічної підміни скрипта компонувальника

У багатьох сценаріях системний скрипт лінкера, що постачається разом із пакетом платформи (`framework-stm32cubef4`), не передбачає спеціальних секцій для безпосереднього доступу контролерів DMA (Direct Memory Access) без кешування. Скрипт `scripts/inject_custom_ld.py` перевіряє наявність власного скрипта лінкера в проєкті та підміняє змінну `LDSCRIPT_PATH` в об'єкті середовища SCons:

```python
# scripts/inject_custom_ld.py
import os

Import("env")

def inject_linker_script():
    project_dir = env.get("PROJECT_DIR")
    custom_ld = os.path.join(project_dir, "ldscripts", "stm32f401_dma_custom.ld")
    
    if os.path.exists(custom_ld):
        print(f"[PRE-BUILD] Застосування кастомного скрипта лінкера: {custom_ld}")
        # Перевизначення шляху до LD-скрипта в об'єкті SCons
        env.Replace(LDSCRIPT_PATH=custom_ld)
        # Додавання прапорця для виводу детальної мапи розподілу пам'яті
        env.Append(LINKFLAGS=["-Wl,--print-memory-usage"])
    else:
        print("[PRE-BUILD] Використовується стандартний скрипт лінкера з SDK.")

inject_linker_script()
```

### 3. Модуль розрахунку CRC32 та аналізу секцій (Post-build)

Сценарій пост-обробки реєструє обробник через `env.AddPostAction()`, прив'язуючись до генерації двійкового образу `$BUILD_DIR/${PROGNAME}.bin`. Він також викликає системну утиліту крос-тулчейну `size` для валідації сумарного обсягу пам'яті:

```python
# scripts/post_build_toolchain.py
import struct
import zlib
import subprocess
import os

Import("env")

def compute_checksum_crc32(file_path):
    """Розрахунок стандартного 32-бітного полінома CRC32."""
    crc = 0
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            crc = zlib.crc32(chunk, crc)
    return crc & 0xFFFFFFFF

def analyze_memory_footprint(elf_path):
    """Запуск size для зчитування секцій .text, .data та .bss."""
    try:
        # Витягуємо точний шлях до утиліти size із середовища SCons
        size_tool = env.subst("$SIZE")
        if not size_tool:
            size_tool = "arm-none-eabi-size"
            
        output = subprocess.check_output([size_tool, elf_path]).decode("utf-8")
        lines = output.strip().split("\n")
        if len(lines) >= 2:
            print("[POST-BUILD] Карта пам'яті ELF:")
            print(f"  {lines[0]}")
            print(f"  {lines[1]}")
    except Exception as err:
        print(f"[POST-BUILD WARNING] Не вдалося викликати size: {err}")

def process_firmware_binary(source, target, env):
    """Пост-процесинг: ін'єкція CRC32 у кінець образу та вивід параметрів."""
    # target[0] є SCons Node об'єктом цільового бінарного файлу
    bin_path = str(target[0])
    elf_path = bin_path.replace(".bin", ".elf")
    
    if not os.path.exists(bin_path):
        print(f"[POST-BUILD ERROR] Бінарний файл не знайдено: {bin_path}")
        return

    if os.path.exists(elf_path):
        analyze_memory_footprint(elf_path)

    original_size = os.path.getsize(bin_path)
    crc_value = compute_checksum_crc32(bin_path)
    
    # Дописуємо 4 байти контрольної суми у форматі Little-Endian
    with open(bin_path, "ab") as f:
        f.write(struct.pack("<I", crc_value))
        
    final_size = os.path.getsize(bin_path)
    
    print("\n" + "=" * 64)
    print(f"[POST-BUILD] Успішна обробка образу: {os.path.basename(bin_path)}")
    print(f"  Початковий розмір Flash: {original_size} байтів")
    print(f"  Розрахована CRC32:       0x{crc_value:08X}")
    print(f"  Фінальний розмір (+4B):  {final_size} байтів")
    print("=" * 64 + "\n")

# Реєстрація пост-хука над генерацією фінального двійкового образу
env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", process_firmware_binary)
```

---

## Робота зі змінними SCons та інтерполяція рядків

Для побудови надійних сценаріїв інженер повинен розуміти внутрішній механізм підстановки SCons. Коли скрипт викликає `env.subst("$BUILD_DIR/${PROGNAME}.bin")`, рушій SCons рекурсивно розгортає всі вбудовані змінні:

1. **`$BUILD_DIR`**: абсолютний шлях до каталогу збірки конкретного цільового середовища (наприклад, `.pio/build/nucleo_f401re`).
2. **`$PROGNAME`**: базове ім'я виконуваного файлу (за замовчуванням `firmware`).
3. **`$CC` / `$CXX` / `$LINK`**: точні шляхи до виконуваних файлів компіляторів та компонувальника у каталозі `~/.platformio/packages/`.
4. **`$PROJECT_DIR`**: абсолютний шлях до кореневого каталогу проєкту.

Використання методу `env.subst()` гарантує переносність скрипта між операційними системами Windows, macOS та Linux без жорсткого кодування роздільників шляхів.

---

## Реєстрація власних цілей CLI (Custom Targets)

Окрім перехоплення стандартних етапів компіляції, SCons дозволяє додавати утилітарні команди безпосередньо у CLI PlatformIO за допомогою методу `env.AddCustomTarget()`. Наприклад, можна автоматизувати генерацію зашифрованого пакета оновлення (OTA Package) командою `pio run -t package_ota`:

```python
def build_ota_package(target, source, env):
    bin_file = env.subst("$BUILD_DIR/${PROGNAME}.bin")
    ota_output = os.path.join(env.get("PROJECT_DIR"), "releases", "firmware_ota.bin")
    os.makedirs(os.path.dirname(ota_output), exist_ok=True)
    
    print(f"[CUSTOM TARGET] Пакування OTA-образу: {bin_file} -> {ota_output}")
    # Тут можна виконати виклик утиліт шифрування AES або підпису криптографічним ключем RSA/ECDSA

env.AddCustomTarget(
    name="package_ota",
    dependencies=["$BUILD_DIR/${PROGNAME}.bin"],
    actions=[build_ota_package],
    title="Генерація підписаного OTA-пакета",
    description="Створює зашифрований образ прошивки для бездротового оновлення"
)
```

---

## Пастки, крайові випадки та архітектурні нюанси

### 1. Каскадний зрив інкрементальної збірки

Якщо генератор вихідних файлів або заголовків у фазі `pre:` беззастережно перезаписує файл `.h` під час кожного виклику `pio run`, операційна система оновлює системну часову мітку модифікації (`mtime`). Рушій SCons інтерпретує це як зміну залежності та ініціює повну повторну компіляцію всіх вихідних модулів проєкту, які включають цей заголовок. Для збереження швидкості інкрементальної збірки скрипт зобов'язаний спочатку зчитати наявний файл і виконувати запис лише у випадку реальної невідповідності даних.

### 2. Відмінності цільових вузлів між різними архітектурами

У платформах на базі ESP-IDF кінцевим артефактом є файл `$BUILD_DIR/${PROGNAME}.bin`. Натомість для мікроконтролерів STM32 чи Cortex-M під голим фреймворком CMSIS лінкер за замовчуванням створює лише файл `$BUILD_DIR/${PROGNAME}.elf`, а конвертація у сирий бінарник виконується окремою утилітою `objcopy`. Якщо підписатися на неіснуючий вузол `.bin`, SCons проігнорує хук без генерації помилки.

Для універсальної підтримки використовується перевірка типу вихідного файлу або реєстрація хука безпосередньо над ELF-файлом:

```python
# Підписка на ELF-вузол із примусовою генерацією BIN-файлу
env.AddPostAction(
    "$BUILD_DIR/${PROGNAME}.elf",
    env.VerboseAction(
        "$OBJCOPY -O binary $BUILD_DIR/${PROGNAME}.elf $BUILD_DIR/${PROGNAME}.bin",
        "Генерація бінарного образу через $OBJCOPY"
    )
)
```

### 3. Забруднення глобального рантайму Python при паралельних тарґетах

Коли у `platformio.ini` визначено декілька середовищ (наприклад, `[env:esp32]` та `[env:stm32]`), PlatformIO компілює їх послідовно або паралельно в межах одного процесу Python. Якщо сценарій розширення використовує пряму мутацію змінних оточення хоста через словник `os.environ["CFLAGS"]`, це змінить поведінку компілятора для всіх наступних тарґетів у черзі. Усі модифікації прапорців та шляхів повинні здійснюватися винятково через методи локального об'єкта `env` (`env.Append()`, `env.Prepend()`, `env.Replace()`).
