# 📋 Специфікація маніфестів SBOM для вбудованих прошивок: формати SPDX та CycloneDX

Сучасні регуляторні стандарти безпеки вбудованих систем (зокрема європейський регламент кіберстійкості Cyber Resilience Act — CRA / Regulation (EU) 2024/2847, директива радіообладнання RED 3.3, стандарт споживчої безпеки EN 303 645 та американський указ Executive Order 14028) вимагають обов'язкової наявності машинночитних маніфестів програмного складу ([SBOM](root:sys-notary/sbom-perelik-skladnykiv-obrazu-i-navishcho-ioho)) для кожного випущеного апаратного виробу.

Для прошивок мікроконтролерів використовують два стандартизовані формати: **CycloneDX** (спеціалізований для ланцюгів постачання, аналізу вразливостей VEX, апаратного складу HBOM та кібербезпеки) та **SPDX** (міжнародний стандарт ISO/IEC 5230:2020, оптимізований для юридичного та ліцензійного аудиту). Нижче наведено структуру обов'язкових полів, синтаксис ліцензійних виразів, схеми ідентифікації через PURL/CPE, апаратні розширення HBOM/CBOM, правила експортного контролю та адаптовані схеми маніфестів для статично скомпільованих бінарних образів у Flash-пам'яті мікроконтролера.

## Регуляторні вимоги: сім мінімальних елементів NTIA

Національне управління телекомунікацій та інформації США (NTIA — National Telecommunications and Information Administration) встановило стандарт мінімальних обов'язкових елементів для будь-якого валідного SBOM. Кожен генератор маніфестів для вбудованих систем зобов'язаний заповнювати такі сутності:

1. **Постачальник (Supplier Name):** Назва організації або автора, що створили компонент (наприклад, `Amazon Web Services`, `STMicroelectronics`, `Arm Limited`).
2. **Назва компонента (Component Name):** Стандартизоване ім'я бібліотеки чи модуля (наприклад, `FreeRTOS Kernel`, `mbedtls`, `stm32h7-hal`).
3. **Версія (Version of the Component):** Точний семантичний тег або версія релізу (`10.5.1`, `3.4.1`).
4. **Унікальні ідентифікатори (Other Unique Identifiers):** Загальновизнані схеми ідентифікації — Package URL (PURL) та Common Platform Enumeration (CPE), що дозволяють автоматичним сканерам звіряти компонент із базами вразливостей CVE (NIST NVD).
5. **Зв'язок залежностей (Dependency Relationship):** Тип відношення між кореневим образом прошивки та підпорядкованими бібліотеками (`CONTAINS`, `DEPENDS_ON`).
6. **Автор маніфесту (Author of SBOM Data):** Інженерна команда, компанія або автоматичний інструмент CI/CD, що сформував документ.
7. **Мітка часу (Timestamp):** Дата й точний час генерації маніфесту у форматі UTC (ISO 8601).

## Синтаксис та алгебра ліцензійних виразів SPDX (SPDX License Expressions)

Ліцензія кожного компонента в маніфесті обов'язково посилається на стандартизований короткий ідентифікатор із загальноприйнятого реєстру SPDX License List. У вбудованих системах часто виникають ситуації, коли один компонент містить вихідники під різними ліцензіями або надає право вибору. Для точного опису таких умов використовують формальну граматику з логічними операторами та круглими дужками:

| Оператор / Модифікатор | Пріоритет | Юридичне значення | Приклад застосування в прошивці |
|---|---|---|---|
| `WITH <виняток>` | 1 (найвищий) | Базова ліцензія з офіційним винятком правовласника | `Apache-2.0 WITH LLVM-exception` |
| `AND` | 2 (середній) | Кон'юнкція: одночасне виконання умов усіх зазначених ліцензій | `MIT AND BSD-3-Clause` (для складеного драйвера) |
| `OR` | 3 (найнижчий) | Диз'юнкція: право розробника обрати одну з ліцензій (Dual Licensing) | `GPL-2.0-only OR Apache-2.0` |
| `+` (суфікс) | — | Дозвіл використовувати зазначену або будь-яку новішу версію ліцензії | `GPL-2.0+` |

```
Приклад складного виразу:
(MIT OR Apache-2.0 WITH LLVM-exception) AND BSD-3-Clause
[Означає: розробник обирає між MIT та Apache з LLVM-винятком, але обов'язково
виконує вимоги ліцензії BSD-3-Clause для додаткової частини файлів]
```

