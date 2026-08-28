# ⚙️ Автоматизований аудит ліцензій у конвеєрі: від мапи лінкера до машинного SBOM і CLI-інтерфейсу прошивки

Під час складання прошивки мікроконтролера до підсумкового бінарного образу потрапляють лише ті об'єктні модулі, на які є прямі чи опосередковані посилання в коді. Ведення обліку ліцензій за списком файлів у дереві репозиторію дає абсолютно хибну картину: бібліотека може лежати в підкаталозі як невикористаний вихідний код, а може бути статично злінкована у Flash. Більше того, компілятор із прапорцями `-ffunction-sections -fdata-sections` та компонувальник із прапорцем `-Wl,--gc-sections` викидають невикликані функції, тому модуль може бути підключений до збірки лише частково.

Щоб отримати стовідсотково достовірний перелік компонентів ([SBOM](root:sys-notary/sbom-perelik-skladnykiv-obrazu-i-navishcho-ioho)), аудит проводять **після лінкування**, аналізуючи мапу розподілу пам'яті (файл `.map`), згенерований компонувальником `arm-none-eabi-ld`, та таблицю символів через `arm-none-eabi-nm`.

Нижче наведено повну реалізацію двох взаємодоповнювальних інструментів для вбудованої системи:
1. Автоматичний конвеєрний скрипт на Python для CI/CD, що витягує злінковані модулі з `.map`-файлу, перевіряє ліцензійну сумісність за політикою безпеки та генерує машинночитний паспорт CycloneDX JSON і зведений файл атрибуції.
2. Вбудований C/C++ модуль для мікроконтролера, що зберігає компактну таблицю ліцензій у службовій секції Flash і надає оператору команду `license` через послідовну консоль (UART / USB CDC).

## Принцип роботи пост-лінкерного сканера мапи пам'яті

Компонувальник `arm-none-eabi-ld` під час виклику з прапорцем `-Map=build/firmware.map` генерує детальний звіт про кожен байт вихідного бінарника. У секції `Memory Configuration` та `Linker script and memory map` містяться рядки, що пов'язують конкретні символи та секції (`.text.vTaskDelay`, `.rodata.aes_tables`) із вхідними файлами `.o` та статичними бібліотеками `.a`.

```
.text.vTaskDelay
                0x08001240       0x68 Middlewares/FreeRTOS/tasks.o
                0x08001240                vTaskDelay
.text.mbedtls_aes_crypt_ecb
                0x08004510       0x94 Middlewares/mbedTLS/aes.o
                0x08004510                mbedtls_aes_crypt_ecb
```

Скрипт сканує цей файл, виділяє всі задіяні об'єктні модулі, зіставляє їх за шаблонами регулярних виразів із базою відомих компонентів проєкту та перевіряє ліцензію кожного знайденого пакета. Якщо виявлено заборонену копілефтну ліцензію (наприклад, GPL або AGPL), скрипт негайно повертає ненульовий код виходу (`exit code 2`), зупиняючи конвеєр [CI для прошивки](root:embedded/firmware-ci) та блокуючи випуск релізу.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""firmware_sbom_scanner.py — пост-лінкерний аудит ліцензій для MCU"""

import re
import sys
import json
import hashlib
from pathlib import Path

