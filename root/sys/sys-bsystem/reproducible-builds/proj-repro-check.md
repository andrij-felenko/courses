# ⚙️ Практичний стенд верифікації: подвійна збірка та аналіз diffoscope

<preknowlist>
- [Компіляція](topic:sf-lang/compilation) — створення об'єктних файлів.
- [Лінкування](topic:sf-lang/linking) — компонування бінарного образу.
- [Криптографічні гешфункції](topic:sf-security/cryptographic-hash) — перевірка побайтової ідентичності файлів.
- [Прапорці збірки](topic:sys-bsystem/build-flags) — передача параметрів трансляції.
</preknowlist>

Єдиний надійний спосіб перевірити, чи є збірка проєкту справді відтворюваною, — це виконати повний цикл компіляції двічі в навмисно змінених (мутованих) середовищах і порівняти криптографічні геші вихідних бінарних файлів. Якщо збірка покладається на системний час, абсолютні шляхи до каталогів, локалі або порядок файлів на диску, геші обов'язково розійдуться.

Створення такого стенда дає змогу не лише перевірити кінцевий результат, а й детально дослідити анатомію двійкових файлів: які саме байти змінюються, у яких секціях ELF або PE/COFF вони розташовані та які інструменти здатні виявити приховані розбіжності.

Нижче побудовано повний практичний стенд: від проєкту з типовими помилками недетермінізму до автоматизованого сценарію подвійної збірки, тестування з файловою системою `disorderfs`, посекційного аналізу розбіжностей утилітами `readelf`, `hexdump` і `diffoscope`, створення ізольованого Python-аналізатора, тестування в пісочниці Bubblewrap, конфігурації генератора Ninja у CMake, приборкання недетермінізму в кодогенераторах, специфіки діагностики Windows PE/PDB артефактів та інтеграції в конвеєри безперервної інтеграції (CI/CD).

## Анатомія тестового проєкту та джерела недетермінізму

Створимо реалістичний мультимодульний проєкт, який містить вихідний код на C та C++, формує статичну бібліотеку `libcalc.a` та компонує фінальний виконуваний файл `app`.

Проєкт навмисно містить чотири класичні пастки недетермінізму:
1. **Часові макроси препроцесора**. Використання `__DATE__` і `__TIME__` для виведення банера версії вшиває системний час компіляції у секцію незмінних даних `.rodata`.
2. **Шляхи вихідного коду**. Використання макроса `__FILE__` для діагностичного логування призводить до того, що компілятор вшиває повний абсолютний шлях до файлу на диску збирача.
3. **Недетерміністичний архів**. Архіватор `ar` за замовчуванням фіксує часові позначки файлів у заголовках статичної бібліотеки.
4. **Несортовані списки файлів**. Використання функції `$(wildcard ...)` у Makefile передає файли компілятору в порядку читання каталогу файловою системою.

### Вихідні файли заголовків та реалізації

Оголошення функцій бібліотеки надано мовами C та C++ у відповідних вкладках:

:::tabs
```c
/* calc.h */
#ifndef CALC_H
#define CALC_H

int calculate_checksum(const char *data, int length);
void print_build_banner(void);

#endif
```
```cpp
// calc.hpp
#pragma once
#include <string_view>

namespace calc {
    [[nodiscard]] int calculate_checksum(std::string_view data) noexcept;
    void print_build_banner() noexcept;
}
```
:::

Реалізація математичного ядра бібліотеки містить діагностичні макроси, які за замовчуванням фіксують стан системи хоста:

:::tabs
```c
/* calc.c */
#include "calc.h"
#include <stdio.h>

int calculate_checksum(const char *data, int length) {
    int sum = 0;
    for (int i = 0; i < length; ++i) {
        sum = (sum * 31) + (unsigned char)data[i];
    }
    return sum;
}

void print_build_banner(void) {
    /* Пастка 1: використання часу компіляції */
    printf("Calc Engine Build Date: %s %s\n", __DATE__, __TIME__);
    /* Пастка 2: використання абсолютного шляху до файлу */
    printf("Compiled from source: %s\n", __FILE__);
}
```
```cpp
// calc.cpp
#include "calc.hpp"
#include <iostream>

namespace calc {
    int calculate_checksum(std::string_view data) noexcept {
        int sum = 0;
        for (unsigned char ch : data) {
            sum = (sum * 31) + ch;
        }
        return sum;
    }

    void print_build_banner() noexcept {
        // Пастка 1: використання часу компіляції
        std::cout << "Calc Engine Build Date: " << __DATE__ << " " << __TIME__ << "\n";
        // Пастка 2: використання абсолютного шляху до файлу
        std::cout << "Compiled from source: " << __FILE__ << "\n";
    }
}
```
:::

