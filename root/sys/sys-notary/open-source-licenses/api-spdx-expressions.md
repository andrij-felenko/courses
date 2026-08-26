# 📋 Специфікація виразів SPDX 2.3/3.0 та нормалізовані ідентифікатори

Специфікація SPDX (англ. *Software Package Data Exchange*, міжнародний стандарт ISO/IEC 5962:2021) визначає формальну граматику, систему типів даних та канонічні ідентифікатори для однозначного опису умов ліцензування вихідних файлів, пакунків та скомпільованих двійкових артефактів. Стандарт усуває неоднозначності природної мови та варіації назв у коментарях, перетворюючи юридичні умови на строго типізовані об'єкти, які піддаються автоматичному синтаксичному аналізу в конвеєрах неперервної інтеграції (CI/CD).

## Граматика ліцензійних виразів (EBNF)

Синтаксис складеного ліцензійного виразу є формальною контекстно-вільною граматикою і визначається такою розширеною формою Бекуса — Наура (EBNF):

```ebnf
compound-expression = simple-expression
                    | compound-expression , ws , "AND" , ws , compound-expression
                    | compound-expression , ws , "OR"  , ws , compound-expression
                    | "(" , ws , compound-expression , ws , ")" ;

simple-expression   = license-id
                    | license-id , "+"
                    | license-id , ws , "WITH" , ws , exception-id
                    | license-ref ;

license-id          = (* Канонічний ідентифікатор зі списку SPDX License List *) ;
exception-id        = (* Ідентифікатор винятку зі списку SPDX Exceptions List *) ;
license-ref         = ( "LicenseRef-" , idstring )
                    | ( "DocumentRef-" , idstring , ":LicenseRef-" , idstring ) ;
idstring            = 1*( ALPHA / DIGIT / "-" / "." ) ;
ws                  = 1*( " " | "\t" | "\n" | "\r" ) ;
```

## Токенізація та побудова синтаксичного дерева (AST)

Під час автоматизованого аудиту синтаксичний аналізатор розбиває вхідний рядок на потік лексем:
- `TOKEN_OPEN_PAREN` та `TOKEN_CLOSE_PAREN` — керують групуванням операцій.
- `TOKEN_OP_AND` та `TOKEN_OP_OR` — булеві оператори взаємодії.
- `TOKEN_OP_WITH` — оператор прив'язки нормативного винятку.
- `TOKEN_LICENSE_ID` — канонічний ключ з офіційного реєстру ліцензій.
- `TOKEN_EXCEPTION_ID` — ключ з реєстру винятків.
- `TOKEN_LICENSE_REF` — користувацький ідентифікатор ліцензії поза реєстром.

Парсер рекурсивного спуску будує бінарне дерево абстрактного синтаксису (Abstract Syntax Tree, AST), листками якого є прості ліцензійні терми, а внутрішніми вузлами — логічні операції.

### Алгоритм розбору та пріоритет операторів

Обчислення логічного дерева ліцензійного виразу виконується у строгому порядку спадання пріоритету:

1. **Дужки `( ... )` (Найвищий пріоритет):** групують підвирази для явного перевизначення порядку асоціативності. Вираз `MIT OR (Apache-2.0 AND GPL-2.0-only)` означає, що користувач може обрати між чистою ліцензією MIT або одночасним виконанням вимог Apache-2.0 та GPL-2.0-only.
2. **Кваліфікатор винятку `WITH <exception-id>`:** зв'язує базову ліцензію з її конкретним нормативним винятком у неподільний атомарний терм. Наприклад, вираз `GPL-2.0-or-later WITH Classpath-exception-2.0` обробляється як єдиний ліцензійний контракт, у якому стандартні вимоги копілефту нейтралізовані для операцій динамічного зв'язування.
3. **Логічна кон'юнкція `AND`:** позначає необхідність одночасного виконання умов обох ліцензій. Виникає при включенні коду під двома різними ліцензіями в один спільний модуль (наприклад, поєднання `MIT AND BSD-3-Clause`). Результуючий бінарний артефакт вимагає виконання сукупності зобов'язань (збереження двох різних копірайтів та дотримання рекламного застереження BSD).
4. **Логічна диз'юнкція `OR` (Найнижчий пріоритет):** позначає множинне (подвійне) ліцензування. Одержувач артефакту має право обрати будь-яку одну з перелічених ліцензій за власним бажанням. Наприклад, вираз `MIT OR Apache-2.0` дозволяє комерційному проєкту обрати `MIT` для уникнення специфічних патентних обмежень Apache, або `Apache-2.0` для отримання прямого патентного гранту.