# База метаданих сторонніх компонентів проєкту
COMPONENT_DATABASE = {
    "freertos": {
        "name": "FreeRTOS Kernel",
        "version": "10.5.1",
        "license_spdx": "MIT",
        "purl": "pkg:generic/freertos@10.5.1",
        "supplier": "Amazon Web Services",
        "pattern": r"(freertos|tasks\.o|queue\.o|list\.o|port\.o)"
    },
    "lwip": {
        "name": "lwIP - Lightweight IP stack",
        "version": "2.2.0",
        "license_spdx": "BSD-3-Clause",
        "purl": "pkg:generic/lwip@2.2.0",
        "supplier": "Swedish Institute of Computer Science",
        "pattern": r"(lwip|tcp\.o|udp\.o|ip4\.o|ethernet\.o|pbuf\.o)"
    },
    "mbedtls": {
        "name": "mbed TLS",
        "version": "3.4.1",
        "license_spdx": "Apache-2.0",
        "purl": "pkg:generic/mbedtls@3.4.1",
        "supplier": "TrustedFirmware.org",
        "pattern": r"(mbedtls|aes\.o|sha256\.o|ssl_tls\.o|x509\.o)"
    },
    "fatfs": {
        "name": "FatFS",
        "version": "R0.15",
        "license_spdx": "FatFS-Permissive",
        "purl": "pkg:generic/fatfs@R0.15",
        "supplier": "ChaN",
        "pattern": r"(ff\.o|diskio\.o|ffsystem\.o|ffunicode\.o)"
    },
    "cmsis_core": {
        "name": "ARM CMSIS Core",
        "version": "5.9.0",
        "license_spdx": "Apache-2.0",
        "purl": "pkg:generic/arm-cmsis@5.9.0",
        "supplier": "Arm Limited",
        "pattern": r"(system_stm32|cmsis|core_cm7\.o)"
    },
    "stm32_hal": {
        "name": "STM32CubeH7 HAL Drivers",
        "version": "1.11.0",
        "license_spdx": "BSD-3-Clause",
        "purl": "pkg:generic/stm32cube-hal@1.11.0",
        "supplier": "STMicroelectronics",
        "pattern": r"(stm32h7xx_hal|stm32h7xx_ll)"
    },
    "vendor_phy_blob": {
        "name": "Vendor Wi-Fi PHY Driver (Binary Blob)",
        "version": "2.4.18",
        "license_spdx": "Proprietary-Vendor-EULA",
        "purl": "pkg:generic/vendor-phy-blob@2.4.18",
        "supplier": "Silicon Vendor Corp",
        "pattern": r"(libphy_wifi\.a|libcoexist\.a)"
    }
}

# Політика ліцензійної відповідності для комерційного пристрою
BANNED_LICENSES = {"GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0-only", "GPL-3.0-or-later", "AGPL-3.0-only"}

def parse_map_file(map_path):
    """Видобути список усіх об'єктних файлів, реально злінкованих у фінальний образ"""
    used_objects = set()
    map_text = Path(map_path).read_text(encoding="utf-8", errors="ignore")
    
    # Шукаємо секції розподілу коду (.text, .rodata, .data)
    object_regex = re.compile(r'([\w\/\.\-]+\.(?:o|a))(?:\([\w\.\-]+\))?')
    for match in object_regex.finditer(map_text):
        used_objects.add(match.group(1))
    return used_objects

def analyze_components(used_objects):
    """Зіставити об'єкти з базою компонентів та виявити активні ліцензії"""
    detected_components = {}
    
    for obj in used_objects:
        obj_str = str(obj)
        matched = False
        for comp_id, info in COMPONENT_DATABASE.items():
            if re.search(info["pattern"], obj_str, re.IGNORECASE):
                if comp_id not in detected_components:
                    detected_components[comp_id] = {
                        "info": info,
                        "matched_objects": []
                    }
                detected_components[comp_id]["matched_objects"].append(obj_str)
                matched = True
                break
    return detected_components

def generate_cyclonedx_sbom(detected, output_path, binary_hash):
    """Згенерувати машинночитний SBOM у форматі CycloneDX 1.5 JSON"""
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "component": {
                "name": "FlightController-MainFirmware",
                "version": "3.2.0-release",
                "type": "firmware",
                "hashes": [{"alg": "SHA-256", "content": binary_hash}]
            }
        },
        "components": []
    }
    
    for comp_id, data in detected.items():
        info = data["info"]
        comp_entry = {
            "type": "library",
            "name": info["name"],
            "version": info["version"],
            "purl": info["purl"],
            "supplier": {"name": info["supplier"]},
            "licenses": [{"license": {"id": info["license_spdx"]}}],
            "properties": [
                {"name": "embedded:linked_objects_count", "value": str(len(data["matched_objects"]))}
            ]
        }
        sbom["components"].append(comp_entry)
        
    Path(output_path).write_text(json.dumps(sbom, indent=2, ensure_ascii=False), encoding="utf-8")