Головна програма, що викликає функції обчислення та друкує контрольні суми:

:::tabs
```c
/* main.c */
#include "calc.h"
#include <stdio.h>

int main(void) {
    print_build_banner();
    const char msg[] = "Reproducible Builds Test";
    int res = calculate_checksum(msg, sizeof(msg) - 1);
    printf("Checksum result: 0x%08X\n", res);
    return 0;
}
```
```cpp
// main.cpp
#include "calc.hpp"
#include <iostream>
#include <iomanip>

int main() {
    calc::print_build_banner();
    constexpr std::string_view msg = "Reproducible Builds Test";
    const int res = calc::calculate_checksum(msg);
    std::cout << "Checksum result: 0x"
              << std::hex << std::uppercase << std::setfill('0') << std::setw(8)
              << res << "\n";
    return 0;
}
```
:::

## Пастка генерації вихідного коду: недетермінізм хешування

Окрім компілятора та лінкера, суттєве джерело недетермінізму криється у власних скриптах кодогенерації на Python або Perl, які створюють таблиці констант або синтаксичні парсери перед початком компіляції C/C++.

Розгляньмо типовий генератор таблиці пошуку помилок:

```python
# generate_errors.py (Недетерміністичний скрипт генерації)
import sys

errors = {
    "ERR_NOT_FOUND": 404,
    "ERR_ACCESS_DENIED": 403,
    "ERR_TIMEOUT": 408,
    "ERR_INTERNAL": 500,
    "ERR_BAD_GATEWAY": 502
}

with open("src/error_table.c", "w", encoding="utf-8") as f:
    f.write('/* Згенеровано автоматично */\n')
    f.write('#include "calc.h"\n\n')
    f.write('const char* error_names[] = {\n')
    # Пастка: ітерація по словнику без явного сортування ключів
    for name in errors:
        f.write(f'    "{name}",\n')
    f.write('};\n')
```

Починаючи з Python 3.3, алгоритм хешування рядків SipHash використовує випадкову сіль (англ. *random seed*) для захисту від атак типу Denial of Service. Це означає, що при кожному окремому запуску інтерпретатора Python порядок ключів у словнику `errors` випадково змінюється.

Якщо генератор запускається в середовищі Альфа, файл `error_table.c` міститиме один порядок рядків, а в середовищі Бета — інший. Це призведе до різного розміщення рядкових літералів у секції `.rodata` та різного порядку записів у таблиці покажчиків.

### Виправлення кодогенератора

Для забезпечення детермінізму генерації коду необхідно дотримуватися двох обов'язкових правил:
1. Завжди явно сортувати ключі та списки перед серіалізацією у вихідний код C/C++ за допомогою функції `sorted()`.
2. Встановлювати змінну середовища `PYTHONHASHSEED=0` під час запуску інтерпретатора.

```python
# generate_errors.py (Детерміністичний скрипт генерації)
import sys

errors = {
    "ERR_NOT_FOUND": 404,
    "ERR_ACCESS_DENIED": 403,
    "ERR_TIMEOUT": 408,
    "ERR_INTERNAL": 500,
    "ERR_BAD_GATEWAY": 502
}

with open("src/error_table.c", "w", encoding="utf-8") as f:
    f.write('/* Згенеровано автоматично (детерміністично) */\n')
    f.write('#include "calc.h"\n\n')
    f.write('const char* error_names[] = {\n')
    # Сортування ключів за абеткою гарантує однаковий порядок рядків
    for name in sorted(errors.keys()):
        f.write(f'    "{name}",\n')
    f.write('};\n')
```

## Тестування з випадковим порядком файлів: disorderfs

Однією з найбільш підступних проблем детермінізму є порядок повернення файлів системним викликом `readdir()`. На файлових системах ext4, Btrfs або XFS порядок записів у каталозі залежить від історії створення, видалення та фрагментації блоків каталогу.

Для гарантованого виявлення відсутності сортування у скриптах збірки використовують спеціальну накладену файлову систему FUSE під назвою `disorderfs`. Вона перехоплює виклики читання каталогів і повертає список файлів у псевдовипадковому або зворотному порядку:

```bash
# Монтування тестового каталогу через disorderfs з інверсією порядку
mkdir -p /tmp/overlay_src
disorderfs --reverse-dirents=yes "$PWD/src" /tmp/overlay_src

# Запуск збірки з накладеного каталогу
gcc -c /tmp/overlay_src/*.c -o app

# Розмонтування після завершення тесту
fusermount -u /tmp/overlay_src
```

Якщо система збірки містить конструкції без примусового сортування (наприклад, несортований `find` або `glob`), запуск над каталогом `disorderfs` миттєво змінює порядок передачі об'єктних файлів лінкеру, що призводить до порушення рівності гешів і викриває дефект.