### Булеве спрощення ліцензійних виразів

Для оптимізації графів відповідності рушії безпеки застосовують правила булевої алгебри для спрощення виразів:
- **Ідемпотентність:** `A AND A = A`, `A OR A = A`.
- **Закон поглинання:** `A OR (A AND B) = A`. Якщо розробник має право обрати чистий `MIT` або комбінацію `MIT AND GPL-3.0`, ліцензійний рушій спрощує вимогу до безпечнішого `MIT`.
- **Дистрибутивність:** `A AND (B OR C) = (A AND B) OR (A AND C)`. Дозволяє розкласти складений вираз на альтернативні правові сценарії для оцінки юридичних ризиків.

## Канонічні ідентифікатори ліцензій (SPDX License List)

Стандарт веде публічний реєстр стандартизованих ліцензій (SPDX License List). Починаючи з версії 3.0, скасовано застарілий неоднозначний суфікс `+`, який замінено на строгі постфікси `-only` (виключно зазначена версія) та `-or-later` (зазначена версія або будь-яка новіша, випущена правовласником):

| Канонічний SPDX ID | Офіційна повна назва | Клас ліцензії | Основні зобов'язання |
|:---|:---|:---|:---|
| `MIT` | MIT License | Permissive | Збереження повідомлення про копірайт та відмови від гарантій |
| `BSD-2-Clause` | BSD 2-Clause "Simplified" License | Permissive | Збереження копірайту у вихідному коді та двійкових образах |
| `BSD-3-Clause` | BSD 3-Clause "New" or "Revised" License | Permissive | Заборона використання імен авторів для реклами та просування |
| `Apache-2.0` | Apache License 2.0 | Permissive + Patents | Прямий патентний грант, пункт про патентну відсіч, журнал змін |
| `MPL-2.0` | Mozilla Public License 2.0 | Weak Copyleft | Копілефт на рівні модифікованого файлу, патентне застереження |
| `LGPL-2.1-only` | GNU Lesser General Public License v2.1 only | Weak Copyleft | Дозволяє динамічний лінк; статичний лінк вимагає надати `.o` |
| `LGPL-2.1-or-later`| GNU Lesser General Public License v2.1 or later | Weak Copyleft | Можливість підвищення до LGPLv3 або повного переходу на GPL |
| `LGPL-3.0-only` | GNU Lesser General Public License v3.0 only | Weak Copyleft | Базується на GPLv3, містить вимоги щодо антитайвоізації |
| `LGPL-3.0-or-later`| GNU Lesser General Public License v3.0 or later | Weak Copyleft | Дозволяє вибір будь-якої майбутньої версії ліцензії LGPL |
| `GPL-2.0-only` | GNU General Public License v2.0 only | Strong Copyleft | Ліцензія ядра Linux; категорична заборона нових обмежень (§6) |
| `GPL-2.0-or-later` | GNU General Public License v2.0 or later | Strong Copyleft | Дозволяє апгрейд до GPLv3 для усунення конфлікту з Apache 2.0 |
| `GPL-3.0-only` | GNU General Public License v3.0 only | Strong Copyleft | Антитайвоізація (§6), патентний захист, сумісність з Apache 2.0 |
| `GPL-3.0-or-later` | GNU General Public License v3.0 or later | Strong Copyleft | Стандартний вибір більшості утиліт GNU та компілятора GCC |
| `AGPL-3.0-only` | GNU Affero General Public License v3.0 only | Network Copyleft | Зобов'язання розкриття вихідного коду при взаємодії через мережу |
| `AGPL-3.0-or-later`| GNU Affero General Public License v3.0 or later | Network Copyleft | Мережевий копілефт із правом оновлення версії ліцензії |
| `Unlicense` | The Unlicense | Public Domain | Повна публічна відмова від авторських прав на твір |

