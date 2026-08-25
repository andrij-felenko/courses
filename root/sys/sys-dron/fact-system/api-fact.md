# 📋 Контракт FactSystem: властивості факту, ключі метаданих, готові елементи

Довідка на один погляд: що саме можна спитати у факту з опису екрана, з якого ключа файлу метаданих кожна відповідь береться і який готовий елемент керування її вже читає. Усе нижче звірене з деревом `mavlink/qgroundcontrol`, гілка `master`, станом на 1 серпня 2026 року; імена, сигнатури й рядкові літерали — з самих заголовків, не з документації.

## Де що лежить

| Що | Файл у дереві проєкту |
| --- | --- |
| Клас факту | `src/FactSystem/Fact.h` · `Fact.cc` |
| Опис величини | `src/FactSystem/FactMetaData.h` · `FactMetaData.cc` |
| Контейнер фактів | `src/FactSystem/FactGroup.h` · `FactGroup.cc` |
| Факт налаштування | `src/FactSystem/SettingsFact.h` · `SettingsFact.cc` |
| Готові елементи керування | `src/FactSystem/FactControls/*.qml` |
| Місток до параметрів для екрана | `src/FactSystem/FactControls/FactPanelController.h` |

## Властивості факту

Усе, що видно з опису екрана. Колонка «сповіщення» каже, за яким сигналом властивість перечитується: `CONSTANT` означає, що прив'язка обчислиться **один раз** і більше ніколи.

### Значення

| Властивість | Тип | Звідки береться | Сповіщення |
| --- | --- | --- | --- |
| `rawValue` | `QVariant` | те, що лежить у пам'яті апарата | `rawValueChanged` |
| `value` | `QVariant` | `rawTranslator(rawValue)` | `valueChanged` |
| `valueString` | `QString` | `value`, округлене до `decimalPlaces` | `valueChanged` |
| `enumOrValueString` | `QString` | підпис переліку, якщо `enumStrings` непорожній; інакше `valueString` | `valueChanged` |
| `defaultValue` | `QVariant` | ключ `default`, пропущений через `rawTranslator` | `CONSTANT` |
| `defaultValueString` | `QString` | те саме, як рядок | `CONSTANT` |
| `defaultValueAvailable` | `bool` | чи був ключ `default` узагалі | `CONSTANT` |
| `valueEqualsDefault` | `bool` | звірка **сирих** значень; без усталеного — завжди `false` | `valueChanged` |
| `invalidValueString` | `QString` | що показати замість «не числа» | `CONSTANT` |

### Ім'я, підписи, довідка

| Властивість | Тип | Звідки береться | Сповіщення |
| --- | --- | --- | --- |
| `name` | `QString` | ім'я, під яким факт заведено в групі | `CONSTANT` |
| `label` | `QString` | ключ `label`; порожній — беруть `shortDesc`; порожній і той — беруть `name` | `CONSTANT` |
| `shortDescription` | `QString` | ключ `shortDesc` — підказка коло поля | `CONSTANT` |
| `longDescription` | `QString` | ключ `longDesc` — текст під кнопкою довідки | `CONSTANT` |
| `category` | `QString` | ключ `category` — верхній рівень дерева редактора | `CONSTANT` |
| `group` | `QString` | ключ `group` — гілка всередині категорії | `CONSTANT` |
| `componentId` | `int` | чий це параметр; `-1` для телеметрії й налаштувань | `CONSTANT` |

### Перелічувані значення й бітові маски

| Властивість | Тип | Звідки береться | Сповіщення |
| --- | --- | --- | --- |
| `enumStrings` | `QStringList` | ключ `enumStrings` або масив `values` | `enumsChanged` |
| `enumValues` | `QVariantList` | ключ `enumValues` або масив `values` | `enumsChanged` |
| `enumIndex` | `int` | позиція поточного сирого значення в `enumValues` | `valueChanged` |
| `enumStringValue` | `QString` | `enumStrings[enumIndex]` | `valueChanged` |
| `bitmaskStrings` | `QStringList` | масив `bitmask`, поле `description` | `bitmaskStringsChanged` |
| `bitmaskValues` | `QVariantList` | масив `bitmask`, поле `index`, перетворене на маску | `bitmaskValuesChanged` |
| `selectedBitmaskStrings` | `QStringList` | підписи тих бітів, що зараз стоять | `valueChanged` |