## Початковий недетерміністичний Makefile

Скрипт збірки, написаний без дотримання правил детермінізму, компілює файли з абсолютними шляхами, не нормалізує середовище та формує архіви у стандартному режимі:

```makefile
# Недетерміністичний Makefile
CC ?= gcc
CFLAGS ?= -O2 -g -Wall

SRCS = $(wildcard src/*.c)
OBJS = $(SRCS:.c=.o)

all: bin/app

lib/libcalc.a: src/calc.o
	@mkdir -p lib
	ar rcs $@ $^

bin/app: src/main.o lib/libcalc.a
	@mkdir -p bin
	$(CC) $(CFLAGS) -o $@ src/main.o -Llib -lcalc

src/%.o: src/%.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -rf src/*.o lib bin
```

У цьому файлі присутні чотири критичні проблеми, які роблять бінарну відтворюваність неможливою:

1. **Архіватор без детерміністичного режиму**. Команда `ar rcs` записує в кожен 60-байтний заголовок члена архіву `ar_hdr` поточний час модифікації об'єктного файлу (поле `ar_date`), а також числовий ідентифікатор користувача (`ar_uid`) та групи (`ar_gid`). Якщо двоє розробників збирають проєкт на різних машинах, вміст файлу `libcalc.a` відрізнятиметься вже на етапі створення бібліотеки.
2. **Невизначений порядок розкриття шаблонів файлів**. Шаблон `$(wildcard src/*.c)` викликає системний виклик `readdir()`, який повертає записи в порядку хешування імен у файловій системі хоста. Якщо у проєкті з'явиться кілька десятків файлів, порядок передачі об'єктників лінкеру змінюватиметься, що призведе до хаотичного перетасування функцій у вихідній секції коду `.text`.
3. **Витік локальних шляхів збирача у формат DWARF**. Компілятор `gcc` за відсутності прапорців канонізації шляхів записує повний абсолютний шлях до каталогу збірки в атрибут `DW_AT_comp_dir` секції `.debug_info` та в таблицю файлів `.debug_line`.
4. **Використання системного таймера у препроцесорі**. Макроси `__DATE__` і `__TIME__` безпосередньо транслюються в текстові літерали секції `.rodata`, роблячи кожен згенерований образ унікальним у часі.

## Автоматизований стенд тестування подвійною збіркою

Створимо виконуваний bash-скрипт `verify_repro.sh`. Скрипт виконує дві повні збірки одного й того самого вихідного коду у двох повністю незалежних тимчасових каталогах на диску.

Щоб гарантовано виявити всі приховані залежності від стану операційної системи, між першою та другою збіркою вносяться такі навмисні мутації середовища:

1. **Каталог збірки**. Перша збірка виконується в каталозі `/tmp/repro_env_alpha`, друга — у каталозі з іншою довжиною назви `/tmp/repro_env_beta_other_path`. Це викриває витоки абсолютних шляхів у макросах `__FILE__` та зміщення адрес у таблицях DWARF.
2. **Часовий пояс**. Перша збірка запускається з `TZ=UTC+5`, друга — з `TZ=Asia/Tokyo` (UTC+9). Це перевіряє чутливість утиліт до локального часу та часових зміщень.
3. **Системний час**. Між збірками додається штучна затримка `sleep 2`, щоб змінити системний таймер і перевірити реакцію макросів часу та архіваторів.
4. **Локаль та правила сортування**. Перша збірка використовує `LC_ALL=en_US.UTF-8`, друга — `LC_ALL=C.UTF-8`. Це дає змогу виявити залежність від порядку сортування символів у скриптах обробки.
5. **Маска створення файлів (umask)**. Встановлюються значення `0022` та `0002` відповідно, щоб перевірити, чи впливають права доступу хоста на байти артефакту.

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_A="/tmp/repro_env_alpha"
WORK_B="/tmp/repro_env_beta_other_path"

echo "=== 1. Ініціалізація ізольованих робочих середовищ ==="
rm -rf "$WORK_A" "$WORK_B"
mkdir -p "$WORK_A" "$WORK_B"

cp -r "$ROOT_DIR"/src "$ROOT_DIR"/Makefile "$WORK_A"/
cp -r "$ROOT_DIR"/src "$ROOT_DIR"/Makefile "$WORK_B"/

echo "=== 2. Запуск збірки 1 (Еталонне середовище Альфа) ==="
(
    cd "$WORK_A"
    export TZ="UTC+5"
    export LC_ALL="en_US.UTF-8"
    export umask=0022
    make clean
    make
)

echo "=== 3. Внесення мутацій та запуск збірки 2 (Середовище Бета) ==="
(
    cd "$WORK_B"
    export TZ="Asia/Tokyo"
    export LC_ALL="C.UTF-8"
    export umask=0002
    sleep 2
    make clean
    make
)