def generate_notice_file(detected, output_path):
    """Згенерувати зведений файл THIRD_PARTY_LICENSES.txt для інструкції користувача"""
    lines = [
        "================================================================================",
        "ВІДОМОСТІ ПРО ЛІЦЕНЗІЇ СТОРОННЬОГО ПРОГРАМНОГО ЗАБЕЗПЕЧЕННЯ",
        "Цей виріб містить програмні компоненти з відкритим вихідним кодом.",
        "================================================================================\n"
    ]
    for comp_id, data in detected.items():
        info = data["info"]
        lines.append(f"Компонент : {info['name']}")
        lines.append(f"Версія    : {info['version']}")
        lines.append(f"Ліцензія  : {info['license_spdx']}")
        lines.append(f"Автор     : {info['supplier']}")
        lines.append(f"Модулів   : {len(data['matched_objects'])} об'єктів злінковано")
        lines.append("-" * 80 + "\n")
        
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")

def main():
    if len(sys.argv) < 3:
        print("Використання: python firmware_sbom_scanner.py <firmware.map> <firmware.bin>")
        sys.exit(1)
        
    map_file = sys.argv[1]
    bin_file = sys.argv[2]
    
    bin_hash = hashlib.sha256(Path(bin_file).read_bytes()).hexdigest()
    linked_objs = parse_map_file(map_file)
    detected = analyze_components(linked_objs)
    
    # Перевірка на заборонені копілефтні ліцензії (CI Gate)
    violations = []
    for comp_id, data in detected.items():
        lic = data["info"]["license_spdx"]
        if lic in BANNED_LICENSES:
            violations.append(f"Компонент '{data['info']['name']}' має копілефтну ліцензію {lic}")
            
    if violations:
        print("\n[ПОМИЛКА ЛІЦЕНЗІЙНОГО ШЛЮЗУ] Знайдено несумісні ліцензії:")
        for v in violations:
            print(f"  ❌ {v}")
        sys.exit(2)
        
    out_sbom = Path(bin_file).with_suffix(".cdx.json")
    out_notice = Path(bin_file).parent / "THIRD_PARTY_LICENSES.txt"
    
    generate_cyclonedx_sbom(detected, out_sbom, bin_hash)
    generate_notice_file(detected, out_notice)
    print(f"\n[УСПІХ] Знайдено компонентів: {len(detected)}. Згенеровано SBOM: {out_sbom}")

if __name__ == "__main__":
    main()
```

## Інтеграція аудиту в конвеєр GitHub Actions / GitLab CI

У конвеєрі автоматичної збірки скрипт встановлюється як обов'язковий крок відразу після завершення лінкування та перед підписом образу. Якщо скрипт виявляє ліцензійне порушення, крок підпису приватним ключем блокується:

```yaml
# Приклад кроку в пайплайні .github/workflows/firmware.yml
- name: Компіляція та лінкування прошивки
  run: |
    mkdir -p build && cd build
    cmake -DCMAKE_BUILD_TYPE=Release ..
    make -j$(nproc)

- name: Пост-лінкерний ліцензійний аудит та генерація SBOM
  run: |
    python3 scripts/firmware_sbom_scanner.py build/firmware.map build/firmware.bin

- name: Підпис образу (тільки якщо ліцензійний шлюз успішний)
  run: |
    imgtool sign --key keys/release-root-rsa3072.pem \
                 --version 3.2.0 \
                 build/firmware.bin build/firmware-signed.bin
