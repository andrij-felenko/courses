# ⚙️ Практикум перелінкування: ізоляція об'єктних файлів та скрипт перезбирання прошивки

Якщо компанія ухвалює інженерне рішення поширювати монолітну прошивку або двійковий файл зі статично скомпільованою бібліотекою під ліцензією LGPLv2.1 або LGPLv3, вона зобов'язана надати клієнтам повноцінний комплект для перелінкування (англ. *relinking kit*).

Цей інженерний практикум демонструє повний цикл підготовки такого комплекту: від маскування внутрішніх символів пропрієтарного коду до автоматизованого стенда, що перевіряє можливість заміни відкритої бібліотеки на модифіковану версію.

## Архітектура демонстраційного проєкту

Типовий вбудований проєкт, що стикається з вимогами LGPL, складається з трьох ключових рівнів:
1. **Відкрита бібліотека під LGPL (`libcodec`):** модуль стиснення телеметричних даних, вихідний код якого за умовами ліцензії повинен бути доступним для модифікації користувачем.
2. **Пропрієтарне ядро (`proprietary_engine`):** алгоритми цифрової фільтрації сигналів та керування виконавчими механізмами, які компанія прагне захистити від витоку у вигляді вихідних текстів.
3. **Комплект поставки для перелінкування (`relink_kit`):** набір файлів, що передається кінцевому клієнту разом із фізичним виробом (пропрієтарний об'єктний файл `.o`, вихідні коди бібліотеки `libcodec`, скрипти компонувальника, конфігурація збирача та інструкція).

Головне інженерне завдання полягає у створенні такого об'єктного файлу `proprietary_engine.o`, який містить рівно стільки інтерфейсної інформації, скільки необхідно лінкеру для успішного збирання, але приховує всі внутрішні назви функцій, проміжні змінні та статичні таблиці коефіцієнтів.

## 1. Реалізація пропрієтарного модуля: маскування символів

За замовчуванням компілятор GCC та Clang робить усі глобальні функції та змінні видимими для зовнішнього лінкування (тип зв'язування `STB_GLOBAL` у таблиці символів ELF `.symtab`). Якщо такий файл передати замовнику, утиліти `nm` або `readelf` одразу покажуть повну структуру внутрішніх викликів.

Щоб запобігти цьому, застосовується техніка керування видимістю символів:
- Усі внутрішні функції позначаються як статичні (`static`) або компілюються з атрибутом прихованої видимості (`-fvisibility=hidden`).
- Лише офіційні точки входу в модуль явно експортуються через атрибут `__attribute__((visibility("default")))` (або `[[gnu::visibility("default")]]` у сучасному C++).
- У C++ коді критично важливо вимикати механізм інформації про типи часу виконання (`-fno-rtti`) та обробку винятків (`-fno-exceptions`), оскільки структури RTTI та таблиці розгортання стека (`.eh_frame`) містять повні незашифровані імена класів і методів навіть за умови увімкненої оптимізації.
- Для C++ методів створюється стабільна плоска C-обгортка (`extern "C"`), щоб уникнути проблем із декодуванням імен (англ. *name mangling*) між різними версіями компіляторів.

:::tabs
```c
/* proprietary_engine.c — Закритий модуль обробки сигналів */
#include <stdint.h>
#include <stddef.h>

/* Експортований інтерфейс зовнішньої LGPL-бібліотеки */
extern int lgpl_codec_compress(const uint8_t *in, size_t in_len, 
                               uint8_t *out, size_t *out_len);

/* Внутрішній пропрієтарний алгоритм: не повинен бути доступний ззовні */
static uint32_t proprietary_math_filter(uint32_t raw_val) {
    uint32_t acc = raw_val * 0x45D9F3B;
    acc ^= (acc >> 16);
    return acc + 0x1234567;
}

/* Публічна точка входу пропрієтарного ядра */
__attribute__((visibility("default")))
int process_sensor_stream(const uint8_t *raw_buf, size_t len, 
                          uint8_t *out_buf, size_t *out_len) {
    if (!raw_buf || !out_buf || !out_len || len == 0) {
        return -1;
    }

    uint8_t preprocessed[256];
    size_t proc_len = (len < sizeof(preprocessed)) ? len : sizeof(preprocessed);

    for (size_t i = 0; i < proc_len; ++i) {
        preprocessed[i] = (uint8_t)proprietary_math_filter(raw_buf[i]);
    }

    return lgpl_codec_compress(preprocessed, proc_len, out_buf, out_len);
}
```
```cpp
// proprietary_engine.cpp — Закритий модуль обробки сигналів
#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <expected>

// Експортований C-інтерфейс зовнішньої LGPL-бібліотеки
extern "C" int lgpl_codec_compress(const uint8_t *in, size_t in_len, 
                                  uint8_t *out, size_t *out_len);

namespace proprietary {

namespace {
// Внутрішній пропрієтарний алгоритм у безназванному просторі імен
constexpr uint32_t math_filter(uint32_t raw_val) noexcept {
    uint32_t acc = raw_val * 0x45D9F3B;
    acc ^= (acc >> 16);
    return acc + 0x1234567;
}
} // namespace

enum class EngineError {
    InvalidInput,
    CompressionFailed
};

// Публічний C++ клас обробника
class [[gnu::visibility("default")]] SensorProcessor {
public:
    std::expected<size_t, EngineError> process(std::span<const uint8_t> input, 
                                               std::span<uint8_t> output) {
        if (input.empty() || output.empty()) {
            return std::unexpected(EngineError::InvalidInput);
        }

        std::vector<uint8_t> preprocessed;
        preprocessed.reserve(input.size());
        for (uint8_t b : input) {
            preprocessed.push_back(static_cast<uint8_t>(math_filter(b)));
        }

        size_t out_written = output.size();
        int rc = lgpl_codec_compress(preprocessed.data(), preprocessed.size(), 
                                     output.data(), &out_written);
        if (rc != 0) {
            return std::unexpected(EngineError::CompressionFailed);
        }

        return out_written;
    }
};

} // namespace proprietary

// Зовнішня C-обгортка для лінкування точки входу
extern "C" [[gnu::visibility("default")]]
int process_sensor_stream(const uint8_t *raw_buf, size_t len, 
                          uint8_t *out_buf, size_t *out_len) {
    if (!raw_buf || !out_buf || !out_len) return -1;
    
    proprietary::SensorProcessor proc;
    auto res = proc.process(std::span(raw_buf, len), std::span(out_buf, *out_len));
    if (!res) return -1;
    
    *out_len = *res;
    return 0;
}
```
:::

## 2. Конвеєр підготовки об'єктного комплекту

Підготовка двійкового файлу для передачі користувачеві вимагає суворого триетапного процесу обробки об'єктного коду:

1. **Компіляція з оптимізацією та секціонуванням:** Використовуються прапорці `-ffunction-sections` та `-fdata-sections`. Це змушує компілятор розміщувати кожну функцію в окремій секції ELF (наприклад, `.text.process_sensor_stream`). Під час фінального лінкування прапорець `--gc-sections` видалить увесь невикористаний код.
2. **Видалення зневаджувальної інформації:** Утиліта `arm-none-eabi-strip --strip-debug` повністю видаляє секції DWARF (`.debug_info`, `.debug_line`, `.debug_str`), які містять назви вихідних файлів, номери рядків та структури типів.
3. **Локалізація прихованих символів:** Утиліта `arm-none-eabi-objcopy --localize-hidden` перетворює всі символи, які не мають атрибута `default`, на локальні (`STB_LOCAL`). Такі символи не можуть конфліктувати з кодом користувача та видаляються з глобальної таблиці імен.

Аналіз таблиці символів скомпільованого об'єктного файлу можна провести за допомогою утиліти `readelf`:

```
$ arm-none-eabi-readelf -s proprietary_engine.o

Symbol table '.symtab' contains 4 entries:
   Num:    Value  Size Type    Bind   Vis      Ndx Name
     0: 00000000     0 NOTYPE  LOCAL  DEFAULT  UND 
     1: 00000000    42 FUNC    LOCAL  DEFAULT    2 proprietary_math_filter
     2: 00000000     0 NOTYPE  GLOBAL DEFAULT  UND lgpl_codec_compress
     3: 00000030   112 FUNC    GLOBAL DEFAULT    2 process_sensor_stream
```

Як видно з виводу, внутрішня функція `proprietary_math_filter` стала локальною (`LOCAL`), зовнішній виклик LGPL-бібліотеки позначено як невизначений (`UND`), а публічна точка входу `process_sensor_stream` доступна для лінкера як глобальна (`GLOBAL`).

```makefile
# Makefile внутрішнього збирання релізного релінк-пакета

CC = arm-none-eabi-gcc
OBJCOPY = arm-none-eabi-objcopy
STRIP = arm-none-eabi-strip

CFLAGS = -mcpu=cortex-m4 -mthumb -O2 -fvisibility=hidden \
         -ffunction-sections -fdata-sections -Wall

all: relink_package

# Збирання пропрієтарного об'єктного файлу
proprietary_engine.o: proprietary_engine.c
	$(CC) $(CFLAGS) -c $< -o $@
	$(STRIP) --strip-debug $@
	$(OBJCOPY) --localize-hidden $@

# Формування комплекту для передачі клієнту
relink_package: proprietary_engine.o
	mkdir -p dist_relink_kit/obj
	mkdir -p dist_relink_kit/lgpl_src
	mkdir -p dist_relink_kit/scripts
	cp proprietary_engine.o dist_relink_kit/obj/
	cp -r ../submodules/lgpl_codec/* dist_relink_kit/lgpl_src/
	cp linker_script.ld dist_relink_kit/scripts/
	cp Makefile.customer dist_relink_kit/Makefile
	cp README_RELINK.txt dist_relink_kit/
	tar -czf customer_relink_bundle.tar.gz dist_relink_kit
```

## 3. Клієнтський Makefile та скрипт лінкера

Файл `Makefile.customer` разом зі скриптом лінкера `linker_script.ld` вкладається у кореневий каталог архіву дистрибуції. Цей скрипт повинен бути максимально простим і не вимагати від клієнта встановлення пропрієтарних IDE: достатньо стандартного пакету GNU Arm Embedded Toolchain.

Компонувальник `arm-none-eabi-gcc` отримує на вхід два файли: скомпільований клієнтом `lgpl_codec.o` та наданий вендором `proprietary_engine.o`. Прапорець `-Wl,--gc-sections` гарантує точне розміщення коду за адресами флеш-пам'яті, визначеними у скрипті лінкера.

Скрипт лінкера повинен містити чітко розмежовані регіони пам'яті:
```
MEMORY
{
  FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 2048K
  RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 512K
}
```

```makefile
# Makefile.customer — Надається клієнту у складі relink kit

TOOLCHAIN_PREFIX ?= arm-none-eabi-
CC = $(TOOLCHAIN_PREFIX)gcc
LD = $(TOOLCHAIN_PREFIX)ld
OBJCOPY = $(TOOLCHAIN_PREFIX)objcopy

CFLAGS = -mcpu=cortex-m4 -mthumb -O2 -Ilgpl_src/include
LDFLAGS = -T scripts/linker_script.ld -Wl,--gc-sections

# 1. Компіляція модифікованого клієнтом коду LGPL-бібліотеки
lgpl_codec.o: lgpl_src/codec.c
	$(CC) $(CFLAGS) -c $< -o $@

# 2. Перелінкування пропрієтарного об'єктного файлу з новою бібліотекою
firmware.elf: obj/proprietary_engine.o lgpl_codec.o
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o $@

firmware.bin: firmware.elf
	$(OBJCOPY) -O binary $< $@

clean:
	rm -f lgpl_codec.o firmware.elf firmware.bin

.PHONY: clean
```

Супровідний файл `README_RELINK.txt` зобов'язаний містити інформацію про точну версію компілятора (`arm-none-eabi-gcc 12.3.rel1`), інструкцію зі встановлення крос-компілятора на Linux/Windows, команду запуску утиліти прошивання (наприклад, `openocd` або `st-flash`) та опис обмежень на розмір скомпільованого коду бібліотеки, щоб модифікований бінарник не вийшов за межі доступної флеш-пам'яті мікроконтролера.

## 4. Автоматизований стенд валідації сумісності в CI/CD

Щоб захистити компанію від претензій аудиторів відкритого коду та судових позовів, релізна процедура в системі безперервної інтеграції (CI/CD) повинна включати обов'язковий тест на валідність комплекту перелінкування.

Тестовий сценарій працює за принципом чорної скриньки:
1. Розгортає сформований архів `customer_relink_bundle.tar.gz` у тимчасовому ізольованому каталозі.
2. Виконує первинне збирання стандартної прошивки.
3. Вносить синтетичну модифікацію у вихідний код відкритої бібліотеки (додає унікальний числовий маркер або змінює логіку обчислень).
4. Запускає команду перелінкування.
5. Перевіряє скомпільований двійковий образ `firmware.bin` на наявність внесеного маркерного байтового патерну.

```python
#!/usr/bin/env python3
"""validate_relink.py — Автоматизована перевірка можливості перелінкування."""
import os
import subprocess
import sys
import tempfile
import shutil

def run_cmd(cmd, cwd):
    res = subprocess.run(cmd, cwd=cwd, shell=True, 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"ПОМИЛКА при виконанні: {cmd}\n{res.stderr}")
        sys.exit(1)
    return res.stdout

def test_relink_kit(bundle_path):
    temp_dir = tempfile.mkdtemp(prefix="relink_test_")
    print(f"[+] Розгортання комплекту перелінкування у: {temp_dir}")
    
    # 1. Розпакування комплекту
    shutil.unpack_archive(bundle_path, temp_dir)
    kit_root = os.path.join(temp_dir, "dist_relink_kit")
    
    # 2. Первинне збирання
    print("[+] Збирання базової прошивки клієнтським Makefile...")
    run_cmd("make firmware.bin", cwd=kit_root)
    
    base_size = os.path.getsize(os.path.join(kit_root, "firmware.bin"))
    print(f"[+] Базовий розмір бінарника: {base_size} байтів")
    
    # 3. Емуляція модифікації LGPL-коду клієнтом
    print("[+] Внесення модифікації у вихідний код LGPL-бібліотеки...")
    codec_c = os.path.join(kit_root, "lgpl_src", "codec.c")
    with open(codec_c, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Додавання клієнтського хука
    modified_content = content.replace(
        "/* COMPRESSION_LOGIC */",
        "/* USER_MODIFIED */ volatile int user_hook = 0xABCD1234;\n/* COMPRESSION_LOGIC */"
    )
    with open(codec_c, "w", encoding="utf-8") as f:
        f.write(modified_content)
        
    # 4. Повторне перелінкування
    print("[+] Повторне збирання модифікованої прошивки...")
    run_cmd("make clean && make firmware.bin", cwd=kit_root)
    
    # 5. Перевірка наявності зміненого маркера у скомпільованому бінарнику
    with open(os.path.join(kit_root, "firmware.bin"), "rb") as f:
        bin_data = f.read()
        
    if b"\x34\x12\xcd\xab" in bin_data:
        print(" УСПІХ: Модифікацію виявлено у прошивці. Комплект ліцензійно валідний.")
    else:
        print("❌ ВАДА: Модифікація не потрапила в образ після перелінкування!")
        sys.exit(1)
        
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_relink_kit("customer_relink_bundle.tar.gz")
```

Така автоматизована перевірка повністю виключає людський фактор, гарантує повну відповідність стандарту OpenChain (ISO/IEC 5230) щодо керування відкритим кодом у ланцюгах постачання та доводить юридичну бездоганність комплекту перелінкування перед передачею прошивки на виробничу лінію.