`bitmaskValues` — це вже готові маски, а не номери бітів: опис дає номер розряду, а список віддає число з єдиною одиницею на цьому місці, тому елемент керування накладає його побітово без арифметики (як число перетворюється на набір розрядів — [біти й порядок байтів](root:sf-algorithms/bits-bytes-endianness): значення в пам'яті це послідовність двійкових розрядів, і `1 << n` вирізає рівно один з них).

Пастка `enumIndex`: коли поточне сире значення не збігається з жодним записом переліку (дробові порівнюються з допуском 1.0e-6), факт **дописує** до переліку запис «Unknown» і випускає `enumsChanged`. Тобто список варіантів у випадному меню може подовшати сам, без жодної зміни файлу опису.

### Межі, крок, показ

| Властивість | Тип | Звідки береться | Сповіщення |
| --- | --- | --- | --- |
| `min` / `max` | `QVariant` | ключі `min` / `max`, показані | `CONSTANT` |
| `minString` / `maxString` | `QString` | те саме як рядок | `CONSTANT` |
| `minIsDefaultForType` / `maxIsDefaultForType` | `bool` | чи межа не задана, а взята як границя типу | `CONSTANT` |
| `userMin` / `userMax` (+ `…String`) | `QVariant` | ключі `userMin` / `userMax` — м'якші межі для звичайного користувача | `CONSTANT` |
| `increment` | `double` | ключ `increment`, пропущений через `rawTranslator` | `CONSTANT` |
| `decimalPlaces` | `int` | ключ `decimalPlaces` або обчислення (нижче) | `CONSTANT` |
| `units` | `QString` | показані одиниці, не сирі | `CONSTANT` |
| `maxStringLength` | `int` | ключ `maxStringLength` — стеля для поля введення | `CONSTANT` |

### Ознаки поведінки

| Властивість | Тип | Звідки береться | Усталено |
| --- | --- | --- | --- |
| `readOnly` | `bool` | ключ `readOnly` | `false` |
| `writeOnly` | `bool` | **ключа в файлі немає** — ставиться лише з коду, `setWriteOnly()` | `false` |
| `volatileValue` | `bool` | ключ `volatile` — апарат міняє значення сам | `false` |
| `hasControl` | `bool` | ключ **`control`** — чи давати елемент введення взагалі | `true` |
| `vehicleRebootRequired` | `bool` | ключ **`rebootRequired`** | `false` |
| `qgcRebootRequired` | `bool` | ключ `qgcRebootRequired` | `false` |
| `typeIsString` / `typeIsBool` | `bool` | з `type` | — |

Дві ознаки перезавантаження діють самі: у конструкторі факт підписує на власний сигнал `containerRawValueChanged` перевірку, яка показує «перезавантажте апарат» або «перезапустіть застосунок». Підписка саме на цей сигнал, а не на `rawValueChanged`, і дає потрібну поведінку: попередження з'являється, коли значення змінила людина, і не з'являється, коли те саме значення прилетіло з борту.

> 🔧 **Навіщо це.** Майже все, що йде з опису величини, оголошене `CONSTANT`. Прив'язка до `label`, `units`, `min` чи `decimalPlaces` обчислиться один раз і **не переобчислиться**, якщо опис приєднати пізніше. Звідси практичне правило: `setMetaData()` викликають до того, як факт віддали на екран. Факт, якому опис під'їхав уже після побудови панелі, показуватиме голе число з порожніми підписами, хоча в самому описі все на місці, — і це не помилка прив'язки, а буквальне значення слова `CONSTANT`.

## Методи факту

```cpp
// читання й перетворення
Q_INVOKABLE QString  validate(const QString &cookedValue, bool convertOnly);
Q_INVOKABLE QVariant clamp(const QString &cookedValue);
Q_INVOKABLE QVariant rawToCooked(const QVariant &rawValue) const;
QString              rawValueStringFullPrecision() const;

// запис
void setRawValue(const QVariant &value);        // від логіки застосунку
void setCookedValue(const QVariant &value);     // від людини, у показаних одиницях
void containerSetRawValue(const QVariant &value); // від апарата
void forceSetRawValue(const QVariant &value);   // повз перевірку «те саме значення»
void setEnumIndex(int index);
void setEnumStringValue(const QString &value);

// опис
void          setMetaData(FactMetaData *metaData, bool setDefaultFromMetaData = false);
FactMetaData *metaData();
void          setEnumInfo(const QStringList &strings, const QVariantList &values);

// темп сповіщень
void setSendValueChangedSignals(bool sendValueChangedSignals);
bool deferredValueChangeSignal() const;
void sendDeferredValueChangedSignal();
void clearDeferredValueChangeSignal();
```

| Метод | Що повертає / робить |
| --- | --- |
| `validate` | порожній рядок — значення допустиме; інакше готовий текст помилки для показу. `convertOnly = true` перевіряє лише тип, не межі |
| `clamp` | притискає введене до меж і повертає притиснуте; не пройшло приведення — повертає поточне сире |
| `rawToCooked` | ганяє довільне число через той самий перетворювач, що й власне значення факту |
| `rawValueStringFullPrecision` | сире без округлення до `decimalPlaces` — те, що годиться в журнал і в діагностику |
| `forceSetRawValue` | записує й сигналить **навіть коли значення не змінилося**; потрібне там, де сама дія запису важлива |
| `setEnumIndex` | пише `enumValues[index]`, а не сам індекс |

## Сигнали

| Сигнал | Несе | Кому адресований | Коли мовчить |
| --- | --- | --- | --- |
| `valueChanged(QVariant)` | показане значення | екранам | коли `setSendValueChangedSignals(false)` — тоді факт піднімає прапорець і чекає таймера групи |
| `rawValueChanged(QVariant)` | сире значення | логіці, журналові | ніколи не глушиться |
| `containerRawValueChanged(QVariant)` | сире значення | власникові факту: тому, хто має надіслати `PARAM_SET` або записати в сховище | коли значення прийшло з апарата через `containerSetRawValue()` |
| `vehicleUpdated(QVariant)` | сире значення | тому, хто чекає **відповіді** апарата | не мовчить узагалі: випускається з `containerSetRawValue()` навіть тоді, коли значення не змінилося |
| `enumsChanged()` | — | випадним спискам | — |
| `bitmaskStringsChanged()`, `bitmaskValuesChanged()` | — | наборам прапорців | — |
| `sendValueChangedSignalsChanged(bool)` | режим | групі | — |

Пара `containerRawValueChanged` і `vehicleUpdated` розв'язує задачу, яку одним сигналом не розв'язати: перший каже «змінилося, і це треба відправити», другий — «апарат відповів». Підтвердження на запис, у якому апарат повернув те саме число, змінює нуль, але дочекатися його треба (протокол вимагає підтвердження — див. [протокол параметрів](root:sys-dron/mavlink-param-tuning-and-diagnostics): станція шле `PARAM_SET` і чекає на `PARAM_VALUE` у відповідь, інакше повторює).

## Типи значень

Ключ `type` у файлі опису порівнюється **без урахування регістру**, тому в справжніх файлах трапляється і `uint32`, і `Uint32`.

| Рядок у файлі | Константа | Діапазон / зміст |
| --- | --- | --- |
| `Uint8` `Int8` | `valueTypeUint8` `valueTypeInt8` | 8 бітів без знаку / зі знаком |
| `Uint16` `Int16` | `valueTypeUint16` `valueTypeInt16` | 16 бітів |
| `Uint32` `Int32` | `valueTypeUint32` `valueTypeInt32` | 32 біти |
| `Uint64` `Int64` | `valueTypeUint64` `valueTypeInt64` | 64 біти |
| `Float` `Double` | `valueTypeFloat` `valueTypeDouble` | дробові одинарної / подвійної точності |
| `String` | `valueTypeString` | рядок; межі не діють, діє `maxStringLength` |
| `Bool` | `valueTypeBool` | булеве |
| `ElapsedSeconds` | `valueTypeElapsedTimeInSeconds` | тривалість; показується як час, а не як число |
| `Custom` | `valueTypeCustom` | значення з власним перетворювачем і власною перевіркою |

Коли `min` або `max` у файлі не задано, межею стає границя самого типу — і саме на це відповідають `minIsDefaultForType` та `maxIsDefaultForType`. Елемент керування питає їх, щоб не малювати повзунок від −2³¹ до 2³¹.

## Файл метаданих

Скелет файлу однаковий для груп телеметрії й для груп налаштувань:

```json
{
    "version":            1,
    "fileType":           "FactMetaData",
    "QGC.MetaData.Defines": { },
    "QGC.MetaData.Facts": [
        { "name": "...", "type": "..." }
    ]
}
```

Блок `QGC.MetaData.Defines` необов'язковий: у ньому тримають шматки тексту, які потім підставляють у кілька описів, щоб не повторювати той самий абзац.

### Усі ключі запису

| Ключ | Тип у JSON | Обов'язковий | Що робить |
| --- | --- | --- | --- |
| `name` | рядок | **так** | ключ, під яким факт шукають у групі |
| `type` | рядок | **так** | один із рядків таблиці типів |
| `label` | рядок | ні | підпис коло елемента керування |
| `shortDesc` | рядок | ні | однорядкова підказка |
| `longDesc` | рядок | ні | повний опис під кнопкою довідки |
| `units` | рядок | ні | **сирі** одиниці; від них залежить, який перетворювач стане сам |
| `default` | будь-що | ні | усталене значення; вмикає `valueEqualsDefault` |
| `mobileDefault` | будь-що | ні | інше усталене для збірок під телефон і планшет |
| `min` / `max` | число | ні | жорсткі межі; не задано — межі типу |
| `userMin` / `userMax` | число | ні | вужчі межі для звичайного користувача |
| `increment` | число | ні | крок; з нього ж виводиться `decimalPlaces`, якщо його не задано |
| `decimalPlaces` | число | ні | знаків після коми на екрані |
| `maxStringLength` | число | ні | стеля довжини для рядкових величин |
| `enumStrings` | рядок | ні | підписи варіантів через кому |
| `enumValues` | рядок | ні | числа варіантів через кому, у тому самому порядку |
| `values` | масив | ні | той самий перелік у вигляді пар `value` + `description` |
| `bitmask` | масив | ні | розряди у вигляді пар `index` + `description` |
| `control` | булеве | ні | `false` — величину показують, але не дають правити |
| `readOnly` | булеве | ні | лише читання |
| `volatile` | булеве | ні | апарат крутить значення сам; не підсвічувати як зміну користувача |
| `rebootRequired` | булеве | ні | після правки треба перезавантажити **апарат** |
| `qgcRebootRequired` | булеве | ні | після правки треба перезапустити **застосунок** |
| `category` / `group` | рядок | ні | місце в дереві редактора параметрів |
| `keywords` | рядок | ні | додаткові слова для пошуку по налаштуваннях |
| `comment` | рядок | ні | нотатка для того, хто редагує файл; застосунок її не читає |

Дві форми переліку не рівноцінні за зручністю. Рядкова (`enumStrings` плюс `enumValues`) коротка, але мовчазно вимагає, щоб у двох рядках було порівну елементів. Масивна тримає підпис і число поруч:

```json
"values": [
    { "value": 0, "description": "Disabled" },
    { "value": 1, "description": "Enabled" }
],
"bitmask": [
    { "index": 0, "description": "Roll" },
    { "index": 1, "description": "Pitch" }
]
```

Різниця між `value` і `index` тут принципова: у переліку пишуть саме значення, у масці — **номер розряду**, і маску з нього застосунок робить сам.

### Справжній запис

Витяг із `src/Settings/RTK.SettingsGroup.json` — величина, у якої задіяно майже все відразу:

```json
{
    "name":               "surveyInAccuracyLimit",
    "shortDesc":          "Survey in accuracy",
    "longDesc":           "The minimum accuracy value that Survey-In must achieve before it can complete.",
    "type":               "double",
    "default":            2.0,
    "min":                0.01,
    "max":                5.0,
    "increment":          0.01,
    "units":              "m",
    "decimalPlaces":      2,
    "qgcRebootRequired":  true,
    "label":              "Survey in accuracy"
}
```

Це і є весь код, потрібний, щоб на сторінці налаштувань з'явилося поле з підписом, підказкою, кроком, перевіркою діапазону, автоматичним переведенням у фути й попередженням про перезапуск.

## Що виводиться, коли ключа немає

Кількість знаків після коми виводиться в три щаблі:

```
decimalPlaces задано в файлі  → беремо його
інакше задано increment       → −⌈log₁₀(дробова частина показаного increment)⌉
інакше                        → 3 + (−log₁₀(rawTranslator(1.0))), обрізане до 0…25
```

**Умова: `type` = `double`, `units` = `m`, `increment` = 0.01, ключа `decimalPlaces` немає.**

```
метрична система (перетворювача нема, множник 1):
  показаний increment  = 0.01
  −⌈log₁₀(0.01)⌉       = −(−2)          = 2 знаки

фути (1 фут = 0.3048 м рівно):
  показаний increment  = 0.01 / 0.3048  = 0.0328084…
  дробова частина      = 0.0328084…
  −⌈log₁₀(0.0328084)⌉  = −(−1)          = 1 знак
```

Третій щабель працює тоді, коли кроку теж немає: береться три знаки й додається поправка на розмах перетворювача — переведення в дрібнішу одиницю саме собою додає знаків, у більшу відбирає.

## Одиниці: коли перетворювач ставиться сам

Рядок `units` порівнюється без урахування регістру спершу з вбудованою таблицею:

| Сирі одиниці | Показані | Перетворення |
| --- | --- | --- |
| `centi-degrees` | `deg` | ділення на 100 |
| `radians`, `rad` | `deg` | множення на 180/π |
| `gimbal-degrees` | `deg` | домовленість MAVLink про кути підвіса |
| `norm` | `%` | множення на 100 |
| `centi-celsius` | `C` | ділення на 100 |

Не збіглося — пробується шар налаштувань застосунку:

| Сирі одиниці | Що це | На що переводиться за вибором користувача |
| --- | --- | --- |
| `m`, `meter`, `meters` | горизонтальна відстань | фути |
| `vertical m` | вертикальна відстань | фути |
| `cm/px` | роздільність зйомки | одиниці горизонтальної відстані |
| `m/s` | швидкість | фути за секунду, милі за годину, км/год, вузли |
| `C` | температура | Фаренгейти |
| `m^2` | площа | км², гектари, фути², акри, милі² |
| `g` | вага | кілограми, унції, фунти |

Дві умови, через які перетворювач **не** стане, хоч би що було написано в `units`:

```
непорожній enumStrings або bitmaskStrings  → жодного перетворення взагалі
шар налаштувань застосунку                 → тільки для Double і Float
                                             і тільки за порожнього enumStrings
```

Перша умова закриває безглуздя на кшталт «код стану GPS у футах». Друга пояснює мовчазну поразку, на яку легко натрапити: цілочислена величина в метрах у фути **не** переводиться, бо переведення дало б дріб, а тип цілий.

Окрема дрібниця: `vertical m` як показані одиниці наприкінці скорочується до `m` — на екрані стоїть звичайне «m», хоча в описі величини вертикальність позначена явно.

## FactGroup

```cpp
explicit FactGroup(int updateRateMsecs, const QString &metaDataFile,
                   QObject *parent = nullptr, bool ignoreCamelCase = false);
explicit FactGroup(int updateRateMsecs,
                   QObject *parent = nullptr, bool ignoreCamelCase = false);
```

| Метод | Що робить |
| --- | --- |
| `bool factExists(const QString &name) const` | чи є такий факт (складене ім'я теж годиться) |
| `Fact *getFact(const QString &name) const` | факт за іменем; немає — `nullptr` і запис у журнал |
| `FactGroup *getFactGroup(const QString &name) const` | вкладена група за іменем |
| `QStringList factNames() const` | імена фактів цієї групи |
| `QStringList factGroupNames() const` | імена вкладених груп |
| `const QMap<QString, FactGroup*> &factGroups() const` | усі вкладені групи |
| `bool telemetryAvailable() const` | чи прийшло в цю групу хоч щось |
| `void setLiveUpdates(bool liveUpdates)` | увімкнути негайні сповіщення для екрана |
| `virtual void handleMessage(Vehicle *, const mavlink_message_t &)` | точка, куди підкладають розбір свого повідомлення |

Складене ім'я розбирається крапкою, **але рівно на дві частини**: `getFact("gps.lock")` знайде групу `gps` і спитає в неї факт `lock`, а `getFact("a.b.c")` поверне `nullptr` із попередженням у журналі. Глибше спускаються ланцюжком `getFactGroup()` або, з опису екрана, ланцюжком властивостей.

Перший аргумент конструктора — період у мілісекундах, з яким таймер групи випускає накопичені сповіщення для екрана; нуль означає «негайно». Другий — шлях до файлу опису в ресурсах збірки:

```cpp
VehicleGPSFactGroup::VehicleGPSFactGroup(QObject *parent)
    : FactGroup(1000, ":/json/Vehicle/GPSFact.json", parent)
{
    _addFact(&_latFact);
    _addFact(&_lonFact);
    _addFact(&_hdopFact);
    _addFact(&_lockFact);
    _addFact(&_countFact);

    _latFact.setRawValue(std::numeric_limits<float>::quiet_NaN());
    _hdopFact.setRawValue(std::numeric_limits<float>::quiet_NaN());
    _lockFact.setRawValue(0);
}
```

Початкове «не число» тут не косметика: доки повідомлення не прийшло, показник має малювати прочерк, а не нуль, який виглядав би як справжня координата.

`setLiveUpdates(true)` зупиняє таймер і знімає глушники з усіх фактів групи; `setLiveUpdates(false)` вертає таймер. Це перемикають сторінки налаштування, де людина крутить регулятор і мусить бачити відгук негайно.

Факти налаштувань — окремий підклас: `SettingsFact(const QString &settingsGroup, FactMetaData *metaData, QObject *parent)` читає початкове значення зі сховища при створенні й підписує збереження на власний `rawValueChanged`; властивість `userVisible` дозволяє тримати службові налаштування поза очима користувача (що саме й де переживає перезапуск — [збереження налаштувань](root:sys-dron/settings-persistence): своя гілка сховища на кожну групу, ключ = ім'я факту).

## Готові елементи керування

Усі лежать в одній теці й приймають одну властивість — `fact`.

| Елемент | Читає з факту | Пише у факт | Коли доречний |
| --- | --- | --- | --- |
| `FactTextField` | `valueString`, `units`, `maxStringLength`, `typeIsString` | після `validate()` — у `value` | будь-яке число або рядок |
| `FactComboBox` | `enumStrings`, `enumValues`, `enumIndex`, `value` | `enumValues[index]`, а за порожніх `enumValues` — сам індекс | є `enumStrings` |
| `FactCheckBox` | `typeIsBool`, `value` | `checkedValue` або `uncheckedValue` (усталено 1 і 0) | булеве або пара 0/1 |
| `FactBitmask` | `bitmaskStrings`, `bitmaskValues`, `value` | значення з накладеною чи знятою маскою розряду | є масив `bitmask` |
| `FactValueSlider` | `valueSliderModel()`, `increment`, `decimalPlaces`, `units`, `value` | вибране моделлю значення | є `increment` |
| `FactLabel` | `valueString`, `units` | нічого | лише показ, `readOnly` |

Поруч із ними в тій самій теці лежать складені варіанти: `FactTextFieldSlider` і `FactTextFieldSlider2` (поле плюс повзунок), `FactCheckBoxSlider` і `FactBitMaskCheckBoxSlider` (галочки в стилі перемикача), `AltitudeFactTextField` (поле висоти зі знанням про режим висоти), `FactTextFieldGrid` і `FactTextFieldRow` (кілька полів однією сіткою), а також родина `LabelledFact…` — `LabelledFactTextField`, `LabelledFactComboBox`, `LabelledFactLabel`, `LabelledFactIncrementer`, `LabelledFactBrowse` — яка сама бере підпис із `label`.

Дві деталі, на яких найчастіше спотикаються.

`FactTextField` при завершенні редагування кличе `fact.validate(text, false)`. Порожній результат — значення пишеться; непорожній — на екрані з'являється текст помилки, а в полі **лишається старе** значення. Тобто перевірка меж стоїть в елементі, а правило перевірки — у файлі опису, і жодного окремого коду перевірки писати не треба.

`FactComboBox` має властивість `indexModel`. Коли `enumValues` порожній, у факт іде сам номер вибраного рядка; коли непорожній — іде число з `enumValues`. Плутанина між цими двома режимами дає класичний симптом: список показує правильні слова, а в апарат їде порядковий номер замість коду.

## Мінімальний робочий виклик

Три джерела значень, три способи дістати факт, один вигляд опису екрана:

```qml
FactPanelController { id: controller }

Column {
    // параметр апарата: -1 — компонент за замовчуванням
    FactTextField {
        fact: controller.getParameterFact(-1, "RTL_RETURN_ALT")
    }

    // телеметрія: ланцюжок груп від об'єкта апарата
    FactLabel {
        fact: QGroundControl.multiVehicleManager.activeVehicle.gps.hdop
    }

    // налаштування застосунку
    FactComboBox {
        fact: QGroundControl.settingsManager.appSettings.preferredFirmwareClass
    }
}
```

Місток до параметрів має рівно три виклики:

```cpp
Q_INVOKABLE Fact *getParameterFact(int componentId, const QString &name,
                                   bool reportMissing = true) const;
Q_INVOKABLE bool  parameterExists(int componentId, const QString &name) const;
Q_INVOKABLE void  getMissingParameters(const QStringList &rgNames);
```

`reportMissing = false` потрібне там, де параметра законно може не бути: панель, спільна для двох прошивок, питає обережно й ховає рядок, замість того щоб засипати журнал скаргами. `getMissingParameters()` замовляє довантаження тих імен, яких у кеші ще нема (черга запитів, повтори й підтвердження — робота [менеджера параметрів](root:sys-dron/parameter-manager): він тримає словник «ім'я → факт» і сам добирає те, чого бракує).