> ⚠️ **Виняток FreeRTOS Exception:** До версії 10.0.0 ядро FreeRTOS ліцензувалося під модифікованою версією GPLv2 із явним дозволом не відкривати власний закритий код при статичному лінкуванні. В ідентифікаторах SPDX цей виняток має офіційну назву `GPL-2.0-only WITH FreeRTOS-exception-2.0`. Починаючи з версії 10, FreeRTOS повністю перейшов на чисту ліцензію `MIT`.

## Специфікація PURL та CPE для мікроконтролерних компонентів

Щоб автоматизовані системи кібербезпеки могли зв'язати прошивку з базами відомих вразливостей (CVE), кожен компонент маркується універсальними ідентифікаторами:

1. **Package URL (PURL):** Стандарт формату URL для програмних пакетів. Для мікроконтролерів використовують схеми `pkg:generic`, `pkg:github` або `pkg:gitlab`:
   - `pkg:generic/freertos-kernel@10.5.1?download_url=https://github.com/FreeRTOS/FreeRTOS-Kernel`
   - `pkg:generic/lwip@2.2.0?checksum=sha256:87654321...`
   - `pkg:github/Mbed-TLS/mbedtls@3.4.1`

2. **Common Platform Enumeration (CPE 2.3):** Схема ідентифікації апаратного та програмного забезпечення від NIST:
   - `cpe:2.3:o:amazon:freertos:10.5.1:*:*:*:*:*:*:*` — операційна система;
   - `cpe:2.3:a:arm:cmsis_dsp:5.9.0:*:*:*:*:*:*:*` — прикладний модуль;
   - `cpe:2.3:h:st:stm32h743zi:-:*:*:*:*:*:*:*` — апаратний чипсет (Hardware CPE).

## Апаратний профіль (HBOM) та криптографічний склад (CBOM) у CycloneDX

Особливістю вбудованих пристроїв є нерозривний зв'язок між мікропрограмою та фізичною платою. Специфікація CycloneDX версії 1.5 дозволяє описувати не лише код, а й супутні апаратні та криптографічні сутності:

1. **Hardware BOM (HBOM):** Опис фізичних мікросхем на друкованій платі (мікроконтролер, зовнішня Flash-пам'ять QSPI, захищений крипточип Secure Element, трансивери шини CAN або PHY Ethernet). Це дозволяє аудиторам безпеки відстежувати апаратні ревізії кремнію та відомі апаратні помилки (Errata).
2. **Cryptographic BOM (CBOM):** Каталог криптографічних алгоритмів, сертифікатів та ключів, вшитих у прошивку або реалізованих апаратними прискорювачами (AES-256-GCM, ECDSA secp256r1, SHA-256). Такий аудит вимагається стандартами безпеки для перевірки стійкості до квантових загроз (Post-Quantum Cryptography readiness).

## Експортний контроль та класифікація шифрування (ECCN)

У маніфестах для польотних контролерів та пристроїв подвійного призначення (Dual-Use) обов'язково зазначають параметри експортного контролю згідно з важелями Вассенаарських домовленостей (Wassenaar Arrangement) та правилами EAR (Export Administration Regulations США).

Якщо прошивка містить модуль симетричного шифрування з довжиною ключа понад 56 біт або асиметричного понад 512 біт (наприклад, `mbedtls` із підтримкою AES-256 чи ECDSA-384), маніфест доповнюють спеціальною властивістю:
- `embedded:export_control:eccn` зі значенням `5D002` (програмне забезпечення для забезпечення інформаційної безпеки) або `5D992` (масове комерційне шифрування);
- `embedded:crypto:strength_bits` зі значенням довжини робочого ключа (наприклад, `256`).

Ці метадані дозволяють митним брокерам та службам експортного аудиту автоматично перевіряти дозвільну документацію партії при перетині кордону без затримки вантажу.

## Специфікація схеми CycloneDX 1.5 JSON для мікроконтролерної прошивки

Формат CycloneDX структурує маніфест за розділами: метадані кореневого бінарного образу (`metadata.component`), масив використаних бібліотек (`components`) та залежності. Для мікроконтролерів критично фіксувати апаратні адреси у Flash та прапорець статичного лінкування через блок `properties`.

```json
{
  "$schema": "http://cyclonedx.org/schema/bom-1.5.schema.json",
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:7f3b891a-9c42-4b2a-8d13-6d0e82c5f110",
  "version": 1,
  "metadata": {
    "timestamp": "2026-08-28T00:00:00Z",
    "tools": [
      {
        "vendor": "Aerospace Dynamics",
        "name": "firmware-sbom-pipeline",
        "version": "1.4.0"
      }
    ],
    "component": {
      "type": "firmware",
      "bom-ref": "pkg:generic/drone-flight-controller@3.2.0",
      "supplier": {
        "name": "Aerospace Dynamics Inc.",
        "url": ["https://aerospace-dynamics.example.com"]
      },
      "name": "FlightController-MainFirmware",
      "version": "3.2.0-release",
      "description": "Монолітний образ польотного контролера для мікроконтролера STM32H743",
      "hashes": [
        {
          "alg": "SHA-256",
          "content": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        }
      ],
      "licenses": [
        {
          "license": {
            "name": "Proprietary Commercial Hardware EULA"
          }
        }
      ],
      "properties": [
        { "name": "embedded:target_arch", "value": "arm-cortex-m7" },
        { "name": "embedded:flash_base_address", "value": "0x08000000" },
        { "name": "embedded:flash_size_bytes", "value": "1048576" },
        { "name": "embedded:secure_boot_signed", "value": "true" },
        { "name": "embedded:export_control:eccn", "value": "5D002" }
      ]
    }
  },
  "components": [
    {
      "type": "library",
      "bom-ref": "pkg:generic/freertos-kernel@10.5.1",
      "supplier": { "name": "Amazon Web Services" },
      "name": "FreeRTOS Kernel",
      "version": "10.5.1",
      "description": "Планувальник задач реального часу для ARM Cortex-M",
      "scope": "required",
      "hashes": [
        { "alg": "SHA-256", "content": "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0" }
      ],
      "licenses": [
        { "license": { "id": "MIT" } }
      ],
      "purl": "pkg:generic/freertos-kernel@10.5.1",
      "cpe": "cpe:2.3:o:amazon:freertos:10.5.1:*:*:*:*:*:*:*",
      "properties": [
        { "name": "embedded:linkage", "value": "static" },
        { "name": "embedded:flash_section", "value": ".text.freertos" }
      ]
    },
    {
      "type": "library",
      "bom-ref": "pkg:generic/lwip@2.2.0",
      "supplier": { "name": "Swedish Institute of Computer Science" },
      "name": "lwIP TCP/IP Stack",
      "version": "2.2.0",
      "licenses": [
        { "license": { "id": "BSD-3-Clause" } }
      ],
      "purl": "pkg:generic/lwip@2.2.0",
      "properties": [
        { "name": "embedded:linkage", "value": "static" }
      ]
    },
    {
      "type": "library",
      "bom-ref": "pkg:generic/mbedtls@3.4.1",
      "supplier": { "name": "TrustedFirmware.org" },
      "name": "mbed TLS",
      "version": "3.4.1",
      "licenses": [
        { "license": { "id": "Apache-2.0" } }
      ],
      "purl": "pkg:generic/mbedtls@3.4.1",
      "properties": [
        { "name": "embedded:linkage", "value": "static" }
      ]
    },
    {
      "type": "library",
      "bom-ref": "pkg:generic/vendor-wifi-phy-blob@2.4.18",
      "supplier": { "name": "Silicon Vendor Corp" },
      "name": "Vendor Wi-Fi PHY Driver (Binary Blob)",
      "version": "2.4.18",
      "description": "Закритий скомпільований об'єктний архів для керування радіотрактом",
      "licenses": [
        {
          "license": {
            "name": "Silicon Vendor Restrictive Binary EULA"
          }
        }
      ],
      "purl": "pkg:generic/vendor-wifi-phy-blob@2.4.18",
      "properties": [
        { "name": "embedded:binary_blob", "value": "true" },
        { "name": "embedded:source_available", "value": "false" }
      ]
    }
  ]
}
```

## Специфікація формату SPDX 2.3 (Tag-Value) для прошивок

Текстове подання SPDX у форматі `tag-value` є компактним і легко обробляється простими вбудованими утилітами або консольними скриптами на хості.

```spdx
SPDXVersion: SPDX-2.3
DataLicense: CC0-1.0
SPDXID: SPDXRef-DOCUMENT
DocumentName: FlightController-MainFirmware-3.2.0
DocumentNamespace: http://spdx.org/spdxdocs/flight-controller-3.2.0-7f3b891a
Creator: Organization: Aerospace Dynamics Inc.
Creator: Tool: firmware-sbom-pipeline-1.4.0
Created: 2026-08-28T00:00:00Z

##### Package: Main Firmware Monolith
PackageName: FlightController-MainFirmware
SPDXID: SPDXRef-Package-Firmware
PackageVersion: 3.2.0
PackageSupplier: Organization: Aerospace Dynamics Inc.
PackageDownloadLocation: NOASSERTION
FilesAnalyzed: false
PackageChecksum: SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
PackageLicenseConcluded: LicenseRef-Proprietary-EULA
PackageLicenseDeclared: LicenseRef-Proprietary-EULA
PackageCopyrightText: Copyright (c) 2026 Aerospace Dynamics Inc.

##### Package: FreeRTOS Kernel
PackageName: FreeRTOS Kernel
SPDXID: SPDXRef-Package-FreeRTOS
PackageVersion: 10.5.1
PackageSupplier: Organization: Amazon Web Services
PackageDownloadLocation: https://github.com/FreeRTOS/FreeRTOS-Kernel
FilesAnalyzed: false
PackageLicenseConcluded: MIT
PackageLicenseDeclared: MIT
PackageCopyrightText: Copyright (C) 2021 Amazon.com, Inc. or its affiliates.

##### Package: mbed TLS
PackageName: mbed TLS
SPDXID: SPDXRef-Package-mbedTLS
PackageVersion: 3.4.1
PackageSupplier: Organization: TrustedFirmware.org
PackageDownloadLocation: https://github.com/Mbed-TLS/mbedtls
FilesAnalyzed: false
PackageLicenseConcluded: Apache-2.0
PackageLicenseDeclared: Apache-2.0
PackageCopyrightText: Copyright The Mbed TLS Contributors

##### Package: Silicon Vendor Wi-Fi Blob
PackageName: Vendor Wi-Fi PHY Driver
SPDXID: SPDXRef-Package-VendorBlob
PackageVersion: 2.4.18
PackageSupplier: Organization: Silicon Vendor Corp
PackageDownloadLocation: NOASSERTION
FilesAnalyzed: false
PackageLicenseConcluded: LicenseRef-SiliconVendor-EULA
PackageLicenseDeclared: LicenseRef-SiliconVendor-EULA
PackageCopyrightText: Copyright (c) 2024 Silicon Vendor Corp. All rights reserved.

##### Relationships
Relationship: SPDXRef-Package-Firmware CONTAINS SPDXRef-Package-FreeRTOS
Relationship: SPDXRef-Package-Firmware CONTAINS SPDXRef-Package-mbedTLS
Relationship: SPDXRef-Package-Firmware CONTAINS SPDXRef-Package-VendorBlob
```

## Порівняльна таблиця полів CycloneDX та SPDX

Для налаштування крос-конвертації маніфестів у конвеєрі використовують пряме зіставлення полів обох стандартів:

| Сутність NTIA | Поле в CycloneDX 1.5 | Поле в SPDX 2.3 / 3.0 | Призначення у вбудованій системі |
|---|---|---|---|
| Кореневий бінарник | `metadata.component` | `SPDXRef-Package-Firmware` | Головний образ `firmware.bin` у Flash |
| Бібліотека / Блоб | `components[i]` | `SPDXRef-Package-<name>` | Окремий статично злінкований `.o`/`.a` модуль |
| Постачальник | `supplier.name` | `PackageSupplier` | Автор чи правовласник стороннього коду |
| Ліцензійний вираз | `licenses[i].license.id` | `PackageLicenseConcluded` | Ідентифікатор SPDX або комерційна угода |
| Хеш бінарника | `hashes[i].content` | `PackageChecksum` | Контрольна сума SHA-256 для звірки з образом |
| Package URL | `purl` | `ExternalRef: PACKAGE-MANAGER purl` | Стандартне глобальне посилання на пакет |
| Апаратний CPE | `cpe` | `ExternalRef: SECURITY cpe23Type` | Прив'язка до бази вразливостей NVD |
| Зв'язок зшивання | `dependencies[i]` | `Relationship: CONTAINS` | Факт статичного лінкування в один образ |

## Валідація маніфестів у конвеєрі CI/CD

Формування маніфесту вважається завершеним лише після проходження автоматичної валідації схеми. Для цього в конвеєрі релізної збірки виконують офіційні утиліти перевірки синтаксису:
- Для CycloneDX: `cyclonedx-cli validate --input-file firmware.cdx.json --input-version v1_5`
- Для SPDX: `spdx-tools-java -verify firmware.spdx`

Успішна валідація гарантує, що сформований паспорт прошивки безпомилково прочитають регуляторні аудитори та автоматичні платформи моніторингу ланцюгів постачання.
