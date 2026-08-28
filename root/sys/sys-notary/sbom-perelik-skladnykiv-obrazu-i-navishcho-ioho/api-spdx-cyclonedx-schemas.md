# Специфікація структур даних SBOM: моделі SPDX 2.3/3.0 та CycloneDX 1.5/1.6

Специфікація машиночитних відомостей про склад програмного забезпечення (Software Bill of Materials, SBOM) стандартизує опис компонентів, файлів, залежностей та ліцензійних умов у вигляді серіалізованого графа (JSON, XML або YAML). У сучасній інженерній практиці домінують два взаємодоповнювальні стандарти: **SPDX (ISO/IEC 5962:2021)** від Linux Foundation та **CycloneDX** від консорціуму OWASP.

Кожен документ SBOM виконує роль цифрового паспорта двійкового артефакту, прошивки або контейнерного образу. Нижче наведено формальну специфікацію полів, схем ідентифікації та графів зв'язків для обох стандартів.

## 1. Метадані документа та ідентифікація образу

Верхньорівневий об'єкт маніфесту фіксує контекст створення SBOM, версію стандарту, унікальний глобальний ідентифікатор документа та інформацію про інструмент генерації.

У стандарті CycloneDX кореневий об'єкт містить обов'язковий блок метаданих `metadata`, де вказується час збірки за стандартом ISO 8601 (UTC), перелік утиліт генерації з точними версіями, а також кореневий компонент образу (наприклад, операційна система або прошивка мікроконтролера). Унікальність екземпляра гарантується полем `serialNumber`, яке формується як UUID 4-ї версії.

```json
{
  "$schema": "http://cyclonedx.org/schema/bom-1.5.schema.json",
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:3e671687-395b-41f5-a30f-a58921a69b79",
  "version": 1,
  "metadata": {
    "timestamp": "2026-08-28T00:00:00Z",
    "tools": [
      {
        "vendor": "OpenEmbedded",
        "name": "create-spdx",
        "version": "5.0"
      }
    ],
    "component": {
      "bom-ref": "pkg:yocto/gateway-image-minimal@2.4.1?arch=cortexa53",
      "type": "operating-system",
      "name": "gateway-image-minimal",
      "version": "2.4.1"
    }
  }
}
```

У стандарті SPDX версії 2.3 коренева структура вимагає обов'язкової ліцензії на самі метадані `dataLicense` (суворо `CC0-1.0` відповідно до специфікації ISO), унікального простору імен `documentNamespace` (URI, що поєднує домен організації, ім'я продукту та криптографічний хеш або UUID), а також блоку створення `creationInfo`.

```json
{
  "spdxVersion": "SPDX-2.3",
  "dataLicense": "CC0-1.0",
  "SPDXID": "SPDXRef-DOCUMENT",
  "name": "gateway-image-minimal-2.4.1",
  "documentNamespace": "https://company.internal/spdx/gateway-image-2.4.1-3e671687",
  "creationInfo": {
    "created": "2026-08-28T00:00:00Z",
    "creators": [
      "Tool: BitBake-create-spdx-5.0",
      "Organization: Edge Systems Inc."
    ],
    "licenseListVersion": "3.23"
  }
}
```

| Поле концепції | SPDX 2.3 | CycloneDX 1.5/1.6 | Призначення |
|---|---|---|---|
| **Версія специфікації** | `spdxVersion` (напр. `"SPDX-2.3"`) | `specVersion` (напр. `"1.5"`) | Визначає семантичну схему парсингу документа. |
| **Ліцензія метаданих** | `dataLicense` (суворо `"CC0-1.0"`) | Не вимагається (мається на увазі CC0/Public) | Юридичний дозвіл на машинну обробку та поширення SBOM. |
| **Унікальний простір імен** | `documentNamespace` (URI) | `serialNumber` (URN UUID) | Гарантує глобальну унікальність екземпляра паспорта. |
| **Атрибуція генератора** | `creationInfo.creators` (масив) | `metadata.tools` (структурований список) | Фіксація білд-системи, версії генератора та автора. |

У новітній моделі SPDX 3.0 архітектура зазнала радикальної модернізації: замість єдиного монолітного документа введено концепцію елементів (*Elements*). Кожен елемент (пакет, файл, ліцензія, утиліта збірки або сесія компіляції) є самостійним вузлом графа із власним IRI (Internationalized Resource Identifier). Це дозволяє об'єднувати маніфести різних підсистем без переписування ідентифікаторів.

## 2. Модель опису компонента та схеми ідентифікації

Компонент (у CycloneDX) або пакет (у SPDX) є атомарною одиницею програмного образу: бібліотекою, ядром ОС, статичним архівом `.a`, драйвером або двійковим бінарником.

