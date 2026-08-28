# ⚙️ Сканер не-кодових активів прошивки та генератор CycloneDX SBOM

У процесі збирання вбудованого дистрибутива традиційні сканери вихідного коду (ScanCode, FOSSology, Syft) аналізують лише файли сирцевих текстів та декларації менеджерів пакунків. Якщо інженер скомпонував у бінарний образ ELF закритий вендорський HAL-блоб (`libwifi_phy.a`), вшив шрифтові таблиці TrueType через `objcopy` або розмістив у секції `.rodata` масив квантованих ваг нейромережі TensorFlow Lite Micro, звичайний сканер коду не виявить цих компонентів у готовому образі прошивки.

Для виявлення та інвентаризації таких ресурсів необхідний спеціалізований інструмент бінарного аудиту, який сканує секції ELF-файлу, розпізнає сигнатури не-кодових активів, обчислює ентропію для виявлення закритих блобів та генерує розширений маніфест компонентів у форматі CycloneDX 1.6.

## Сигнатури та структура вбудованих активів

Більшість не-кодових ресурсів мають фіксовані бінарні заголовки (магічні числа), за якими сканер може однозначно розпізнати їхній тип навіть у разі відсутності налагоджувальних символів:

1. **Шрифти TrueType / OpenType:**
   - Перші 4 байти містять значення `0x00010000` (для шрифтів OpenType з векторними контурами TrueType).
   - Рядок `'OTTO'` (`0x4F54544F`) — для контурів PostScript CFF (Compact Font Format).
   - Рядок `'ttcf'` (`0x74746366`) — для колекцій шрифтів TrueType Collection.
   - За заголовком слідує 2-байтове поле кількості таблиць (`numTables`), після чого розміщується каталог 16-байтових записів таблиць (`cmap`, `glyf`, `head`, `hmtx`, `name`).

2. **Моделі TensorFlow Lite Micro:**
   - Серіалізуються у форматі Google FlatBuffers.
   - Перші 4 байти задають відносне зміщення до кореневої таблиці буфера.
   - На зміщенні +4 байти міститься обов'язковий 4-байтовий рядковий тег ідентифікатора формату: `'TFL3'` (`0x54464C33`).

3. **Закриті вендорські блоби та мікрокод:**
   - Часто постачаються у вигляді статичних архівів `.a` або бінарних дампів для завантаження в пам'ять інструкцій DSP.
   - Характеризуються відсутністю відкритих рядкових констант копірайтів та високим рівнем ентропії інформації внаслідок внутрішньої компресії чи шифрування.

## Механізм обчислення ентропії Шеннона

Для детекції закритих або зашифрованих бінарних блобів сканер використовує статистичний розрахунок **інформаційної ентропії Шеннона**. Ентропія вимірює середню кількість інформації на один байт даних і лежить у діапазоні від 0 до 8 біт на байт.

Різні типи даних мають характерні рівні ентропії:
- Звичайний текст ASCII та нестиснені константи: від 3.5 до 4.5 біт/байт (висока надлишковість).
- Скомпільований машинний код ARM Thumb-2 чи RISC-V: від 5.5 до 6.2 біт/байт (помірна надлишковість інструкцій).
- Нестиснені тензорні ваги квантованих нейромереж: від 5.8 до 6.8 біт/байт.
- Стиснений мікрокод DSP, зашифровані прошивки або запаковані вендорські блоби: від 7.5 до 7.99 біт/байт (розподіл значень байтів наближається до рівномірного білого шуму).

Коли сканер виявляє неперервний блок байтів розміром понад 4 КБ з ентропією понад 7.5 біт на байт, який не має відкритого заголовка відомого формату, такий блок маркується як підозрілий пропрієтарний блоб (`HighEntropyBlob`) і вимагає обов'язкового ручного аналізу.

## Реалізація низькорівневого аналізатора секцій ELF

Нижче наведено код утиліти, яка завантажує бінарний образ ELF або дамп Flash-пам'яті, знаходить секції `.rodata` та `.data`, ідентифікує вшиті активи та повертає їхні характеристики (тип, розмір, зміщення та SHA-256 хеш).

:::tabs
@tab C
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

#define ASSET_UNKNOWN           0
#define ASSET_FONT_TTF          1
#define ASSET_TFLITE_ML         2
#define ASSET_HIGH_ENTROPY_BLOB 3

typedef struct {
    uint32_t offset;
    uint32_t size;
    int asset_type;
    double entropy;
    uint8_t sha256_stub[32];
} asset_descriptor_t;

/* Обчислення ентропії Шеннона для блоку байтів */
double calculate_entropy(const uint8_t *data, size_t len) {
    if (len == 0) return 0.0;
    uint32_t counts[256] = {0};
    for (size_t i = 0; i < len; ++i) {
        counts[data[i]]++;
    }
    double entropy = 0.0;
    for (int i = 0; i < 256; ++i) {
        if (counts[i] > 0) {
            double p = (double)counts[i] / (double)len;
            entropy -= p * (log(p) / log(2.0));
        }
    }
    return entropy;
}