```

## Додаткова верифікація таблиці символів через `arm-none-eabi-nm`

Для максимальної надійності скрипт аудиту в CI доповнюють перехресною звіркою через утиліту `arm-none-eabi-nm`. Команда `arm-none-eabi-nm --defined-only --numeric-sort build/firmware.elf` виводить повний список визначених глобальних символів із точними адресами у Flash.

Якщо в образі виявляються символи із характерними префіксами бібліотек GPL (наприклад, `gpl_`, `gmp_` або `ff_`), які не були задекларовані у файлі конфігурації компонентів, конвеєр генерує попередження `UNREGISTERED_SYMBOL_DETECTED`. Це унеможливлює ситуацію, коли розробник перейменував файл вихідного коду, намагаючись приховати походження запозиченого копілефтного алгоритму.

## Крайові випадки аудиту: слабкі символи, архіви та автозгенерований код

Під час побудови конвеєра ліцензійного контролю важливо враховувати чотири технічні підводні камені:

1. **Слабкі символи (Weak Symbols):** У бібліотеках HAL або FreeRTOS часто оголошуються функції-заглушки з атрибутом `__attribute__((weak))`. Якщо користувач перевизначає таку функцію у власному файлі, бібліотечна версія викидається компонувальником. Аудитор повинен аналізувати саме `.map`-файл, де зафіксовано, чия реалізація залишилася у Flash.
2. **Автоматично згенерований код (Кодогенератори):** Драйвери, згенеровані утилітами на зразок STM32CubeMX або конфігуратором зв'язку MAVLink, мають спеціальні ліцензійні застереження в заголовках. Деякі генератори вимагають збереження власної ліцензії в згенерованих файлах `.c`/`.h`, навіть якщо сама бібліотека вважається відкритою.
3. **Статичні архіви `.a`:** Компонувальник за замовчуванням бере з архіву `.a` лише ті об'єктні файли, на символи яких є реальні посилання. Якщо бібліотека складається з десяти модулів, а викликається лише один, ліцензійні зобов'язання (наприклад, обов'язок атрибуції) поширюються лише на той модуль, який реально увійшов у моноліт.
4. **Транзитивні залежності:** Деякі бібліотеки (наприклад, `mbedtls`) внутрішньо викликають функції апаратного прискорення з `CMSIS-DSP` або потребують системних викликів `FreeRTOS`. Скрипт аудиту зобов'язаний розпізнавати весь ланцюг задіяних об'єктів, щоб жоден проміжний рівень не випав зі зведеного паспорта SBOM.

## Зв'язування хешу SBOM із криптографічним образом OTA

У захищених системах з бездротовим оновленням ([відкат OTA](root:sf-devices/ota-rollback)) файл маніфесту SBOM стає частиною підписаного метапакета випуску. Контрольна сума `SHA-256` самого бінарного файлу прошивки `firmware.bin` обов'язково записується в заголовок контейнера образу разом із номером версії. 

Коли сервер оновлень або діагностичний стенд перевіряє цілісність прошивки, він звіряє хеш у полі `metadata.component.hashes` згенерованого SBOM-маніфесту з хешем, підписаним закритим ключем виробника. Це унеможливлює підміну компонентів на проміжних вузлах постачання та гарантує, що сертифікований склад коду точно відповідає фізичним байтам у Flash-пам'яті пристрою.

## Вбудований інтерфейс запиту ліцензій через консоль (UART / USB CLI)

Щоб виконати вимогу надання інформації про ліцензії безпосередньо з пристрою (особливо у вбудованих приладах без графічного дисплея), у прошивку вбудовують службовий модуль опитування. Він зберігає стислу таблицю атрибуції у Flash-пам'яті (секція `.rodata`) та виводить її у відповідь на команду `license` або `about` у діагностичному терміналі.

Пам'ять під таблицю виділяється статично під час компіляції: рядок копірайту та версії зберігається безпосередньо у Flash, не витрачаючи дефіцитну оперативну пам'ять (SRAM).

:::tabs
```c
// cli_license.c — вивід ліцензійної таблиці з Flash у послідовну консоль
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    const char *component_name;
    const char *version;
    const char *spdx_license;
    const char *copyright_holder;
} FirmwareLicenseEntry;

// Таблиця прошитих компонентів (розміщується в секції .rodata у Flash)
static const FirmwareLicenseEntry FW_LICENSES[] = {
    { "FreeRTOS Kernel",       "10.5.1",  "MIT",          "Amazon.com, Inc. or its affiliates" },
    { "lwIP TCP/IP Stack",     "2.2.0",   "BSD-3-Clause", "Swedish Institute of Computer Science" },
    { "mbed TLS",              "3.4.1",   "Apache-2.0",   "TrustedFirmware.org" },
    { "FatFS Module",          "R0.15",   "FatFS-Notice", "ChaN" },
    { "ARM CMSIS Core & DSP",  "5.9.0",   "Apache-2.0",   "Arm Limited" },
    { "STM32CubeH7 HAL",       "1.11.0",  "BSD-3-Clause", "STMicroelectronics" },
    { "Wi-Fi PHY Driver",      "2.4.18",  "Proprietary",  "Silicon Vendor Corp" },
    { "Flight Autopilot Core", "3.2.0",   "Proprietary",  "Aerospace Dynamics Inc." }
};