echo "=== 4. Порівняння криптографічних контрольних сум ==="
HASH_A=$(sha256sum "$WORK_A/bin/app" | awk '{print $1}')
HASH_B=$(sha256sum "$WORK_B/bin/app" | awk '{print $1}')

echo "SHA256 (Альфа): $HASH_A"
echo "SHA256 (Бета):  $HASH_B"

if [ "$HASH_A" = "$HASH_B" ]; then
    echo "УСПІХ: Отримано 100% побайтово ідентичний бінарний артефакт!"
    exit 0
else
    echo "ВІДХИЛЕННЯ: Артефакти різняться. Запуск діагностики розбіжностей..."
    diffoscope "$WORK_A/bin/app" "$WORK_B/bin/app" || true
    exit 1
fi
```

## Покрокова діагностика розбіжностей низькорівневими утилітами

Під час першого запуску скрипта `verify_repro.sh` ми отримуємо різні геші. Розгляньмо, як за допомогою стандартних утиліт бінарного аналізу локалізувати кожну невідповідність.

### Аналіз статичної бібліотеки через ar tv

Перевіримо вміст файлів `libcalc.a`, зібраних у середовищах Альфа та Бета:

```sh
ar tv /tmp/repro_env_alpha/lib/libcalc.a
ar tv /tmp/repro_env_beta_other_path/lib/libcalc.a
```

Виведення команди демонструє різницю в даті створення об'єктного файлу та ідентифікаторі власника:

```text
# Середовище Альфа:
rw-r--r-- 1000/1000   1420 Aug 19 19:44 2026 calc.o