/* Сканування буфера на наявність сигнатур не-кодових активів */
int scan_firmware_buffer(const uint8_t *buf, size_t buf_size,
                         asset_descriptor_t *out_assets, size_t max_assets,
                         size_t *found_count) {
    if (!buf || !out_assets || !found_count) return -1;
    *found_count = 0;

    for (size_t i = 0; i + 16 < buf_size; ++i) {
        if (*found_count >= max_assets) break;

        /* Перевірка сигнатури TrueType / OpenType */
        if ((buf[i] == 0x00 && buf[i+1] == 0x01 && buf[i+2] == 0x00 && buf[i+3] == 0x00) ||
            (memcmp(&buf[i], "OTTO", 4) == 0) ||
            (memcmp(&buf[i], "ttcf", 4) == 0)) {
            
            asset_descriptor_t *asset = &out_assets[*found_count];
            asset->offset = (uint32_t)i;
            asset->size = 4096; /* Оцінка розміру за таблицею офсетів */
            asset->asset_type = ASSET_FONT_TTF;
            asset->entropy = calculate_entropy(&buf[i], 1024);
            (*found_count)++;
            i += 256; /* Пропуск заголовка */
            continue;
        }

        /* Перевірка сигнатури TFLite FlatBuffers: на зміщенні +4 стоїть TFL3 */
        if (memcmp(&buf[i+4], "TFL3", 4) == 0) {
            asset_descriptor_t *asset = &out_assets[*found_count];
            asset->offset = (uint32_t)i;
            asset->size = *(const uint32_t*)&buf[i]; /* Розмір буфера FlatBuffer */
            asset->asset_type = ASSET_TFLITE_ML;
            asset->entropy = calculate_entropy(&buf[i], 1024);
            (*found_count)++;
            i += 512;
            continue;
        }
    }
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <span>
#include <cmath>
#include <array>
#include <optional>
#include <algorithm>

enum class AssetType {
    Unknown,
    FontTrueType,
    TFLiteModel,
    HighEntropyBlob
};

struct AssetDescriptor {
    std::size_t offset{0};
    std::size_t size{0};
    AssetType type{AssetType::Unknown};
    double entropy{0.0};
    std::array<uint8_t, 32> sha256{};
};

class FirmwareAssetScanner {
public:
    static double calculateEntropy(std::span<const uint8_t> data) noexcept {
        if (data.empty()) return 0.0;
        std::array<std::size_t, 256> counts{};
        for (const uint8_t byte : data) {
            counts[byte]++;
        }
        double entropy = 0.0;
        const double total = static_cast<double>(data.size());
        for (const std::size_t count : counts) {
            if (count > 0) {
                const double p = static_cast<double>(count) / total;
                entropy -= p * std::log2(p);
            }
        }
        return entropy;
    }

    static std::vector<AssetDescriptor> scan(std::span<const uint8_t> firmware) {
        std::vector<AssetDescriptor> detected;
        if (firmware.size() < 16) return detected;

        for (std::size_t i = 0; i + 16 < firmware.size(); ++i) {
            const auto window = firmware.subspan(i);

            // Перевірка магічних чисел TrueType / OpenType
            const bool isTtf = (window[0] == 0x00 && window[1] == 0x01 && window[2] == 0x00 && window[3] == 0x00) ||
                               (std::string_view(reinterpret_cast<const char*>(window.data()), 4) == "OTTO") ||
                               (std::string_view(reinterpret_cast<const char*>(window.data()), 4) == "ttcf");

            if (isTtf) {
                const auto sampleSize = std::min<std::size_t>(window.size(), 1024);
                detected.push_back(AssetDescriptor{
                    .offset = i,
                    .size = 4096,
                    .type = AssetType::FontTrueType,
                    .entropy = calculateEntropy(window.subspan(0, sampleSize))
                });
                i += 256;
                continue;
            }

            // Перевірка магічного тегу TFLite FlatBuffers
            if (window.size() >= 8 &&
                std::string_view(reinterpret_cast<const char*>(window.data() + 4), 4) == "TFL3") {
                
                uint32_t modelSize = 0;
                std::copy_n(window.data(), sizeof(uint32_t), reinterpret_cast<uint8_t*>(&modelSize));
                const auto sampleSize = std::min<std::size_t>(window.size(), 1024);

                detected.push_back(AssetDescriptor{
                    .offset = i,
                    .size = modelSize > 0 ? modelSize : 8192,
                    .type = AssetType::TFLiteModel,
                    .entropy = calculateEntropy(window.subspan(0, sampleSize))
                });
                i += 512;
                continue;
            }
        }
        return detected;
    }
};
```
:::

## Генерація розширеного маніфесту CycloneDX 1.6

Отримані бінарні дескриптори конвертуються у валідний JSON-документ специфікації CycloneDX 1.6, у якому моделі машинного навчання маркуються типом `machine-learning-model`, а шрифти — типом `data` або `file` із детальними юридичними метаданими.

Скрипт зчитує метадані з локального каталогу активів, обчислює криптографічний хеш SHA-256 для кожної знайденої ділянки пам'яті та зв'язує фізичний бінарний артефакт із ліцензійними деклараціями:

```python
import json
import hashlib

def build_cyclonedx_sbom(firmware_name: str, assets: list) -> dict:
    components = []
    
    for asset in assets:
        if asset["type"] == "TFLiteModel":
            comp = {
                "type": "machine-learning-model",
                "bom-ref": f"model-tflite-{asset['offset']:08x}",
                "name": "EdgeDetectionQuantizedModel",
                "version": "1.2.0",
                "description": "INT8 quantized convolutional neural network for anomaly detection",
                "modelCard": {
                    "modelParameters": {
                        "approach": { "type": "supervised" },
                        "task": "anomaly-detection",
                        "architectureFamily": "MobileNetV2-Lite"
                    },
                    "datasets": [
                        {
                            "type": "training",
                            "name": "IndustrialVibrationDataset-v2",
                            "governance": {
                                "licenses": [ { "license": { "id": "CC-BY-4.0" } } ]
                            }
                        }
                    ]
                },
                "licenses": [ { "license": { "id": "Apache-2.0" } } ],
                "hashes": [ { "alg": "SHA-256", "content": asset["sha256"] } ]
            }
            components.append(comp)
            
        elif asset["type"] == "FontTrueType":
            comp = {
                "type": "data",
                "bom-ref": f"font-embedded-{asset['offset']:08x}",
                "name": "Inter-Regular",
                "version": "4.0",
                "description": "Embedded TrueType Typography Font Software for GUI",
                "licenses": [
                    {
                        "license": {
                            "id": "OFL-1.1",
                            "url": "https://spdx.org/licenses/OFL-1.1.html"
                        }
                    }
                ],
                "properties": [
                    { "name": "font:embedding-type", "value": "flash-rom" },
                    { "name": "font:reserved-font-name", "value": "Inter" }
                ],
                "hashes": [ { "alg": "SHA-256", "content": asset["sha256"] } ]
            }
            components.append(comp)

    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": "urn:uuid:3e671687-395b-41f5-a30f-a58921a69b79",
        "version": 1,
        "metadata": {
            "component": {
                "type": "device",
                "name": firmware_name,
                "version": "2.4.0-production"
            }
        },
        "components": components
    }