## Стандартні винятки ліцензій (SPDX Exceptions List)

Винятки модифікують базовий договір, додаючи спеціальні дозволи або знімаючи ефект копілефтного зараження для конкретних сценаріїв використання:

| Ідентифікатор винятку | Базова ліцензія | Інженерне призначення |
|:---|:---|:---|
| `Classpath-exception-2.0` | `GPL-2.0-only` / `GPL-2.0-or-later` | Дозволяє статичне та динамічне компонування Java-байткоду без вимоги відкривати вихідний код застосунку. |
| `LLVM-exception` | `Apache-2.0` | Дозволяє компонувати згенерований компілятором код рантайму LLVM/Clang без збереження обов'язкової атрибуції в бінарниках. |
| `Autoconf-exception-3.0` | `GPL-3.0-or-later` | Звільняє згенеровані скрипти `configure` від вимог розкриття коду за правилами GPLv3. |
| `Bison-exception-2.2` | `GPL-3.0-or-later` | Дозволяє поширювати C/C++ парсери, згенеровані утилітою GNU Bison, під будь-якою пропрієтарною чи вільною ліцензією. |
| `GCC-exception-3.1` | `GPL-3.0-or-later` | Дозволяє компонувати системні бібліотеки `libgcc`, `libstdc++` та рантайм GCC із пропрієтарним кодом без активації вимог копілефту. |
| `Bootloader-exception` | `GPL-2.0-or-later` | Дозволяє завантажувати закриті образи ОС без розкриття їхнього коду під ліцензією завантажувача. |

## Нестандартні та приватні ліцензії (LicenseRef)

Якщо сторонній компонент використовує нестандартний пропрієтарний договір, комерційну EULA або внутрішню угоду підприємства, яка відсутня в офіційному реєстрі SPDX, стандарт вимагає використання префікса `LicenseRef-`:

```
LicenseRef-Vendor-Proprietary-NDA-2026
DocumentRef-ThirdParty:LicenseRef-Custom-Commercial
```

Префікс `DocumentRef-` дозволяє посилатися на ліцензійні описи, що зберігаються в зовнішніх підписаних документах SBOM.

## Семантика спеціальних значень: NONE та NOASSERTION

Стандарт SPDX визначає два спеціальних псевдозначення для полів, де точний ліцензійний вираз не може бути вказаний:
1. **`NONE`:** свідчить про те, що файл чи пакет свідомо не містить жодної ліцензії (наприклад, автор прямо відмовився надавати ліцензію, або код є суспільним надбанням без формального тексту).
2. **`NOASSERTION`:** свідчить про те, що сканер або автор SBOM не зміг визначити ліцензію, або вирішив не робити жодних правових тверджень щодо цього компонента. Це сигнал тривоги для шлюзу CI/CD, який вимагає ручної верифікації пакета інженером.

## Типізація зв'язків між пакетами в графі SBOM

У специфікації SPDX 2.3 та профільній моделі SPDX 3.0 відносини між елементами мають строгу юридичну семантику:

- `DYNAMIC_LINK`: вказує, що цільовий двійковий модуль завантажує сторонню бібліотеку динамічно в рантаймі (використовуючи таблицю `DT_NEEDED` або виклики `dlopen`). Це дозволяє валідатору підтвердити відповідність умовам LGPL без вимоги передачі об'єктних файлів.
- `STATIC_LINK`: фіксує факт нерозривного фізичного вшивання об'єктного коду бібліотеки у виконуваний файл під час складання. Шлюз відповідності негайно перевіряє відсутність ліцензій класу Strong Copyleft (GPL).
- `DEPENDS_ON`: загальний логічний зв'язок залежності між модулями або сервісами, які не обов'язково ділять єдиний адресний простір.
- `GENERATED_FROM`: визначає зв'язок між вихідним файлом та скомпільованим бінарником чи кодогенератором (наприклад, парсером flex/bison).

## Формати серіалізації: Tag-Value та JSON Schema