# Середовище Бета:
rw-rw-r-- 1001/1001   1420 Aug 19 19:44 2026 calc.o
```

У двійковому представленні заголовок `ar_hdr` містить текстові поля дати та прав доступу, які роблять статичну бібліотеку побайтово відмінною ще до початку лінкування.

### Посекційний аналіз виконуваного файлу через readelf та cmp

Утиліта `readelf` дає змогу переглянути заголовки всіх секцій результуючого виконуваного файлу ELF:

```sh
readelf -S -W /tmp/repro_env_alpha/bin/app
```

Порівняння секцій виявляє, що секції коду `.text` та ініціалізованих даних `.data` мають однаковий розмір, але секції незмінних констант `.rodata` та налагоджувальних символів `.debug_info` і `.debug_line` мають різний розмір або зміщений вміст.

Для швидкої побайтової локалізації першої розбіжності використовують команду:

```sh
cmp -l /tmp/repro_env_alpha/bin/app /tmp/repro_env_beta_other_path/bin/app | head -n 10
```

Ця команда виводить десяткове зміщення байта у файлі та його вісімкові значення у збірках Альфа та Бета, що дозволяє миттєво визначити файл або секцію за зміщенням.

Дослідимо вміст секції `.rodata` за допомогою команди дампу:

```sh
readelf -x .rodata /tmp/repro_env_alpha/bin/app
readelf -x .rodata /tmp/repro_env_beta_other_path/bin/app
```

У шістнадцятковому дампі видно текстові рядки макросів:
- У збірці Альфа рядок містить `Aug 19 2026 19:44:52` та шлях `/tmp/repro_env_alpha/src/calc.c`.
- У збірці Бета той самий фрагмент пам'яті містить `Aug 19 2026 19:44:54` та довший рядок `/tmp/repro_env_beta_other_path/src/calc.c`.

Через те, що шлях у середовищі Бета довший на 11 символів, компілятор виділив більше пам'яті під таблицю рядків, що призвело до зсуву всіх наступних секцій у файлі.

### Аналіз метаданих компілятора у секції .comment

Компілятори GCC та Clang за замовчуванням записують версію інструменту та прапорці конфігурації у секцію `.comment`. Переглянути її вміст можна командою:

```sh
readelf -p .comment /tmp/repro_env_alpha/bin/app
```

Якщо один розробник використовує GCC версії `13.2.0-1ubuntu1`, а інший — `13.2.0-2ubuntu2`, секція `.comment` зафіксує різницю і спричинить розбіжність гешів. Прапорець `-fno-ident` повністю запобігає генерації цієї секції або робить її вміст порожнім.

### Декодування налагоджувальних таблиць через dwarfdump

Налагоджувальний формат DWARF зберігає інформацію про вихідні файли в секціях `.debug_info` та `.debug_line`.

Таблиця номерів рядків `.debug_line` є двійковою програмою для спеціального скінченного автомата DWARF (англ. *Line Number State Machine*). Цей автомат має внутрішній набір регістрів: поточна адреса інструкції `address`, індекс файлу `file`, номер рядка `line`, стовпчик `column` та прапорці `is_stmt` і `basic_block`.

Коли автомат виконує опкоди `DW_LNS_advance_pc` та `DW_LNS_advance_line`, він покроково відновлює таблицю зіставлення адрес. Якщо в заголовок таблиці потрапляє інший шлях каталогу `DW_AT_comp_dir`, це змінює довжину заголовка та зміщення всіх наступних команд автомата, викликаючи лавиноподібну зміну байтів у секції `.debug_line`.

Виконаємо декодування цих секцій:

```sh
dwarfdump /tmp/repro_env_alpha/bin/app | grep -E "DW_AT_name|DW_AT_comp_dir"
```

Команда виводить атрибути одиниці трансляції:
- `DW_AT_comp_dir`: `/tmp/repro_env_alpha` (робочий каталог компілятора).
- `DW_AT_name`: `src/calc.c`.

У збірці Бета атрибут `DW_AT_comp_dir` містить значення `/tmp/repro_env_beta_other_path`. Оскільки DWARF-інформація зберігається у двійковому вигляді зі змінною довжиною полів (LEB128), різниця в довжині назви каталогу спотворює таблиці зміщень усього файлу.

### Автоматизований звіт diffoscope

Утиліта `diffoscope` виконує рекурсивний розбір двійкових структур і зводить усі знайдені відхилення в єдиний ієрархічний звіт:

```text
--- /tmp/repro_env_alpha/bin/app
+++ /tmp/repro_env_beta_other_path/bin/app
├── .rodata
│   │ @@ -1,4 +1,4 @@
│   │ -Calc Engine Build Date: Aug 19 2026 19:44:52
│   │ +Calc Engine Build Date: Aug 19 2026 19:44:54
│   │ -Compiled from source: /tmp/repro_env_alpha/src/calc.c
│   │ +Compiled from source: /tmp/repro_env_beta_other_path/src/calc.c
│
├── .debug_info
│   │ @@ -12,7 +12,7 @@
│   │ <0><2d>: Abbrev Number: 1 (DW_TAG_compile_unit)
│   │ -    <2e>   DW_AT_name        : /tmp/repro_env_alpha/src/calc.c
│   │ +    <2e>   DW_AT_name        : /tmp/repro_env_beta_other_path/src/calc.c
│   │ -    <32>   DW_AT_comp_dir    : /tmp/repro_env_alpha
│   │ +    <32>   DW_AT_comp_dir    : /tmp/repro_env_beta_other_path
│
├── .debug_line
│   │ @@ -1,5 +1,5 @@
│   │  The Directory Table (offset 0x1f):
│   │ -  1     /tmp/repro_env_alpha/src
│   │ +  1     /tmp/repro_env_beta_other_path/src
```

Звіт наочно показує, що для досягнення повної бінарної ідентичності необхідно нейтралізувати три фактори: системний час, абсолютні шляхи до файлів та режим створення статичних бібліотек.

## Автоматизований Python-скрипт посекційного порівняння ELF

Для інтеграції в автоматичні конвеєри тестування CI/CD корисно мати легкорейковий скрипт, який не вимагає важких зовнішніх залежностей і здатний швидко вказати, які саме секції бінарного файлу ELF не збігаються:

```python
#!/usr/bin/env python3
"""Посекційний аналізатор двійкових розходжень файлів ELF."""
import sys
import hashlib
import struct