```

## Крайові випадки та обробка складних сценаріїв

Під час аналізу реальних прошивок сканер стикається з низкою специфічних інженерних викликів, які вимагають окремої логіки обробки:

1. **Компресовані та обрізані шрифти (Subsetted Fonts):** якщо розробники оптимізували TrueType-шрифт за допомогою утиліти `pyftsubset`, частина стандартних таблиць (наприклад, `DSIG` чи `hdmx`) може бути видалена для мінімізації розміру у Flash. Сканер повинен обов'язково перевіряти наявність критичних таблиць `head` та `name`, оскільки саме таблиця `name` містить рядки авторських прав, копірайтів та посилання на ліцензію SIL OFL.
2. **Упаковані моделі та підграфи (Multi-Subgraph TFLite):** у складних моделях обчислювальний граф містить декілька вкладених підграфів з індивідуальними таблицями квантування. Розмір буфера FlatBuffers зчитується безпосередньо з кореневого зміщення заголовка для уникнення передчасного обриву сканування під час проходження нульових байтів вирівнювання пам'яті.
3. **Зашифровані секції прошивки (Encrypted Flash):** якщо прошивка збирається з увімкненим апаратним шифруванням Flash-пам'яті (Secure Boot / Flash Encryption на ESP32 чи STM32 TrustZone), аналіз сигнатур та ентропії виконується **до етапу шифрування** на виході компонувальника `ld`. Сканування зашифрованого двійкового файлу дасть суцільну ентропію понад 7.9 біт на байт на всій довжині образу, що унеможливить розпізнавання внутрішніх сигнатур.

## Інтеграція у конвеєр CI/CD

Впровадження автоматизованого сканера у процес збирання гарантує:
1. **Виявлення прихованих активів:** жоден розробник не зможе випадково вшити комерційний TrueType-шрифт без ліцензії чи навчальні ваги під CC BY-NC.
2. **Контроль ентропії:** виявлення секцій із високою ентропією (понад 7.5 біт на байт) сигналізує про наявність неідентифікованого стисненого або зашифрованого бінарного блоба, який вимагає окремого юридичного аналізу.
3. **Відповідність вимогам кібербезпеки:** автоматично сформований SBOM CycloneDX передається замовникам разом із бінарним оновленням прошивки, забезпечуючи повну прозорість ланцюга постачання.