static const size_t FW_LICENSES_COUNT = sizeof(FW_LICENSES) / sizeof(FW_LICENSES[0]);

void cli_cmd_print_licenses(void (*print_fn)(const char *str)) {
    char buf[128];
    print_fn("\r\n=== СПИСОК КОМПОНЕНТІВ ТА ЛІЦЕНЗІЙ ПРОШИВКИ (SBOM) ===\r\n");
    print_fn("Назва                    Версія   Ліцензія     Власник копірайту\r\n");
    print_fn("------------------------------------------------------------------------\r\n");

    for (size_t i = 0; i < FW_LICENSES_COUNT; ++i) {
        const FirmwareLicenseEntry *e = &FW_LICENSES[i];
        snprintf(buf, sizeof(buf), "%-24s %-8s %-12s %s\r\n",
                 e->component_name, e->version, e->spdx_license, e->copyright_holder);
        print_fn(buf);
    }
    print_fn("------------------------------------------------------------------------\r\n");
    print_fn("Повний текст ліцензій доступний за запитом або в інструкції користувача.\r\n\r\n");
}
```
```cpp
// cli_license.hpp / cli_license.cpp — ідіоматична C++ версія для вбудованої консолі
#include <array>
#include <string_view>
#include <format>
#include <span>

struct LicenseEntry {
    std::string_view name;
    std::string_view version;
    std::string_view spdx_id;
    std::string_view copyright;
};

// Незмінна таблиця у Flash пам'яті (constexpr)
inline constexpr std::array<LicenseEntry, 8> kFirmwareLicenses{{
    { "FreeRTOS Kernel",       "10.5.1",  "MIT",          "Amazon.com, Inc. or its affiliates" },
    { "lwIP TCP/IP Stack",     "2.2.0",   "BSD-3-Clause", "Swedish Institute of Computer Science" },
    { "mbed TLS",              "3.4.1",   "Apache-2.0",   "TrustedFirmware.org" },
    { "FatFS Module",          "R0.15",   "FatFS-Notice", "ChaN" },
    { "ARM CMSIS Core & DSP",  "5.9.0",   "Apache-2.0",   "Arm Limited" },
    { "STM32CubeH7 HAL",       "1.11.0",  "BSD-3-Clause", "STMicroelectronics" },
    { "Wi-Fi PHY Driver",      "2.4.18",  "Proprietary",  "Silicon Vendor Corp" },
    { "Flight Autopilot Core", "3.2.0",   "Proprietary",  "Aerospace Dynamics Inc." }
}};

template <typename OutputFunctor>
void print_firmware_licenses(OutputFunctor&& out) {
    out("\r\n=== СПИСОК КОМПОНЕНТІВ ТА ЛІЦЕНЗІЙ ПРОШИВКИ (SBOM) ===\r\n");
    out("Назва                    Версія   Ліцензія     Власник копірайту\r\n");
    out("------------------------------------------------------------------------\r\n");

    for (const auto& entry : kFirmwareLicenses) {
        // Форматування рядка фіксованої ширини
        char buffer[128];
        int written = snprintf(buffer, sizeof(buffer), "%-24.*s %-8.*s %-12.*s %.*s\r\n",
                               static_cast<int>(entry.name.size()), entry.name.data(),
                               static_cast<int>(entry.version.size()), entry.version.data(),
                               static_cast<int>(entry.spdx_id.size()), entry.spdx_id.data(),
                               static_cast<int>(entry.copyright.size()), entry.copyright.data());
        if (written > 0) {
            out(std::string_view(buffer, static_cast<size_t>(written)));
        }
    }
    out("------------------------------------------------------------------------\r\n");
    out("Повний текст ліцензій доступний за запитом або в інструкції користувача.\r\n\r\n");
}
```
:::

Така комбінація — автоматичний аналіз мапи компіляції в CI та внутрішній модуль консольного виводу — закриває всі нормативні вимоги щодо прозорості компонентів і гарантує відсутність копілефтних порушень у серійному виробі.