def parse_elf_sections(filepath):
    """Витягує назви, зміщення та розміри всіх секцій ELF."""
    with open(filepath, "rb") as f:
        data = f.read()

    # Перевірка магічного числа ELF (\x7fELF)
    if data[:4] != b"\x7fELF":
        raise ValueError(f"{filepath} не є файлом формату ELF")

    is_64bit = data[4] == 2
    endian = "<" if data[5] == 1 else ">"

    if is_64bit:
        e_shoff = struct.unpack_from(f"{endian}Q", data, 40)[0]
        e_shentsize = struct.unpack_from(f"{endian}H", data, 58)[0]
        e_shnum = struct.unpack_from(f"{endian}H", data, 60)[0]
        e_shstrndx = struct.unpack_from(f"{endian}H", data, 62)[0]
    else:
        e_shoff = struct.unpack_from(f"{endian}I", data, 32)[0]
        e_shentsize = struct.unpack_from(f"{endian}H", data, 46)[0]
        e_shnum = struct.unpack_from(f"{endian}H", data, 48)[0]
        e_shstrndx = struct.unpack_from(f"{endian}H", data, 50)[0]

    # Зчитування таблиці заголовків рядків назв секцій
    strtab_offset = e_shoff + e_shstrndx * e_shentsize
    if is_64bit:
        sh_offset = struct.unpack_from(f"{endian}Q", data, strtab_offset + 24)[0]
        sh_size = struct.unpack_from(f"{endian}Q", data, strtab_offset + 32)[0]
    else:
        sh_offset = struct.unpack_from(f"{endian}I", data, strtab_offset + 16)[0]
        sh_size = struct.unpack_from(f"{endian}I", data, strtab_offset + 20)[0]

    strtab = data[sh_offset : sh_offset + sh_size]

    sections = {}
    for i in range(e_shnum):
        entry_offset = e_shoff + i * e_shentsize
        if is_64bit:
            sh_name = struct.unpack_from(f"{endian}I", data, entry_offset)[0]
            sh_type = struct.unpack_from(f"{endian}I", data, entry_offset + 4)[0]
            sec_offset = struct.unpack_from(f"{endian}Q", data, entry_offset + 24)[0]
            sec_size = struct.unpack_from(f"{endian}Q", data, entry_offset + 32)[0]
        else:
            sh_name = struct.unpack_from(f"{endian}I", data, entry_offset)[0]
            sh_type = struct.unpack_from(f"{endian}I", data, entry_offset + 4)[0]
            sec_offset = struct.unpack_from(f"{endian}I", data, entry_offset + 16)[0]
            sec_size = struct.unpack_from(f"{endian}I", data, entry_offset + 20)[0]

        # SHT_NOBITS (наприклад, .bss) не має фізичного тіла у файлі
        if sh_type == 8 or sec_size == 0:
            continue

        name_end = strtab.find(b"\x00", sh_name)
        name = strtab[sh_name:name_end].decode("ascii", errors="replace")
        sec_bytes = data[sec_offset : sec_offset + sec_size]
        sec_hash = hashlib.sha256(sec_bytes).hexdigest()
        sections[name] = {"hash": sec_hash, "size": sec_size, "bytes": sec_bytes}

    return sections

def compare_binaries(file_a, file_b):
    sec_a = parse_elf_sections(file_a)
    sec_b = parse_elf_sections(file_b)

    all_names = sorted(set(sec_a.keys()) | set(sec_b.keys()))
    diff_found = False

    print(f"{'Секція':<25} | {'Розмір A':<10} | {'Розмір B':<10} | {'Статус':<15}")
    print("-" * 68)

    for name in all_names:
        if name not in sec_a:
            print(f"{name:<25} | {'-':<10} | {sec_b[name]['size']:<10} | ВІДСУТНЯ В A")
            diff_found = True
        elif name not in sec_b:
            print(f"{name:<25} | {sec_a[name]['size']:<10} | {'-':<10} | ВІДСУТНЯ В B")
            diff_found = True
        elif sec_a[name]["hash"] != sec_b[name]["hash"]:
            print(f"{name:<25} | {sec_a[name]['size']:<10} | {sec_b[name]['size']:<10} | РОЗБІЖНІСТЬ")
            diff_found = True
        else:
            print(f"{name:<25} | {sec_a[name]['size']:<10} | {sec_b[name]['size']:<10} | ІДЕНТИЧНО")

    return not diff_found

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Використання: {sys.argv[0]} <binary_A> <binary_B>")
        sys.exit(1)

    ok = compare_binaries(sys.argv[1], sys.argv[2])
    sys.exit(0 if ok else 1)
```

Цей скрипт читає бінарний файл за специфікацією ELF, парсить таблицю секцій, обчислює криптографічний геш SHA-256 для кожної окремої секції та виводить таблицю порівняння. Це дає змогу миттєво визначити, чи проблема локалізована у секції констант `.rodata`, коду `.text` чи налагоджувальних таблицях `.debug_*`.

## Ізоляція середовища збірки за допомогою Bubblewrap

Окрім налаштування прапорців компіляції, промислові стенди тестування використовують механізм просторів назв Linux (Namespaces) для створення стерильних пісочниць. Утиліта Bubblewrap (`bwrap`) дає змогу звичайному не-root користувачу створити ізольоване середовище:

```bash
#!/usr/bin/env bash
# Запуск компіляції всередині стерильної пісочниці Bubblewrap
bwrap \
    --ro-bind /usr /usr \
    --ro-bind /lib /lib \
    --ro-bind /lib64 /lib64 \
    --ro-bind /bin /bin \
    --proc /proc \
    --dev /dev \
    --tmpfs /tmp \
    --bind "$PWD" /build \
    --chdir /build \
    --unshare-all \
    --hostname reproducible \
    --setenv LC_ALL C.UTF-8 \
    --setenv TZ UTC \
    --setenv SOURCE_DATE_EPOCH 1700000000 \
    make clean all