Для точної ідентифікації використовують два стандартизовані зовнішні покажчики:
1. **Package URL (PURL)** — канонічний URI відповідно до специфікації `github.com/package-url/purl-spec` у форматі `pkg:<type>/<namespace>/<name>@<version>?<qualifiers>#<subpath>`. Тип визначає екосистему пакунків (`deb`, `rpm`, `apk`, `maven`, `cargo`, `pypi`, `generic`), простір імен задає дистрибутив або організацію, а кваліфікатори передають архітектуру (`arch=arm64`), канал дистрибуції або хеш джерела.
2. **Common Platform Enumeration (CPE 2.3)** — формалізований рядок NIST для зіставлення з базою вразливостей NVD у форматі `cpe:2.3:<part>:<vendor>:<product>:<version>:<update>:<edition>:<language>:<sw_edition>:<target_sw>:<target_hw>:<other>`.

### Специфікація компонента в CycloneDX (JSON)

У CycloneDX поле `type` класифікує сутність: `application` (застосунок), `framework` (фреймворк), `library` (бібліотека), `container` (контейнер), `operating-system` (ОС), `firmware` (прошивка), `device` (апаратний блок) або `file` (окремий файл). Поле `bom-ref` слугує локальним унікальним ключем для побудови дерева залежностей.

```json
{
  "components": [
    {
      "bom-ref": "pkg:deb/debian/libssl3@3.0.11-1~deb12u2?arch=arm64",
      "type": "library",
      "name": "libssl3",
      "version": "3.0.11-1~deb12u2",
      "supplier": {
        "name": "Debian Project",
        "url": ["https://www.debian.org"]
      },
      "hashes": [
        {
          "alg": "SHA-256",
          "content": "8b51d6a89c4501a3512e0f0653b47f44a30e7ee9a278912e584f23b2bca6df90"
        }
      ],
      "licenses": [
        {
          "license": {
            "id": "Apache-2.0"
          }
        }
      ],
      "purl": "pkg:deb/debian/libssl3@3.0.11-1~deb12u2?arch=arm64",
      "cpe": "cpe:2.3:a:openssl:openssl:3.0.11:*:*:*:*:*:*:*",
      "externalReferences": [
        {
          "type": "vcs",
          "url": "git+https://github.com/openssl/openssl.git@openssl-3.0.11"
        }
      ]
    }
  ]
}
```

### Специфікація пакета в SPDX 2.3 (JSON)

У форматі SPDX кожен пакет ідентифікується унікальним рядком `SPDXID`, що починається з префікса `SPDXRef-Package-`. Важливою особливістю SPDX є явне розрізнення двох типів ліцензій:
- `licenseDeclared` — ліцензія, офіційно задекларована авторами в маніфесті пакунка або заголовках репозиторію;
- `licenseConcluded` — ліцензійний висновок, зроблений автоматичним сканером або юристом за результатами аудиту всіх вихідних файлів (може відрізнятися від задекларованої через наявність сторонніх включень під іншими ліцензіями).

```json
{
  "packages": [
    {
      "SPDXID": "SPDXRef-Package-libssl3",
      "name": "libssl3",
      "versionInfo": "3.0.11-1~deb12u2",
      "packageSupplier": "Organization: Debian Project",
      "packageDownloadLocation": "https://deb.debian.org/debian/pool/main/o/openssl/libssl3_3.0.11-1_arm64.deb",
      "filesAnalyzed": false,
      "checksums": [
        {
          "algorithm": "SHA256",
          "checksumValue": "8b51d6a89c4501a3512e0f0653b47f44a30e7ee9a278912e584f23b2bca6df90"
        }
      ],
      "licenseConcluded": "Apache-2.0",
      "licenseDeclared": "Apache-2.0",
      "licenseComments": "Licensing verified from source headers and upstream LICENSE",
      "externalRefs": [
        {
          "referenceCategory": "PACKAGE-MANAGER",
          "referenceType": "purl",
          "referenceLocator": "pkg:deb/debian/libssl3@3.0.11-1~deb12u2?arch=arm64"
        },
        {
          "referenceCategory": "SECURITY",
          "referenceType": "cpe23Type",
          "referenceLocator": "cpe:2.3:a:openssl:openssl:3.0.11:*:*:*:*:*:*:*"
        }
      ]
    }
  ]
}
```

## 3. Графові відношення та типи зв'язків

Плоский список компонентів не дає змоги визначити, як саме компонент потрапив у кінцевий двійковий файл: як пряма залежність кореневої програми, як статично скомпільований шматок коду чи як допоміжна утиліта збірки хоста.

Графова модель відношень дозволяє розрізняти контексти використання. Наприклад, якщо бібліотека `mbedtls` влінкована статично (`STATIC_LINK`), її машинний код стає частиною бінарника демона телеметрії, що змінює модель ліцензійного зараження. Якщо ж бібліотека `libsqlite3` підключається динамічно (`DYNAMIC_LINK`), операційна система завантажує її окремим файлом під час старту процесу через динамічний компонувальник `ld-linux.so`.

### Типи зв'язків у SPDX

SPDX описує граф через явний масив `relationships`. Кожен запис фіксує спрямований зв'язок від `spdxElementId` до `relatedSpdxElement`:

```json
{
  "relationships": [
    {
      "spdxElementId": "SPDXRef-DOCUMENT",
      "relationshipType": "DESCRIBES",
      "relatedSpdxElement": "SPDXRef-Package-RootFS"
    },
    {
      "spdxElementId": "SPDXRef-Package-TelemetryApp",
      "relationshipType": "STATIC_LINK",
      "relatedSpdxElement": "SPDXRef-Package-mbedtls"
    },
    {
      "spdxElementId": "SPDXRef-Package-TelemetryApp",
      "relationshipType": "DYNAMIC_LINK",
      "relatedSpdxElement": "SPDXRef-Package-libsqlite3"
    },
    {
      "spdxElementId": "SPDXRef-Package-TelemetryApp",
      "relationshipType": "DEPENDS_ON",
      "relatedSpdxElement": "SPDXRef-Package-musl"
    },
    {
      "spdxElementId": "SPDXRef-Package-FirmwareBin",
      "relationshipType": "GENERATED_FROM",
      "relatedSpdxElement": "SPDXRef-Package-FirmwareSource"
    }
  ]
}
```

### Дерево залежностей у CycloneDX

CycloneDX використовує блок `dependencies`, де кожен вузол посилається на `bom-ref` батьківського компонента та містить список прямих дочірніх залежностей `dependsOn`:

```json
{
  "dependencies": [
    {
      "ref": "pkg:yocto/gateway-image-minimal@2.4.1",
      "dependsOn": [
        "pkg:deb/debian/telemetry-daemon@1.2.0",
        "pkg:deb/debian/musl@1.2.4"
      ]
    },
    {
      "ref": "pkg:deb/debian/telemetry-daemon@1.2.0",
      "dependsOn": [
        "pkg:deb/debian/libsqlite3@3.40.1",
        "pkg:generic/mbedtls@3.4.0"
      ]
    }
  ]
}
```

Завдяки такій деревоподібній структурі сканери безпеки можуть рекурсивно обчислювати транзитивне замикання графа залежностей і визначати точний ланцюжок викликів, який призвів до затягування вразливого пакета в образ.

## 4. Специфікація VEX (Vulnerability Exploitability eXchange)

VEX розширює SBOM можливістю передачі оцінки вразливостей від постачальника ПЗ до споживача. Блок VEX описує, чи становить знайдена CVE реальну загрозу для конкретного продукту.

Коли автоматизований сканер виявляє застарілу версію компонента з відомими CVE, він звіряє отримані ідентифікатори з секцією `vulnerabilities` або окремим файлом OpenVEX. Якщо постачальник підтвердив статус `not_affected` із належним технічним обґрунтуванням, сканер не генерує тривогу та не блокує автоматичний процес випуску релізу.

Стандартизовані стани аналізу (`state`):
- `not_affected` — продукт не вразливий (вимагає обов'язкового поля `justification`).
- `affected` — вразливість підтверджено, експлуатація можлива.
- `fixed` — вразливість усунуто в даній версії або накладено бекпорт-патч.
- `under_investigation` — аналіз впливу триває.

Офіційні причини невразливості (`justification` за стандартом NTIA/CycloneDX):
- `code_not_present` — код вразливої підсистеми видалено або вимкнено під час компіляції (`#ifdef`).
- `code_not_reachable` — вразлива функція присутня в бінарнику, але не викликається за жодних шляхів виконання.
- `requires_configuration` — для експлуатації потрібна специфічна конфігурація, яка відсутня в пристрої.
- `requires_dependency` — атака вимагає наявності додаткової залежності, яка не встановлена в образі.
- `requires_environment` — вразливість потребує зовнішнього оточення, недоступного в системі.
- `protected_by_mitigation` — атаку нейтралізовано зовнішніми захисними бар'єрами (AppArmor, seccomp, SELinux).

### Приклад VEX-секції в CycloneDX 1.5

```json
{
  "vulnerabilities": [
    {
      "id": "CVE-2023-38545",
      "source": {
        "name": "NVD",
        "url": "https://nvd.nist.gov/vuln/detail/CVE-2023-38545"
      },
      "ratings": [
        {
          "source": { "name": "NVD" },
          "score": 9.8,
          "severity": "critical",
          "method": "CVSSv31",
          "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        }
      ],
      "affects": [
        {
          "ref": "pkg:deb/debian/libcurl4@7.88.1-10+deb12u4"
        }
      ],
      "analysis": {
        "state": "not_affected",
        "justification": "code_not_reachable",
        "response": ["will_not_fix"],
        "detail": "Вразливість кучі виникає виключно під час проксування через SOCKS5 з резолвінгом імен хостом. Пристрій використовує виключно прямі HTTPS-з'єднання з статичними IP без налаштованого SOCKS5-проксі."
      }
    }
  ]
}
```

У полі `detail` інженер фіксує вичерпне технічне пояснення, яке пояснює логіку висновку аудиторам, замовникам та автоматичним шлюзам верифікації безпеки.