Стандарт підтримує кілька взаємозамінних форматів серіалізації.

### 1. Текстовий формат Tag-Value (SPDX 2.3)

Історичний людинозчитний формат, зручний для швидкого аналізу в UNIX-пайплайнах за допомогою `grep` та `awk`:

```spdx
SPDXVersion: SPDX-2.3
DataLicense: CC0-1.0
SPDXID: SPDXRef-DOCUMENT
DocumentName: embedded-controller-build
DocumentNamespace: https://example.com/spdx/controller-1.0.0
Creator: Tool: SPDX-Audit-Engine-v2
Created: 2026-08-26T12:00:00Z

PackageName: mbedtls
SPDXID: SPDXRef-Package-mbedtls
PackageVersion: 3.5.0
PackageDownloadLocation: https://github.com/Mbed-TLS/mbedtls/releases
PackageLicenseDeclared: Apache-2.0 OR GPL-2.0-or-later
PackageLicenseConcluded: Apache-2.0 OR GPL-2.0-or-later
PackageCopyrightText: Copyright (C) 2006-2023, Arm Limited
```

### 2. Структурований формат JSON (SPDX 2.3 / 3.0)

Основний формат для інтеграції з корпоративними базами даних уразливостей та автоматизованими оркестраторами безпеки:

```json
{
  "spdxVersion": "SPDX-2.3",
  "dataLicense": "CC0-1.0",
  "SPDXID": "SPDXRef-DOCUMENT",
  "name": "embedded-gateway-firmware",
  "documentNamespace": "https://example.com/spdx/gateway-v2.1.0",
  "creationInfo": {
    "created": "2026-08-26T10:00:00Z",
    "creators": ["Tool: Syft-v0.98.0", "Organization: Acme Embedded Security"]
  },
  "packages": [
    {
      "name": "mbedtls",
      "SPDXID": "SPDXRef-Package-mbedtls",
      "versionInfo": "3.5.0",
      "downloadLocation": "https://github.com/Mbed-TLS/mbedtls/archive/v3.5.0.tar.gz",
      "filesAnalyzed": true,
      "licenseConcluded": "Apache-2.0 OR GPL-2.0-or-later",
      "licenseDeclared": "Apache-2.0 OR GPL-2.0-or-later",
      "licenseComments": "Dual-licensed under Apache 2.0 or GPL 2.0+",
      "copyrightText": "Copyright (C) 2006-2023, Arm Limited, All Rights Reserved"
    },
    {
      "name": "libsqlite3",
      "SPDXID": "SPDXRef-Package-sqlite",
      "versionInfo": "3.44.2",
      "downloadLocation": "https://www.sqlite.org/2023/sqlite-amalgamation-3440200.zip",
      "filesAnalyzed": false,
      "licenseConcluded": "Unlicense",
      "licenseDeclared": "Unlicense",
      "licenseComments": "SQLite source code is dedicated to the public domain",
      "copyrightText": "NO COPYRIGHT - Public Domain"
    },
    {
      "name": "libmodbus",
      "SPDXID": "SPDXRef-Package-libmodbus",
      "versionInfo": "3.1.10",
      "downloadLocation": "https://github.com/stephane/libmodbus/releases/tag/v3.1.10",
      "filesAnalyzed": true,
      "licenseConcluded": "LGPL-2.1-or-later",
      "licenseDeclared": "LGPL-2.1-or-later",
      "copyrightText": "Copyright (C) 2008-2022 Stephane Raimbault"
    }
  ],
  "relationships": [
    {
      "spdxElementId": "SPDXRef-DOCUMENT",
      "relationshipType": "DESCRIBES",
      "relatedSpdxElement": "SPDXRef-Package-mbedtls"
    },
    {
      "spdxElementId": "SPDXRef-DOCUMENT",
      "relationshipType": "CONTAINS",
      "relatedSpdxElement": "SPDXRef-Package-libmodbus"
    }
  ]
}
```

Використання стандартизованих ідентифікаторів у поєднанні зі строгою граматикою дозволяє конвеєрам збирання виконувати логічні операції спрощення та нормалізації ліцензійних графів на етапі валідації безпеки.