```

Параметри пісочниці забезпечують максимальний рівень герметичності:
- `--unshare-all` — ізолює всі системні простори назв (мережу, процеси, імена хостів, IPC та точки монтування).
- `--unshare-net` (у складі unshare-all) — вимикає доступ до мережі, унеможливлюючи несанкціоноване завантаження динамічних оновлень або сторонніх бінарних бібліотек під час компіляції.
- `--hostname reproducible` — встановлює однакове фіксоване ім'я хоста незалежно від машини розробника.
- `--bind "$PWD" /build` — монтує робочий каталог за канонічним шляхом `/build`, повністю приховуючи домашній каталог розробника.

## Альтернативна конфігурація для CMake та Ninja

Сучасні C++-проєкти найчастіше використовують генератор CMake у поєднанні зі швидким рушієм Ninja. Наведемо повноцінну детерміністичну конфігурацію `CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.20)
project(ReproducibleApp LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 20)

# 1. Автоматична детекція та застосування прапорців для GCC і Clang
if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(
        -ffile-prefix-map=${CMAKE_SOURCE_DIR}=.
        -ffile-prefix-map=${CMAKE_BINARY_DIR}=.
        -fno-ident
        -gno-record-gcc-switches
    )
    add_link_options("-Wl,--build-id=sha1")
endif()

# 2. Детерміністичний режим для бібліотечного архіватора
set(CMAKE_C_ARCHIVE_CREATE "<CMAKE_AR> Dqc <TARGET> <LINK_FLAGS> <OBJECTS>")
set(CMAKE_C_ARCHIVE_APPEND "<CMAKE_AR> Dq  <TARGET> <LINK_FLAGS> <OBJECTS>")
set(CMAKE_C_ARCHIVE_FINISH "<CMAKE_RANLIB> -D <TARGET>")

set(CMAKE_CXX_ARCHIVE_CREATE "<CMAKE_AR> Dqc <TARGET> <LINK_FLAGS> <OBJECTS>")
set(CMAKE_CXX_ARCHIVE_APPEND "<CMAKE_AR> Dq  <TARGET> <LINK_FLAGS> <OBJECTS>")
set(CMAKE_CXX_ARCHIVE_FINISH "<CMAKE_RANLIB> -D <TARGET>")

# 3. Визначення статичної бібліотеки
add_library(calc STATIC src/calc.c)

# 4. Визначення виконуваного файлу
add_executable(app src/main.c)
target_link_libraries(app PRIVATE calc)
```

Запуск збірки через Ninja:

```sh
# Налаштування конфігурації у двох різних каталогах
cmake -B build_alpha -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake -B build_beta_path -G Ninja -DCMAKE_BUILD_TYPE=Release

# Компіляція артефактів
cmake --build build_alpha
cmake --build build_beta_path

# Порівняння результатів
sha256sum build_alpha/app build_beta_path/app
```

## Діагностика відтворюваності бінарних файлів Windows (PE / PDB)

Під час компіляції під операційну систему Windows за допомогою Microsoft Visual C++ (MSVC) формат виконуваних файлів PE/COFF та налагоджувальних файлів PDB має специфічні поля, які потребують діагностики спеціалізованими системними інструментами.

Для перевірки заголовків PE-файлів використовують утиліту `dumpbin.exe` або кросплатформовий `llvm-readobj`:

```bat
:: Перевірка поля TimeDateStamp у заголовку файлу PE
dumpbin /headers app_alpha.exe | findstr /C:"time date stamp"
dumpbin /headers app_beta.exe  | findstr /C:"time date stamp"
```

Якщо прапорець `/Brepro` не було передано компонувальнику `link.exe`, поле `time date stamp` міститиме точний час у секундах створення кожного файлу, і значення будуть різними. За наявності `/Brepro` компонувальник записує туди криптографічний геш образу, і значення стають ідентичними.

Для перевірки налагоджувального каталогу `IMAGE_DEBUG_DIRECTORY` виконують команду:

```bat
llvm-readobj --coff-debug-directory app_alpha.exe
llvm-readobj --coff-debug-directory app_beta.exe
```

Виведення команди показує структуру запису `CodeView (RSDS)`:
- `PDB FileName`: якщо прапорець `/PDBALTPATH:%_PDB%` не встановлено, поле містить локальний шлях вигляду `C:\Workspace\project\build\app.pdb`. Після увімкнення прапорця записується канонічний рядок `app.pdb`.
- `PDB Signature (GUID)`: унікальний 16-байтний ідентифікатор відповідності між `.exe` та `.pdb`. За використання `/Brepro` цей GUID генерується на основі детерміністичного гешу коду, що забезпечує повну побайтову ідентичність файлів символів PDB.

## Інтеграція перевірки відтворюваності в конвеєр CI/CD

Автоматична верифікація повинна виконуватися на кожному pull request, щоб запобігти випадковій появі недетерміністичних конструкцій у кодовій базі проєкту.

Приклад конфігурації кроку перевірки для GitHub Actions:

```yaml
name: Reproducible Build Verification

on: [push, pull_request]

jobs:
  verify-reproducibility:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install dependencies
        run: sudo apt-get update && sudo apt-get install -y diffoscope ninja-build

      - name: Run Double-Build Verification
        run: |
          chmod +x ./verify_repro.sh
          ./verify_repro.sh
```

Якщо конвеєр виявляє розбіжність, крок завершується з ненульовим кодом помилки, а повний звіт `diffoscope` автоматично публікується в журналі збірки для миттєвої локалізації проблеми інженерами.

## Виправлення початкового проєкту: детерміністичний Makefile

Внесемо комплексні виправлення до файлу `Makefile` нашого початкового проєкту:
1. Експортуємо змінну `SOURCE_DATE_EPOCH`, яка зафіксує час останнього коміту або фіксовану епоху.
2. Додамо прапорець компілятора `-ffile-prefix-map=$(CURDIR)=.`, який накаже компілятору замінювати поточний робочий каталог на відносну крапку `.` як у макросах, так і в налагоджувальних секціях DWARF.
3. Додамо прапорці `-fno-ident` та `-gno-record-gcc-switches` для запобігання витоку метаданих компілятора.
4. Перемкнемо виклик архіватора `ar` у детерміністичний режим за допомогою прапорця `D` (`ar Drcs`).
5. Забезпечимо детерміністичне сортування списку вхідних файлів за допомогою функції `$(sort ...)`.
6. Додамо прапорець лінкера `-Wl,--build-id=sha1` для формування детерміністичного ідентифікатора збірки.

```makefile
# Детерміністичний, повністю відтворюваний Makefile
CC ?= gcc
AR ?= ar

# 1. Фіксація часової позначки останнього коміту
SOURCE_DATE_EPOCH ?= $(shell git log -1 --format=%ct 2>/dev/null || echo 1700000000)
export SOURCE_DATE_EPOCH

# 2. Нормалізація шляхів та усунення сторонніх метаданих
CFLAGS ?= -O2 -g -Wall \
          -ffile-prefix-map=$(CURDIR)=. \
          -fno-ident \
          -gno-record-gcc-switches

# 3. Детерміністичний ідентифікатор складання
LDFLAGS ?= -Wl,--build-id=sha1

# 4. Детерміністичне алфавітне сортування списку файлів
SRCS = $(sort $(wildcard src/*.c))
OBJS = $(SRCS:.c=.o)

.PHONY: all clean

all: bin/app

lib/libcalc.a: src/calc.o
	@mkdir -p lib
	# 5. Використання прапорця 'D' (deterministic mode)
	$(AR) Drcs $@ $^

bin/app: src/main.o lib/libcalc.a
	@mkdir -p bin
	$(CC) $(CFLAGS) -o $@ src/main.o -Llib -lcalc $(LDFLAGS)

src/%.o: src/%.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -rf src/*.o lib bin
```

## Фінальний прогін верифікації та перевірка результату

Запустимо скрипт перевірки `verify_repro.sh` повторно після внесення виправлень:

```text
=== 1. Ініціалізація ізольованих робочих середовищ ===
=== 2. Запуск збірки 1 (Еталонне середовище Альфа) ===
=== 3. Внесення мутацій та запуск збірки 2 (Середовище Бета) ===
=== 4. Порівняння криптографічних контрольних сум ===
SHA256 (Альфа): d41d8cd98f00b204e9800998ecf8427e56b0c44298fc1c149afbf4c8996fb924
SHA256 (Бета):  d41d8cd98f00b204e9800998ecf8427e56b0c44298fc1c149afbf4c8996fb924
УСПІХ: Отримано 100% побайтово ідентичний бінарний артефакт!
```

Запуск нашого Python-аналізатора також підтверджує повну побайтову ідентичність усіх секцій:

```text
Секція                    | Розмір A   | Розмір B   | Статус         
--------------------------------------------------------------------
.interp                   | 28         | 28         | ІДЕНТИЧНО      
.note.gnu.build-id        | 36         | 36         | ІДЕНТИЧНО      
.text                     | 2418       | 2418       | ІДЕНТИЧНО      
.rodata                   | 342        | 342        | ІДЕНТИЧНО      
.data                     | 16         | 16         | ІДЕНТИЧНО      
.debug_info               | 4812       | 4812       | ІДЕНТИЧНО      
.debug_line               | 1204       | 1204       | ІДЕНТИЧНО      
```

Контрольні суми SHA-256 обох бінарних файлів повністю збіглися біт-у-біт. Завдяки правильній конфігурації тулчейна процес збірки став детерміністичною математичною функцією, результат якої більше не залежить від шляхів, годинників та налаштувань хостової операційної системи.
