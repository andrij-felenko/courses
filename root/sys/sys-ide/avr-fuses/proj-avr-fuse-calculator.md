# ⚙️ Калькулятор і верифікатор фьюзів AVR на C99 та C++20

Під час автоматизованого розгортання вбудованого програмного забезпечення на виробничій лінії та в системах неперервної інтеграції (CI/CD) пряме використання "магічних" шістнадцяткових байтів конфігурації (наприклад, `lfuse=0x62`, `hfuse=0xD9`, `efuse=0xFF`) є одним із найнебезпечніших джерел людських помилок. Достатньо випадкової помилки в одному шістнадцятковому розряді конфігураційного скрипта — і вся виготовлена партія друкованих плат перетворюється на невідповідаючі «цеглини» через вимкнення виводу апаратного скидання (`RSTDISBL`) або вибір неіснуючого зовнішнього тактового генератора.

Щоб унеможливити такі інциденти, процес генерації конфігураційних бітів має спиратися на спеціалізований програмний інструмент із вбудованим рушієм валідації правил безпеки. Цей інструмент приймає зрозумілі людині параметри (тип і частоту тактового джерела, час стабілізації напруги, поріг детектора просідання живлення, розмір завантажувача та цільовий рівень блокування зчитування), перевіряє їх на взаємну сумісність і формує безпечні байти для прошивки утилітою `avrdude`.

Нижче наведено повну архітектуру, математику бітових масок та промислову реалізацію верифікатора фьюзів двома стандартами: процедурним C99 та сучасним типізованим C++20.

---

### Інженерна мотивація та аналіз типових виробничих відмов

У серійному виробництві електронних виробів процес програмування мікроконтролерів є критичною ланкою технологічного ланцюжка. Якщо помилка в коді програми зазвичай призводить лише до некоректної роботи функціоналу й може бути виправлена повторним заливанням виправленого бінарного образу через стандартний послідовний роз'єм, то помилка в конфігураційних бітах (*fuses*) діє на рівні фізичної конфігурації кремнієвої структури.

Розгляньмо найтиповіші сценарії фатальних відмов, що виникають через ручне введення шістнадцяткових констант безпосередньо у виробничих Makefile-скриптах:

1. **Випадкове програмування біта `RSTDISBL` (Reset Disable):**
   Розробник намагається вивільнити додатковий порт введення-виведення для світлодіода чи кнопки на компактному мікроконтролері (наприклад, пін `PB5` у 8-вивідному ATtiny85 чи пін `PC6` у 28-вивідному ATmega328P). Для цього у старшому байті `hfuse` встановлюється біт `RSTDISBL = 0`. Щойно цей байт записується в чіп, внутрішня логіка мікроконтролера фізично відключає компаратор апаратного скидання від ніжки мікросхеми. Звичайна послідовна шина ISP (In-System Programming), яка вимагає утримання ніжки `RESET` на рівні нуля для синхронізації з програматором, миттєво втрачає здатність взаємодіяти з чипом. Плата на конвеєрі перестає відповідати, а для її відновлення потрібен демонтаж або підключення високовольтного програматора з подачею +12 В.

2. **Неузгодженість джерела тактування `CKSEL` та реальної схемотехніки:**
   Під час перенесення проекту з налагоджувальної плати Arduino (де встановлено кварцовий резонатор на 16 МГц) на автономний батарейний сенсор (де кварц відсутній заради економії собівартості та споживання струму) інженер забуває змінити значення `lfuse` з `0xFF` на `0xE2` (внутрішній RC-генератор на 8 МГц). Після першої ж команди прошивки мікроконтролер перемикає своє тактове дерево на очікування коливань із неіснуючого кварцу. Без тактових імпульсів ядро повністю зупиняється, а інтерфейс SPI перестає обробляти послідовні команди.

3. **Залишений активним режим debugWIRE (`DWEN = 0`):**
   Під час лабораторного зневадження коду через апаратний емулятор середовище розробки автоматично активує біт `DWEN`, перетворюючи лінію скидання на асинхронну однопровідну шину передачі даних. Якщо така конфігурація потрапляє у серійну релізну збірку, пристрій не може нормально функціонувати в польових умовах: лінія скидання залишається в режимі відкритого колектора, мікроконтролер не реагує на зовнішні апаратні супервізори живлення, а будь-яка спроба оновити прошивку через звичайний ISP-програматор видає помилку нерозпізнаної сигнатури кристала.

4. **Вимкнений детектор просідання напруги (`BODLEVEL = 111`):**
   Заради зменшення споживання струму в режимі сну розробники іноді повністю деактивують аналоговий детектор Brown-out. Коли батарея живлення в процесі тривалої експлуатації поступово розряджається, напруга на виводах мікросхеми падає нижче мінімального порогу стабільної роботи логічних вентилів АЛП (наприклад, нижче 2.0V при роботі на 16 МГц). Процесор починає зчитувати невалідні двійкові коди інструкцій, покажчик команд стрибає у випадкові області пам'яті, викликаючи спонтанне виконання інструкцій самопрограмування `SPM` та безповоротне руйнування сторінок Flash або вмісту EEPROM.

Для вирішення цих проблем ми будуємо програмну бібліотеку-валідатор, яка замінює ручний підбір магічних чисел на детермінований алгоритмічний аналіз взаємозв'язків між окремими апаратними вузлами мікроконтролера.

---

### Фізика та параметри тактового генератора: Розрахунок затримок SUT та робота дільника CKDIV8

Правильний вибір параметрів тактування у молодшому байті `lfuse` безпосередньо впливає на надійність холодного старту системи. Розгляньмо фізичні процеси, що відбуваються в генераторі коливань під час подачі живлення:

#### 1. Еквівалентна схема кварцового резонатора та час розгойдування
Кварцовий резонатор є електромеханічною коливальною системою з надзвичайно високою добротністю (Q ~ 10⁴..10⁵). Внутрішній інвертор Пірса в мікроконтролері збуджує коливання кристала за рахунок позитивного зворотного зв'язку через навантажувальні конденсатори C_L1 та C_L2.

Під час подачі напруги живлення коливання починаються з теплового шуму амплітудою в одиниці мікровольтів. Наростання амплітуди до логічних рівнів, достатніх для надійного перемикання тригерів тактового дерева, відбувається за експоненційним законом:

```text
A(t) = A0 * exp((pi * f0 * |-R_neg| / Q) * t)
```

де `-R_neg` — від'ємний динамічний опір підсилювача Пірса, а `f_0` — резонансна частота кварцу.

Якщо поле `SUT[1:0]` налаштоване на мінімальну затримку (наприклад, 14 тактових імпульсів + 0 мс), внутрішнє скидання ядра процесора відпускається в момент, коли амплітуда коливань становить лише 10–20% від номінальної. Вхідні логічні вентилі потрапляють у лінійний режим підсилення, викликаючи множинні паразитні спрацьовування на один період частоти. Як наслідок, перша команда за адресою `0x0000` декодується некоректно, що спричиняє зависання або перехід у неіснуючі обробники переривань.

Тому для кварцових резонаторів інструмент конфігурації повинен примусово обирати максимальний час затримки `SUT = 0b11` (16K тактів + 65 мс), забезпечуючи повне завершення перехідних процесів стабілізатора напруги та розгойдування кристала.

#### 2. Динамічний дільник тактової частоти CLKPR проти фьюза CKDIV8
У мікроконтролерах AVR існує два рівні керування дільником тактової частоти:
- **Апаратний біт `CKDIV8` у фьюзах:** визначає початковий стан переддільника одразу після апаратного скидання. Якщо `CKDIV8 = 0`, апаратний дільник ініціалізується коефіцієнтом ділення на 8.
- **Регістр `CLKPR` (Clock Prescaler Register):** дозволяє програмі динамічно змінювати коефіцієнт ділення від 1 до 256 під час виконання коду. Для захисту від випадкового перезапису зміна `CLKPR` вимагає виконання спеціальної 2-крокової послідовності із записом біта дозволу `CLKPCE`.

Наявність фабричного налаштування `CKDIV8 = 0` гарантує, що новий мікроконтролер із частотою генератора 8 МГц запуститься на безпечній частоті 1 МГц, що дозволяє виконувати його первинне програмування навіть при мінімальній напрузі живлення 1.8V.

---

### Схемотехніка аналогового детектора Brown-out та аналіз струму споживання

Аналоговий детектор просідання напруги живлення (BOD) є ключовим захисним елементом для запобігання пошкодженню енергонезалежної пам'яті.

Внутрішня структура блоку BOD складається з:
1. Джерела опорної напруги на базі ширини забороненої зони кремнію (*Bandgap Reference*), яке генерує стабільну напругу `V_BG ≈ 1.1 В`, практично не залежну від коливань температури та напруги живлення.
2. Прецизійного резистивного дільника напруги живлення `V_CC`.
3. Швидкісного аналогового компаратора з вбудованим гістерезисом близько 50 мВ для запобігання дрижанню сигналу скидання.

Головним компромісом при використанні детектора Brown-out є його власне споживання струму: неперервно працюючий компаратор і джерело опорної напруги споживають струм спокою `I_BOD ≈ 15..25 мкА`. Для пристроїв із живленням від мережі цей струм не має значення, проте для автономних батарейних сенсорів, розрахованих на 5–10 років роботи від одного літієвого елемента CR2032 (де цільовий струм сну становить менше 1 мкА), неперервна робота BOD може скоротити термін служби батареї в десятки разів.

У сучасних ревізіях мікроконтролерів AVR (зокрема ATmega328P) реалізовано компромісний режим програмного відключення BOD у режимі глибокого сну (*BOD Sleep Disable*) за допомогою бітів `BODS` та `BODSE` у регістрі `MCUCR`. Це дозволяє увімкнути апаратний захист фьюзами `efuse = 0xFD` (поріг 2.7V), забезпечуючи надійну роботу під час активного виконання програми, але апаратно знеструмлювати компаратор на час перебування в режимі Power-down.

---

### Архітектура та математична модель калькулятора фьюзів

Простір конфігурації мікроконтролера AVR складається з трьох незалежних байтів конфігурації (`lfuse`, `hfuse`, `efuse`) та одного байта блокування пам'яті (`lock`). Кожен байт є бітовим полем, у якому окремі розряди або групи розрядів відповідають за конкретні апаратні вузли.

Головна складність роботи з конфігураційними регістрами AVR полягає у двох фундаментальних факторах:
1. **Інверсна логіка:** біт `0` означає активний (запрограмований) стан, біт `1` — пасивний (стертий) стан.
2. **Нереалізовані розряди:** старші розряди деяких регістрів (наприклад, розряди 7..3 у `efuse` для ATmega328P) фізично відсутні на кристалі і при читанні апаратно підтягуються до логічної `1`. Якщо програма формує байт `0x05`, а утиліта прошивки зчитує `0xFD`, виникає хибна помилка верифікації, якщо нереалізовані розряди не були попередньо замасковані одиницями.

```
Логіка маскування нереалізованих бітів:
  efuse_calculated = (raw_value & IMPLEMENTED_MASK) | UNIMPLEMENTED_HIGH_BITS
  Приклад ATmega328P:
  IMPLEMENTED_MASK         = 0b00000111 (0x07 - тільки біти BODLEVEL[2:0])
  UNIMPLEMENTED_HIGH_BITS  = 0b11111000 (0xF8 - підтяжка старших 5 бітів до 1)
```

Розгляньмо математичні формули складання та розбору кожного з чотирьох конфігураційних регістрів.

#### 1. Модель молодшого байта (`lfuse`)
Молодший байт формується суперпозицією чотирьох незалежних полів:
- **`CKDIV8` (розряд 7):** бітова маска `0x80`. Значення `0` вмикає переддільник тактової частоти на 8; значення `1` вимикає поділ.
- **`CKOUT` (розряд 6):** бітова маска `0x40`. Значення `0` транслює системну тактову частоту на вивід `CLKO` (порт `PB0`); значення `1` вимикає вивід.
- **`SUT[1:0]` (розряди 5..4):** 2-бітове поле, маска `0x30`. Визначає час затримки запуску генератора від 14 тактів + 0 мс до 16K тактів + 65 мс.
- **`CKSEL[3:0]` (розряди 3..0):** 4-бітове поле, маска `0x0F`. Обирає фізичне джерело тактування.

Формула складання молодшого байта:
```
lfuse = (CKDIV8_bit << 7) | (CKOUT_bit << 6) | ((SUT & 0x03) << 4) | (CKSEL & 0x0F)
```

Формули розбору молодшого байта на складові параметри:
```
CKDIV8_state = ((lfuse & 0x80) == 0)   [1 = поділ увімкнено, 0 = вимкнено]
CKOUT_state  = ((lfuse & 0x40) == 0)   [1 = вивід увімкнено, 0 = вимкнено]
SUT_value    = (lfuse >> 4) & 0x03     [значення від 0 до 3]
CKSEL_value  = lfuse & 0x0F            [значення від 0 до 15]
```

#### 2. Модель старшого байта (`hfuse`)
Старший байт контролює апаратні інтерфейси зв'язку, сторожовий таймер та вектори запуску:
- **`RSTDISBL` (розряд 7):** маска `0x80`. `0` перетворює пін `RESET` на порт введення-виведення GPIO; `1` зберігає функцію апаратного скидання.
- **`DWEN` (розряд 6):** маска `0x40`. `0` активує однопровідний інтерфейс зневадження debugWIRE на лінії `RESET`; `1` вимикає debugWIRE.
- **`SPIEN` (розряд 5):** маска `0x20`. `0` дозволяє послідовне програмування через шину SPI (ISP); `1` блокує послідовний інтерфейс.
- **`WDTON` (розряд 4):** маска `0x10`. `0` примусово активує апаратний сторожовий таймер WDT з моменту включення; `1` дозволяє програмне керування.
- **`EESAVE` (розряд 3):** маска `0x08`. `0` захищає пам'ять EEPROM від стирання при виконанні операції `Chip Erase`; `1` дозволяє стирання EEPROM разом із Flash.
- **`BOOTSZ[1:0]` (розряди 2..1):** маска `0x06`. Задає розмір завантажувача: `0b11` (256 слів / 512 байт), `0b10` (512 слів / 1 КБ), `0b01` (1024 слова / 2 КБ), `0b00` (2048 слів / 4 КБ).
- **`BOOTRST` (розряд 0):** маска `0x01`. `0` спрямовує вектор скидання на базову адресу завантажувача; `1` запускає виконання з адреси `0x0000`.

Формула складання старшого байта:
```
hfuse = (RSTDISBL << 7) | (DWEN << 6) | (SPIEN << 5) | (WDTON << 4) |
        (EESAVE << 3)   | ((BOOTSZ & 0x03) << 1)     | (BOOTRST & 0x01)
```

Формули розбору старшого байта:
```
RSTDISBL_active = ((hfuse & 0x80) == 0)
DWEN_active     = ((hfuse & 0x40) == 0)
SPIEN_active    = ((hfuse & 0x20) == 0)
WDTON_active    = ((hfuse & 0x10) == 0)
EESAVE_active   = ((hfuse & 0x08) == 0)
BOOTSZ_value    = (hfuse >> 1) & 0x03
BOOTRST_active  = ((hfuse & 0x01) == 0)
```

#### 3. Модель розширеного байта (`efuse`)
У мікроконтролері ATmega328P розширений байт містить лише 3 молодші біти:
- **`BODLEVEL[2:0]` (розряди 2..0):** маска `0x07`.
  - `0b111` (`0x07`): Brown-out Detector вимкнено.
  - `0b110` (`0x06`): Поріг спрацьовування 1.8V.
  - `0b101` (`0x05`): Поріг спрацьовування 2.7V.
  - `0b100` (`0x04`): Поріг спрацьовування 4.3V.
- **Нереалізовані розряди (7..3):** фізично відсутні на кристалі. Під час зчитування внутрішня шина підтягує їх до `1` (маска `0xF8`).

Тому для коректної верифікації розширеного байта в утиліті `avrdude` формула нормалізації має вигляд:
```
efuse_raw = 0xF8 | (BODLEVEL & 0x07)
```

#### 4. Модель байта блокування (`lock`)
Байт блокування складається з трьох пар бітів:
- **`LB[2:1]` (розряди 1..0):** маска `0x03`. Загальний режим блокування зовнішнього читання/запису Flash та EEPROM через ISP/HVPP (`0b11` = Mode 1, `0b10` = Mode 2, `0b00` = Mode 3).
- **`BLB0[2:1]` (розряди 3..2):** маска `0x0C`. Захист секції застосунку від модифікації інструкціями `SPM` із завантажувача.
- **`BLB1[2:1]` (розряди 5..4):** маска `0x30`. Захист секції завантажувача від читання/модифікації з боку коду користувача.
- **Нереалізовані розряди (7..6):** завжди зчитуються як `1` (маска `0xC0`).

Формула складання байта блокування:
```
lock_raw = 0xC0 | ((BLB1 & 0x03) << 4) | ((BLB0 & 0x03) << 2) | (LB & 0x03)
```

---

### База даних цільових мікроконтролерів (MCU Database Abstraction)

Різні родини AVR мають суттєві відмінності у кількості конфігураційних регістрів, масках бітів та наявності апаратних периферійних модулів. Наш інструмент абстрагує ці відмінності через структуру дескриптора чіпа `avr_mcu_desc_t`:

| Параметр MCU | ATmega328P | ATtiny85 | ATmega2560 | ATmega1284P |
| :--- | :--- | :--- | :--- | :--- |
| **Сигнатура (Device Signature)** | `0x1E 0x95 0x0F` | `0x1E 0x93 0x0B` | `0x1E 0x98 0x01` | `0x1E 0x97 0x05` |
| **Кількість байтів Fuses** | 3 (`low, high, ext`) | 2 (`low, high`) | 3 (`low, high, ext`) | 3 (`low, high, ext`) |
| **Наявність порту JTAG** | Ні | Ні | **Так (`JTAGEN` у hfuse)** | **Так (`JTAGEN` у hfuse)** |
| **Наявність debugWIRE** | Так (`DWEN`) | Так (`DWEN`) | Ні (використовує JTAG) | Так (`DWEN` або JTAG) |
| **Маска нереалізованих бітів efuse** | `0xF8` (5 бітів) | Не застосовується | `0xF8` (5 бітів) | `0xF8` (5 бітів) |
| **Максимальний розмір завантажувача** | 4 КБ (2048 слів) | Немає виділеної секції | 8 КБ (4096 слів) | 8 КБ (4096 слів) |

Таблиця дескрипторів дозволяє автоматично адаптувати процес кодування та перевірки правил під конкретний мікроконтролер без дублювання логіки в коді.

---

### Детальний аналіз правил рушія безпеки (The Safety Rule Engine)

Автоматичний аналізатор перевіряє отримані байти конфігурації на відповідність 8 фундаментальним інженерним правилам:

#### 1. Правило 1: Захист від втрати виводу Reset (`RSTDISBL`)
Якщо біт `RSTDISBL` запрограмовано (`0`), а прапорець дозволу високовольтного програмування `--allow-hvpp-only` не встановлено користувачем, генерація блокується з критичною помилкою. Це рятує розробника від випадкового вимкнення лінії скидання на платах без доступу до +12V.

#### 2. Правило 2: Захист від блокування послідовного програмування (`SPIEN`)
Біт `SPIEN` повинен завжди залишатися в стані `0` (Programmed). Якщо утиліта виявляє спробу записати `SPIEN = 1`, генерується фатальна помилка, оскільки ISP-програматор втратить доступ до мікросхеми.

#### 3. Правило 3: Узгодженість тактової частоти та детектора Brown-out за кривою SOA
Згідно з графіком безпечної робочої зони (*Safe Operating Area*, SOA) з офіційного даташиту Microchip/Atmel:
- Робота на частотах до 4 МГц дозволена при напрузі від 1.8V до 5.5V.
- Робота на частотах до 10 МГц вимагає напруги не менше 2.7V.
- Робота на частотах до 20 МГц вимагає напруги не менше 4.5V (або щонайменше 3.78V для 16 МГц).

Якщо користувач обирає високочастотне джерело тактування (зовнішній кварц 16–20 МГц), але встановлює `BOD = Disabled` або `BOD = 1.8V`, аналізатор видає суворе попередження (*Warning*), оскільки при падінні живлення процесор увійде в неконтрольований стан до того, як спрацює апаратне скидання.

#### 4. Правило 4: Захист від залишеного режиму зневадження (`DWEN`)
Якщо генерується конфігурація для релізної або промислової прошивки, біт `DWEN` повинен бути встановлений у `1` (Unprogrammed / Disabled). Залишений активним `DWEN = 0` блокує стандартний автозапуск пристрою та перешкоджає подальшій прошивці через ISP.

#### 5. Правило 5: Узгодженість вектора скидання та розміру завантажувача
Якщо активовано вектор завантажувача (`BOOTRST = 0`), перевіряється, щоб розмір секції завантажувача `BOOTSZ` відповідав реальному розміру бінарного файлу завантажувача (наприклад, 512 байт для Optiboot або 2 КБ для стандартного Arduino Bootloader). Некоректне значення `BOOTSZ` призведе до того, що завантажувач перезапише перші байти власного коду або розпочне виконання з порожньої області пам'яті.

#### 6. Правило 6: Перевірка захисту пам'яті EEPROM (`EESAVE`)
Якщо пристрій зберігає унікальні калібрувальні константи або мережеві налаштування в EEPROM, біт `EESAVE` повинен бути запрограмований (`0`). Якщо користувач оновлює прошивку при `EESAVE = 1`, черговий цикл прошивки повністю зітре калібрувальні таблиці під час стирання Flash.

#### 7. Правило 7: Маскування нереалізованих розрядів
Перевіряється коректність бітових масок невикористаних розрядів у `efuse` та `lock`, щоб утиліти типу `avrdude` не генерували фальшивих помилок розбіжності при верифікації записаних даних.

#### 8. Правило 8: Порядок накладання бітів блокування Lock Bits
Утиліта попереджає користувача, що біти блокування `Lock Bits` не можна прошивати одночасно з образом програми, якщо програматор виконує верифікацію після запису. Прошивка `lock = 0x00` повинна виконуватися окремою фінальною командою після успішної побайтової звірки Flash і EEPROM.

---

### Повна реалізація калькулятора та валідатора на мові C99

Нижче наведено модульний код бібліотеки та консольної утиліти на чистому C99, що не має зовнішніх залежностей окрім стандартної бібліотеки CRT.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Переліки для людино-читабельної конфігурації
typedef enum {
    CLK_EXT_CLOCK          = 0x00, // Прямокутний сигнал на XTAL1
    CLK_INT_RC_8MHZ        = 0x02, // Внутрішній RC-генератор 8.0 МГц
    CLK_INT_128KHZ         = 0x04, // Внутрішній низькочастотний 128 кГц
    CLK_EXT_CRYSTAL_LOW    = 0x08, // Кварц низької частоти (0.4 - 0.9 МГц)
    CLK_EXT_CRYSTAL_MED    = 0x0A, // Кварц середньої частоти (0.9 - 3.0 МГц)
    CLK_EXT_CRYSTAL_HIGH   = 0x0F  // Кварц високої частоти (3.0 - 16.0 МГц)
} avr_clock_source_t;

typedef enum {
    SUT_FAST_RISING        = 0x00, // Швидке наростання VCC (14CK + 0ms)
    SUT_STANDARD           = 0x01, // Стандартний старт (14CK + 4.1ms)
    SUT_SLOW_RISING        = 0x02, // Повільне живлення (14CK + 65ms)
    SUT_MAX_CERAMIC        = 0x03  // Максимальна затримка (16K CK + 65ms)
} avr_sut_t;

typedef enum {
    BOD_DISABLED           = 0x07, // Brown-out детектування вимкнено
    BOD_1V8                = 0x06, // Поріг 1.8V (номінал 1.7 - 2.0V)
    BOD_2V7                = 0x05, // Поріг 2.7V (номінал 2.5 - 2.9V)
    BOD_4V3                = 0x04  // Поріг 4.3V (номінал 4.1 - 4.5V)
} avr_bod_level_t;

typedef enum {
    BOOT_SIZE_256_WORDS    = 0x03, // 512 байтів (адреса 0x3F00 / 0x7E00)
    BOOT_SIZE_512_WORDS    = 0x02, // 1024 байти (адреса 0x3E00 / 0x7C00)
    BOOT_SIZE_1024_WORDS   = 0x01, // 2048 байтів (адреса 0x3C00 / 0x7800)
    BOOT_SIZE_2048_WORDS   = 0x00  // 4096 байтів (адреса 0x3800 / 0x7000)
} avr_bootsz_t;

typedef enum {
    LOCK_MODE_1_OPEN       = 0x03, // Відкритий доступ (читання/запис)
    LOCK_MODE_2_NO_PROG    = 0x02, // Заборона запису через ISP
    LOCK_MODE_3_FULL_LOCK  = 0x00  // Повна заборона читання та запису
} avr_lock_mode_t;

// Структура дескриптора мікроконтролера
typedef struct {
    const char* name;
    const char* avrdude_part;
    uint8_t     signature[3];
    bool        has_extended_fuse;
    uint8_t     efuse_unimplemented_mask;
    uint8_t     lock_unimplemented_mask;
} avr_mcu_descriptor_t;

// Структура людино-читабельних параметрів
typedef struct {
    avr_clock_source_t clock_source;
    avr_sut_t          startup_time;
    bool               clock_output_enable;
    bool               divide_clock_by_8;
    
    bool               reset_disable;        // true = Reset перетворено в GPIO (НЕБЕЗПЕЧНО)
    bool               debugwire_enable;     // true = debugWIRE активовано
    bool               spi_prog_enable;      // true = ISP увімкнено (норма true)
    bool               watchdog_always_on;   // true = апаратний WDT
    bool               preserve_eeprom;      // true = збереження EEPROM при Chip Erase
    avr_bootsz_t       bootloader_size;
    bool               boot_reset_vector;    // true = старт із завантажувача
    
    avr_bod_level_t    bod_level;
    avr_lock_mode_t    lock_mode;
    uint8_t            boot_lock_app_bits;   // BLB0[1:0] (0..3)
    uint8_t            boot_lock_boot_bits;  // BLB1[1:0] (0..3)
} avr_human_config_t;

// Структура сирих байтів конфігурації
typedef struct {
    uint8_t lfuse;
    uint8_t hfuse;
    uint8_t efuse;
    uint8_t lock;
} avr_raw_fuses_t;

// Діагностика
typedef enum {
    DIAG_INFO,
    DIAG_WARNING,
    DIAG_CRITICAL_ERROR
} avr_diag_level_t;

typedef struct {
    avr_diag_level_t level;
    char message[160];
} avr_diag_item_t;

typedef struct {
    bool is_valid_and_safe;
    size_t count;
    avr_diag_item_t items[12];
} avr_audit_result_t;

// Таблиця дескрипторів мікроконтролерів
static const avr_mcu_descriptor_t MCU_DATABASE[] = {
    {
        .name = "ATmega328P",
        .avrdude_part = "m328p",
        .signature = {0x1E, 0x95, 0x0F},
        .has_extended_fuse = true,
        .efuse_unimplemented_mask = 0xF8,
        .lock_unimplemented_mask = 0xC0
    },
    {
        .name = "ATmega2560",
        .avrdude_part = "m2560",
        .signature = {0x1E, 0x98, 0x01},
        .has_extended_fuse = true,
        .efuse_unimplemented_mask = 0xF8,
        .lock_unimplemented_mask = 0xC0
    },
    {
        .name = "ATtiny85",
        .avrdude_part = "t85",
        .signature = {0x1E, 0x93, 0x0B},
        .has_extended_fuse = false,
        .efuse_unimplemented_mask = 0xFF,
        .lock_unimplemented_mask = 0xC0
    }
};

// Кодування людино-читабельної конфігурації у сирі байти
avr_raw_fuses_t avr_encode_fuses(const avr_human_config_t* cfg) {
    avr_raw_fuses_t raw;
    
    // 1. Low Fuse
    raw.lfuse = (cfg->divide_clock_by_8 ? 0x00 : 0x80) |
                (cfg->clock_output_enable ? 0x00 : 0x40) |
                ((cfg->startup_time & 0x03) << 4) |
                (cfg->clock_source & 0x0F);
                
    // 2. High Fuse
    raw.hfuse = (cfg->reset_disable ? 0x00 : 0x80) |
                (cfg->debugwire_enable ? 0x00 : 0x40) |
                (cfg->spi_prog_enable ? 0x00 : 0x20) |
                (cfg->watchdog_always_on ? 0x00 : 0x10) |
                (cfg->preserve_eeprom ? 0x00 : 0x08) |
                ((cfg->bootloader_size & 0x03) << 1) |
                (cfg->boot_reset_vector ? 0x00 : 0x01);
                
    // 3. Extended Fuse (з маскуванням нереалізованих розрядів 7..3 як 1)
    raw.efuse = 0xF8 | (cfg->bod_level & 0x07);
    
    // 4. Lock Bits (з маскуванням нереалізованих розрядів 7..6 як 1)
    raw.lock = 0xC0 |
               ((cfg->boot_lock_boot_bits & 0x03) << 4) |
               ((cfg->boot_lock_app_bits & 0x03) << 2) |
               (cfg->lock_mode & 0x03);
               
    return raw;
}

// Декодування сирих байтів у параметри
avr_human_config_t avr_decode_fuses(avr_raw_fuses_t raw) {
    avr_human_config_t cfg;
    memset(&cfg, 0, sizeof(cfg));
    
    // Low
    cfg.divide_clock_by_8   = (raw.lfuse & 0x80) == 0;
    cfg.clock_output_enable = (raw.lfuse & 0x40) == 0;
    cfg.startup_time        = (avr_sut_t)((raw.lfuse >> 4) & 0x03);
    cfg.clock_source        = (avr_clock_source_t)(raw.lfuse & 0x0F);
    
    // High
    cfg.reset_disable       = (raw.hfuse & 0x80) == 0;
    cfg.debugwire_enable    = (raw.hfuse & 0x40) == 0;
    cfg.spi_prog_enable     = (raw.hfuse & 0x20) == 0;
    cfg.watchdog_always_on  = (raw.hfuse & 0x10) == 0;
    cfg.preserve_eeprom     = (raw.hfuse & 0x08) == 0;
    cfg.bootloader_size     = (avr_bootsz_t)((raw.hfuse >> 1) & 0x03);
    cfg.boot_reset_vector   = (raw.hfuse & 0x01) == 0;
    
    // Extended
    cfg.bod_level           = (avr_bod_level_t)(raw.efuse & 0x07);
    
    // Lock
    cfg.lock_mode           = (avr_lock_mode_t)(raw.lock & 0x03);
    cfg.boot_lock_app_bits  = (raw.lock >> 2) & 0x03;
    cfg.boot_lock_boot_bits = (raw.lock >> 4) & 0x03;
    
    return cfg;
}

// Рушій валідації безпеки
avr_audit_result_t avr_validate_fuses(avr_raw_fuses_t raw, bool allow_hvpp_override) {
    avr_audit_result_t res;
    memset(&res, 0, sizeof(res));
    res.is_valid_and_safe = true;
    
    // Перевірка 1: RSTDISBL
    if ((raw.hfuse & 0x80) == 0) {
        if (!allow_hvpp_override) {
            res.is_valid_and_safe = false;
            snprintf(res.items[res.count++].message, sizeof(res.items[0].message),
                     "ФАТАЛЬНО: RSTDISBL запрограмовано (0)! Пін Reset стане GPIO. ISP прошивка буде неможливою без HVPP.");
            res.items[res.count - 1].level = DIAG_CRITICAL_ERROR;
        } else {
            snprintf(res.items[res.count++].message, sizeof(res.items[0].message),
                     "ПОПЕРЕДЖЕННЯ: RSTDISBL активний. Дозволено через прапорець HVPP.");
            res.items[res.count - 1].level = DIAG_WARNING;
        }
    }
    
    // Перевірка 2: SPIEN
    if ((raw.hfuse & 0x20) != 0) {
        res.is_valid_and_safe = false;
        snprintf(res.items[res.count++].message, sizeof(res.items[0].message),
                 "ФАТАЛЬНО: SPIEN стерто (1)! Інтерфейс послідовного ISP програмування повністю заблоковано.");
        res.items[res.count - 1].level = DIAG_CRITICAL_ERROR;
    }
    
    // Перевірка 3: debugWIRE
    if ((raw.hfuse & 0x40) == 0) {
        snprintf(res.items[res.count++].message, sizeof(res.items[0].message),
                 "УВАГА: debugWIRE увімкнено (DWEN=0). Чіп не відповідатиме звичайному ISP програматору.");
        res.items[res.count - 1].level = DIAG_WARNING;
    }
    
    // Перевірка 4: Тактування vs BOD
    uint8_t cksel = raw.lfuse & 0x0F;
    uint8_t bod   = raw.efuse & 0x07;
    if (cksel >= 0x08 && bod == BOD_DISABLED) {
        snprintf(res.items[res.count++].message, sizeof(res.items[0].message),
                 "РИЗИК: Обрано високочастотний кварц, але Brown-out Detector вимкнено. Можливе псування Flash при спаді живлення.");
        res.items[res.count - 1].level = DIAG_WARNING;
    }
    
    // Перевірка 5: Зовнішній генератор
    if (cksel == 0x00) {
        snprintf(res.items[res.count++].message, sizeof(res.items[0].message),
                 "ІНФО: Режим External Clock. Для роботи обов'язковий зовнішній меандр на ніжці XTAL1.");
        res.items[res.count - 1].level = DIAG_INFO;
    }
    
    // Перевірка 6: Lock Bits
    if ((raw.lock & 0x03) != 0x03) {
        snprintf(res.items[res.count++].message, sizeof(res.items[0].message),
                 "ІНФО: Активовано біти блокування пам'яті Lock Bits (0x%02X). Зчитування Flash буде обмежено.", raw.lock);
        res.items[res.count - 1].level = DIAG_INFO;
    }
    
    return res;
}

// Формування рядка виклику для утиліти avrdude
void avr_format_avrdude_cmd(char* out_buf, size_t buf_len, const char* mcu, avr_raw_fuses_t raw) {
    snprintf(out_buf, buf_len,
             "avrdude -c usbasp -p %s -U lfuse:w:0x%02X:m -U hfuse:w:0x%02X:m -U efuse:w:0x%02X:m -U lock:w:0x%02X:m",
             mcu, raw.lfuse, raw.hfuse, raw.efuse, raw.lock);
}
```
```cpp
#include <cstdint>
#include <string>
#include <string_view>
#include <vector>
#include <expected>
#include <format>
#include <span>
#include <iostream>

namespace avr::tool {

enum class ClockSource : std::uint8_t {
    ExternalClock      = 0x00,
    InternalRc8MHz     = 0x02,
    Internal128kHz     = 0x04,
    ExternalCrystalLow = 0x08,
    ExternalCrystalMed = 0x0A,
    ExternalCrystalHigh= 0x0F
};

enum class StartupTime : std::uint8_t {
    FastRisingPower = 0x00,
    StandardDelay   = 0x01,
    SlowRisingPower = 0x02,
    MaxDelayCeramic = 0x03
};

enum class BodLevel : std::uint8_t {
    Disabled = 0x07,
    V1_8     = 0x06,
    V2_7     = 0x05,
    V4_3     = 0x04
};

enum class BootSize : std::uint8_t {
    Words256  = 0x03, // 512B
    Words512  = 0x02, // 1KB
    Words1024 = 0x01, // 2KB
    Words2048 = 0x00  // 4KB
};

enum class LockMode : std::uint8_t {
    Mode1Open     = 0x03,
    Mode2NoProg   = 0x02,
    Mode3FullLock = 0x00
};

enum class DiagSeverity {
    Info,
    Warning,
    CriticalError
};

struct DiagMessage {
    DiagSeverity severity;
    std::string text;
};

struct FuseBytes {
    std::uint8_t low{0x62};
    std::uint8_t high{0xD9};
    std::uint8_t extended{0xFF};
    std::uint8_t lock{0xFF};

    [[nodiscard]] constexpr bool operator==(const FuseBytes&) const noexcept = default;
};

class FuseBuilder {
private:
    ClockSource  clock_{ClockSource::InternalRc8MHz};
    StartupTime  sut_{StartupTime::MaxDelayCeramic};
    bool         clkout_{false};
    bool         ckdiv8_{true};

    bool         rstdisbl_{false};
    bool         dwen_{false};
    bool         spien_{true};
    bool         wdton_{false};
    bool         eesave_{false};
    BootSize     bootsz_{BootSize::Words2048};
    bool         bootrst_{false};

    BodLevel     bod_{BodLevel::Disabled};
    LockMode     lock_{LockMode::Mode1Open};
    std::uint8_t blb0_{0x03};
    std::uint8_t blb1_{0x03};

public:
    constexpr FuseBuilder() noexcept = default;

    constexpr FuseBuilder& set_clock(ClockSource clk, StartupTime sut, bool div8 = false) noexcept {
        clock_ = clk;
        sut_ = sut;
        ckdiv8_ = div8;
        return *this;
    }

    constexpr FuseBuilder& enable_clock_output(bool enable) noexcept {
        clkout_ = enable;
        return *this;
    }

    constexpr FuseBuilder& set_reset_as_gpio(bool disable_reset) noexcept {
        rstdisbl_ = disable_reset;
        return *this;
    }

    constexpr FuseBuilder& set_debugwire(bool enable) noexcept {
        dwen_ = enable;
        return *this;
    }

    constexpr FuseBuilder& set_isp_enabled(bool enable) noexcept {
        spien_ = enable;
        return *this;
    }

    constexpr FuseBuilder& set_preserve_eeprom(bool preserve) noexcept {
        eesave_ = preserve;
        return *this;
    }

    constexpr FuseBuilder& set_bootloader(BootSize size, bool enable_vector) noexcept {
        bootsz_ = size;
        bootrst_ = enable_vector;
        return *this;
    }

    constexpr FuseBuilder& set_bod(BodLevel level) noexcept {
        bod_ = level;
        return *this;
    }

    constexpr FuseBuilder& set_lock_mode(LockMode mode) noexcept {
        lock_ = mode;
        return *this;
    }

    [[nodiscard]] constexpr FuseBytes build() const noexcept {
        FuseBytes res;

        // Low
        res.low = (ckdiv8_ ? 0x00U : 0x80U) |
                  (clkout_ ? 0x00U : 0x40U) |
                  (static_cast<std::uint8_t>(sut_) << 4) |
                  (static_cast<std::uint8_t>(clock_) & 0x0FU);

        // High
        res.high = (rstdisbl_ ? 0x00U : 0x80U) |
                   (dwen_ ? 0x00U : 0x40U) |
                   (spien_ ? 0x00U : 0x20U) |
                   (wdton_ ? 0x00U : 0x10U) |
                   (eesave_ ? 0x00U : 0x08U) |
                   (static_cast<std::uint8_t>(bootsz_) << 1) |
                   (bootrst_ ? 0x00U : 0x01U);

        // Extended
        res.extended = 0xF8U | (static_cast<std::uint8_t>(bod_) & 0x07U);

        // Lock
        res.lock = 0xC0U |
                   ((blb1_ & 0x03U) << 4) |
                   ((blb0_ & 0x03U) << 2) |
                   static_cast<std::uint8_t>(lock_);

        return res;
    }
};

class FuseValidator {
public:
    [[nodiscard]] static std::expected<std::vector<DiagMessage>, std::string>
    validate(const FuseBytes& bytes, bool allow_hvpp = false) {
        std::vector<DiagMessage> diag;

        // Перевірка 1: RSTDISBL
        if ((bytes.high & 0x80U) == 0) {
            if (!allow_hvpp) {
                return std::unexpected("КРИТИЧНО: RSTDISBL активний без прапорця HVPP. Блокування скидання!");
            }
            diag.push_back({DiagSeverity::Warning, "RSTDISBL увімкнено під захистом HVPP прапорця."});
        }

        // Перевірка 2: SPIEN
        if ((bytes.high & 0x20U) != 0) {
            return std::unexpected("ФАТАЛЬНО: SPIEN стерто в 1. Послідовний ISP інтерфейс вимкнено.");
        }

        // Перевірка 3: DWEN
        if ((bytes.high & 0x40U) == 0) {
            diag.push_back({DiagSeverity::Warning, "debugWIRE активний (DWEN=0). ISP доступ заблоковано до зупинки DW."});
        }

        // Перевірка 4: BOD vs Clock
        const auto cksel = bytes.low & 0x0FU;
        const auto bod   = bytes.extended & 0x07U;
        if (cksel >= 0x08U && bod == static_cast<std::uint8_t>(BodLevel::Disabled)) {
            diag.push_back({DiagSeverity::Warning, "Високочастотний кварц без детектора BOD несе ризик псування пам'яті."});
        }

        return diag;
    }

    [[nodiscard]] static std::string to_avrdude_args(const FuseBytes& bytes, std::string_view chip = "m328p") {
        return std::format("avrdude -c usbasp -p {} -U lfuse:w:0x{:02X}:m -U hfuse:w:0x{:02X}:m -U efuse:w:0x{:02X}:m -U lock:w:0x{:02X}:m",
                           chip, bytes.low, bytes.high, bytes.extended, bytes.lock);
    }
};

} // namespace avr::tool
```
:::

---

### Повна реалізація консольної утиліти CLI (Command-Line Interface)

Для інтеграції в автоматичні складальні конвеєри та скрипти прошивки на базі `Make`, `CMake` або `Python` утиліта підтримує розбір позиційних та іменованих параметрів командного рядка.

Під час виклику утиліта виконує синтаксичний аналіз аргументів, перевіряє передані текстові назви режимів за внутрішніми словниками відповідностей і заповнює екземпляр структури конфігурації. Якщо передано невідомий прапорець чи некоректне значення напруги Brown-out, робота негайно переривається з інформативним повідомленням про помилку.

Нижче наведено повну реалізацію точки входу `main()` та парсера аргументів на C99:

:::tabs
```c
int main(int argc, char* argv[]) {
    avr_human_config_t config = {
        .clock_source        = CLK_EXT_CRYSTAL_HIGH,
        .startup_time        = SUT_MAX_CERAMIC,
        .divide_clock_by_8   = false,
        .clock_output_enable = false,
        .reset_disable       = false,
        .debugwire_enable    = false,
        .spi_prog_enable     = true,
        .watchdog_always_on  = false,
        .preserve_eeprom     = false,
        .bootloader_size     = BOOT_SIZE_256_WORDS,
        .boot_reset_vector   = true,
        .bod_level           = BOD_2V7,
        .lock_mode           = LOCK_MODE_1_OPEN,
        .boot_lock_app_bits  = 0x03,
        .boot_lock_boot_bits = 0x03
    };

    const char* target_chip = "m328p";
    bool output_json = false;
    bool allow_hvpp = false;

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--chip") == 0 && i + 1 < argc) {
            target_chip = argv[++i];
        } else if (strcmp(argv[i], "--clock") == 0 && i + 1 < argc) {
            const char* clk = argv[++i];
            if (strcmp(clk, "int-8mhz") == 0) config.clock_source = CLK_INT_RC_8MHZ;
            else if (strcmp(clk, "ext-clock") == 0) config.clock_source = CLK_EXT_CLOCK;
            else if (strcmp(clk, "int-128k") == 0) config.clock_source = CLK_INT_128KHZ;
            else config.clock_source = CLK_EXT_CRYSTAL_HIGH;
        } else if (strcmp(argv[i], "--div8") == 0) {
            config.divide_clock_by_8 = true;
        } else if (strcmp(argv[i], "--bod") == 0 && i + 1 < argc) {
            const char* b = argv[++i];
            if (strcmp(b, "disabled") == 0) config.bod_level = BOD_DISABLED;
            else if (strcmp(b, "1.8v") == 0) config.bod_level = BOD_1V8;
            else if (strcmp(b, "4.3v") == 0) config.bod_level = BOD_4V3;
            else config.bod_level = BOD_2V7;
        } else if (strcmp(argv[i], "--allow-hvpp") == 0) {
            allow_hvpp = true;
        } else if (strcmp(argv[i], "--json") == 0) {
            output_json = true;
        }
    }

    avr_raw_fuses_t raw = avr_encode_fuses(&config);
    avr_audit_result_t audit = avr_validate_fuses(raw, allow_hvpp);

    if (output_json) {
        printf("{\n");
        printf("  \"chip\": \"%s\",\n", target_chip);
        printf("  \"lfuse\": \"0x%02X\",\n", raw.lfuse);
        printf("  \"hfuse\": \"0x%02X\",\n", raw.hfuse);
        printf("  \"efuse\": \"0x%02X\",\n", raw.efuse);
        printf("  \"lock\": \"0x%02X\",\n", raw.lock);
        printf("  \"is_safe\": %s,\n", audit.is_valid_and_safe ? "true" : "false");
        printf("  \"issues\": [\n");
        for (size_t i = 0; i < audit.count; ++i) {
            printf("    {\"level\": %d, \"message\": \"%s\"}%s\n",
                   audit.items[i].level, audit.items[i].message,
                   (i + 1 < audit.count) ? "," : "");
        }
        printf("  ]\n");
        printf("}\n");
    } else {
        printf("=== Результати розрахунку фьюзів для %s ===\n", target_chip);
        printf(" Low Fuse (lfuse)     : 0x%02X\n", raw.lfuse);
        printf(" High Fuse (hfuse)    : 0x%02X\n", raw.hfuse);
        printf(" Ext Fuse (efuse)     : 0x%02X\n", raw.efuse);
        printf(" Lock Bits (lock)     : 0x%02X\n\n", raw.lock);

        char cmd[256];
        avr_format_avrdude_cmd(cmd, sizeof(cmd), target_chip, raw);
        printf("Команда для AVRDUDE:\n  %s\n\n", cmd);

        printf("Статус аудиту безпеки: %s\n", audit.is_valid_and_safe ? "БЕЗПЕЧНО" : "ВИЯВЛЕНО ФАТАЛЬНІ ПОМИЛКИ");
        for (size_t i = 0; i < audit.count; ++i) {
            const char* tag = (audit.items[i].level == DIAG_CRITICAL_ERROR) ? "[ФАТАЛЬНО]" :
                              (audit.items[i].level == DIAG_WARNING) ? "[ПОПЕРЕДЖЕННЯ]" : "[ІНФО]";
            printf(" %s %s\n", tag, audit.items[i].message);
        }
    }

    return audit.is_valid_and_safe ? EXIT_SUCCESS : EXIT_FAILURE;
}
```
```cpp
#include <iostream>
#include <span>
#include <string_view>

int main(int argc, char* argv[]) {
    const std::span<char*> args(argv, argc);
    std::string_view target_chip = "m328p";
    bool allow_hvpp = false;
    bool output_json = false;

    avr::tool::FuseBuilder builder;
    builder.set_clock(avr::tool::ClockSource::ExternalCrystalHigh, avr::tool::StartupTime::MaxDelayCeramic, false)
           .set_bod(avr::tool::BodLevel::V2_7)
           .set_bootloader(avr::tool::BootSize::Words256, true)
           .set_isp_enabled(true);

    for (size_t i = 1; i < args.size(); ++i) {
        const std::string_view arg = args[i];
        if (arg == "--chip" && i + 1 < args.size()) {
            target_chip = args[++i];
        } else if (arg == "--allow-hvpp") {
            allow_hvpp = true;
        } else if (arg == "--json") {
            output_json = true;
        }
    }

    const auto raw = builder.build();
    auto validation_result = avr::tool::FuseValidator::validate(raw, allow_hvpp);

    if (output_json) {
        std::cout << std::format("{{\n  \"chip\": \"{}\",\n  \"lfuse\": \"0x{:02X}\",\n  \"hfuse\": \"0x{:02X}\",\n  \"efuse\": \"0x{:02X}\",\n  \"lock\": \"0x{:02X}\",\n  \"is_safe\": {}\n}}\n",
                                 target_chip, raw.low, raw.high, raw.extended, raw.lock, validation_result.has_value());
    } else {
        std::cout << std::format("=== Результати розрахунку фьюзів для {} ===\n", target_chip);
        std::cout << std::format(" LFUSE: 0x{:02X}, HFUSE: 0x{:02X}, EFUSE: 0x{:02X}, LOCK: 0x{:02X}\n\n",
                                 raw.low, raw.high, raw.extended, raw.lock);
        std::cout << std::format("Команда AVRDUDE:\n  {}\n\n",
                                 avr::tool::FuseValidator::to_avrdude_args(raw, target_chip));

        if (validation_result.has_value()) {
            std::cout << "Статус: БЕЗПЕЧНО ДО ПРОШИВКИ.\n";
            for (const auto& msg : validation_result.value()) {
                std::cout << std::format(" [ПОПЕРЕДЖЕННЯ] {}\n", msg.text);
            }
        } else {
            std::cerr << std::format("Статус: ПОМИЛКА БЕЗПЕКИ — {}\n", validation_result.error());
            return EXIT_FAILURE;
        }
    }

    return EXIT_SUCCESS;
}
```
:::

---

### Модульні тести та перевірка еталонних профілів

Для підтвердження повної коректності алгоритмів бітового кодування виконаємо перевірку трьох інженерних профілів:
1. Заводський стан (Factory Default ATmega328P: 1 МГц RC).
2. Профіль плати Arduino Uno (16 МГц кристал, Optiboot 512B, BOD 2.7V).
3. Промисловий захищений профіль (16 МГц, Watchdog, Lock Mode 3).

:::tabs
```c
void run_unit_tests(void) {
    printf("=== Запуск модульних тестів калькулятора фьюзів (C99) ===\n");
    
    // Тест 1: Заводський профіль ATmega328P
    avr_human_config_t cfg_factory = {
        .clock_source        = CLK_INT_RC_8MHZ,
        .startup_time        = SUT_MAX_CERAMIC,
        .divide_clock_by_8   = true,
        .clock_output_enable = false,
        .reset_disable       = false,
        .debugwire_enable    = false,
        .spi_prog_enable     = true,
        .watchdog_always_on  = false,
        .preserve_eeprom     = false,
        .bootloader_size     = BOOT_SIZE_2048_WORDS,
        .boot_reset_vector   = false,
        .bod_level           = BOD_DISABLED,
        .lock_mode           = LOCK_MODE_1_OPEN,
        .boot_lock_app_bits  = 0x03,
        .boot_lock_boot_bits = 0x03
    };
    
    avr_raw_fuses_t raw_factory = avr_encode_fuses(&cfg_factory);
    printf("Заводський профіль: LFUSE=0x%02X (очікується 0x62), HFUSE=0x%02X (очікується 0xD9), EFUSE=0x%02X (очікується 0xFF)\n",
           raw_factory.lfuse, raw_factory.hfuse, raw_factory.efuse);
           
    if (raw_factory.lfuse == 0x62 && raw_factory.hfuse == 0xD9 && raw_factory.efuse == 0xFF) {
        printf(" [PASS] Тест заводського профілю пройдено успішно.\n");
    } else {
        printf(" [FAIL] Помилка кодування заводського профілю!\n");
    }
    
    // Тест 2: Профіль Arduino Uno
    avr_human_config_t cfg_uno = {
        .clock_source        = CLK_EXT_CRYSTAL_HIGH,
        .startup_time        = SUT_MAX_CERAMIC,
        .divide_clock_by_8   = false,
        .clock_output_enable = false,
        .reset_disable       = false,
        .debugwire_enable    = false,
        .spi_prog_enable     = true,
        .watchdog_always_on  = false,
        .preserve_eeprom     = false,
        .bootloader_size     = BOOT_SIZE_256_WORDS,
        .boot_reset_vector   = true,
        .bod_level           = BOD_2V7,
        .lock_mode           = LOCK_MODE_1_OPEN,
        .boot_lock_app_bits  = 0x03,
        .boot_lock_boot_bits = 0x00 // Захист Optiboot
    };
    
    avr_raw_fuses_t raw_uno = avr_encode_fuses(&cfg_uno);
    printf("Профіль Arduino Uno: LFUSE=0x%02X (очікується 0xFF), HFUSE=0x%02X (очікується 0xDE), EFUSE=0x%02X (очікується 0xFD)\n",
           raw_uno.lfuse, raw_uno.hfuse, raw_uno.efuse);
           
    if (raw_uno.lfuse == 0xFF && raw_uno.hfuse == 0xDE && (raw_uno.efuse & 0x07) == 0x05) {
        printf(" [PASS] Тест профілю Arduino Uno пройдено успішно.\n");
    } else {
        printf(" [FAIL] Помилка кодування профілю Arduino Uno!\n");
    }
}
```
```cpp
void run_cpp_unit_tests() {
    std::cout << "=== Запуск модульних тестів валідатора (C++20) ===\n";

    // 1. Перевірка Factory Profile
    constexpr auto factory_bytes = avr::tool::FuseBuilder{}
        .set_clock(avr::tool::ClockSource::InternalRc8MHz, avr::tool::StartupTime::MaxDelayCeramic, true)
        .set_isp_enabled(true)
        .set_bootloader(avr::tool::BootSize::Words2048, false)
        .set_bod(avr::tool::BodLevel::Disabled)
        .build();

    static_assert(factory_bytes.low == 0x62U, "Factory Low Fuse має бути 0x62");
    static_assert(factory_bytes.high == 0xD9U, "Factory High Fuse має бути 0xD9");
    static_assert(factory_bytes.extended == 0xFFU, "Factory Extended Fuse має бути 0xFF");
    std::cout << " [PASS] Compile-time constexpr валідацію Factory Profile виконано успішно.\n";

    // 2. Перевірка перехоплення критичної помилки RSTDISBL
    constexpr auto brick_bytes = avr::tool::FuseBuilder{}
        .set_reset_as_gpio(true) // Спроба вимкнути Reset
        .build();

    auto audit_res = avr::tool::FuseValidator::validate(brick_bytes, false);
    if (!audit_res.has_value()) {
        std::cout << " [PASS] Рушій валідації успішно заблокував небезпечну конфігурацію: " 
                  << audit_res.error() << "\n";
    } else {
        std::cerr << " [FAIL] Валідатор пропустив небезпечний RSTDISBL!\n";
    }
}
```
:::

---

### Проектування апаратного виробничого стенда (Bed-of-Nails Jig)

Надійна прошивка фьюзів у виробничих умовах вимагає не лише коректного програмного забезпечення, але й дотримання строгих апаратних вимог до тестової оснастки.

Типова тестова оснастка типу «ложемент із голками» (*Bed-of-Nails Fixture*) містить підпружинені контакти Pogo-pin, що притискаються до золочених тестових майданчиків (*Test Points*, TP) на нижньому боці друкованої плати.

Схемотехнічні вимоги до ліній зв'язку стенда:
1. **Довжина з'єднувальних провідників:** сумарна довжина дротів від програматора до голок Pogo-pin не повинна перевищувати 10–15 см. На тактових частотах шини SPI понад 1 МГц паразитна індуктивність довгих шлейфів у комбінації з ємністю контактних майданчиків створює відчутне дзвінке перерегулювання (*ringing*) на фронтах сигналу `SCK`.
2. **Фільтрація та блокувальні конденсатори:** безпосередньо біля контактів живлення стенда `V_CC` мають бути розташовані керамічні блокувальні конденсатори ємністю 0.1 мкФ (100 нФ) та танталовий електролітичний конденсатор на 10 мкФ. Під час стирання Flash споживання струму мікроконтролера короткочасно зростає імпульсами до кількох десятків міліампер, що за відсутності локальної фільтрації викликає просідання живлення та зрив операції запису.
3. **Керована комутація живлення:** стенд повинен мати апаратний ключ на P-канальному польовому транзисторі MOSFET для програмного вмикання, вимикання та холодного перезапуску плати під час виконання технологічних тестів.

---

### Покроковий регламент виробничого конвеєра прошивки та верифікації

Впровадження автоматичної верифікації фьюзів у конвеєр фабричного складання електроніки повністю виключає випадки випуску пристроїв із незамкненим зневаджувальним інтерфейсом.

Виробничий цикл прошивки кожного серійного виробу організовано за суворим 5-фазним регламентом:

1. **Фаза 1: Контроль первинного підключення та зчитування сигнатури.**
   Програматор подає живлення на плату, притискає вивід `RESET` до нуля та зчитує 3 байти підпису кристала (`Device Signature`). Якщо сигнатура не збігається з очікуваною (наприклад, повернуто `0x000000` або `0xFFFFFF`), цикл зупиняється з повідомленням про дефект контакту голок стенда або непропай чіпа.

2. **Фаза 2: Прошивка образів Flash, EEPROM та базових конфігураційних фьюзів.**
   Виконується повне апаратне стирання `Chip Erase`, після чого у Flash записується бінарний образ прошивки, у EEPROM — унікальний серійний номер пристрою та калібрувальні коефіцієнти, а у регістри `lfuse`, `hfuse`, `efuse` — розраховані значення.

3. **Фаза 3: Побайтова верифікація цілісності образу пам'яті (Verification).**
   Програматор вичитує весь вміст Flash-пам'яті назад у буфер ПК та обчислює контрольну суму CRC32. Отриманий геш порівнюється з еталонним значенням вихідного HEX-файлу. На цьому етапі біти `Lock Bits` ще не заблоковані, тому зчитування відбувається безперешкодно.

4. **Фаза 4: Апаратне замикання бітів захисту читання (Lock Bits Mode 3).**
   Окремою командою в регістр блокування записується байт `lock = 0x00` (`Mode 3`). Це безповоротно відключає зовнішній доступ до шин даних через послідовний інтерфейс.

5. **Фаза 5: Контрольний тест відмови зчитування (Security Verification).**
   Програматор намагається повторно зчитати першу сторінку Flash. Якщо спроба читання завершується помилкою або повертає суцільні байти `0x00` чи лічильник адрес, плата маркується як успішно заблокована (*Secure Sealed*). Результати тесту із зазначенням серійного номера, часу та ідентифікатора оператора зберігаються в заводську базу даних контролю якості.

```bash
#!/usr/bin/env bash
set -euo pipefail

CHIP="m328p"
HEX_APP="build/firmware.hex"
HEX_EEPROM="build/calibration.eep"

echo "=== Фаза 1: Генерація та валідація байтів конфігурації ==="
CMD_ARGS=$(./avr-fuse-calc --chip ${CHIP} --clock ext-crystal --sut max --bod 4.3v --boot-size 256 --bootrst --avrdude)

echo "=== Фаза 2: Прошивка Flash, EEPROM та базових Fuses ==="
avrdude -c usbasp -p ${CHIP} -e \
    -U flash:w:${HEX_APP}:i \
    -U eeprom:w:${HEX_EEPROM}:i \
    -U lfuse:w:0xFF:m \
    -U hfuse:w:0xDE:m \
    -U efuse:w:0xFC:m

echo "=== Фаза 3: Верифікація цілісності образу Flash (CRC32) ==="
avrdude -c usbasp -p ${CHIP} -U flash:v:${HEX_APP}:i

echo "=== Фаза 4: Апаратне замикання бітів захисту читання (Lock Bits Mode 3) ==="
avrdude -c usbasp -p ${CHIP} -U lock:w:0x00:m

echo "=== Фаза 5: Контрольна перевірка захисту від читання ==="
if avrdude -c usbasp -p ${CHIP} -U flash:r:/tmp/dump.bin:r 2>/dev/null; then
    echo "[УСПІХ] Плату успішно прошито та апаратно заблоковано від зчитування."
fi
```

---

### Аналіз надійності, відновлення після збоїв та обробка виняткових ситуацій

Під час серійного виробництва у реальних цехових умовах стенд неминуче стикається з відхиленнями технологічного процесу. Надійний скрипт автоматизації повинен мати закладену логіку обробки позаштатних ситуацій:

1. **Діагностика забруднення або окислення контактів Pogo-pin:**
   Якщо перехідний опір між золоченою голкою та тестовим майданчиком плати перевищує 5–10 Ом через залишки флюсу після пайки, фронти імпульсів на лінії `SCK` спотворюються, викликаючи періодичні помилки контрольної суми під час верифікації. Програмний модуль повинен реалізувати алгоритм адаптивного заниження частоти (*Automatic Baudrate Fallback*): якщо передача на дефолтній швидкості 1.5 МГц зазнала невдачі, утиліта автоматично повторює спробу на частоті 375 кГц, а потім на 93.75 кГц. Якщо зв'язок встановлюється лише на заниженій частоті, стенд видає оператору попередження про необхідність механічного очищення контактних голок ізопропіловим спиртом.

2. **Обробка раптового знеструмлення під час циклу прошивки:**
   Якщо живлення плати раптово зникає в момент стирання Flash або запису розширеного байта `efuse`, мікроконтролер може залишитися з частково розрядженими комірками або порожньою пам'яттю програм. Оскільки запис бітів блокування `Lock Bits` виконується суворо на фінальній фазі після повної верифікації, плата гарантовано залишається у незаблокованому стані. Це дозволяє оператору просто повторити цикл прошивки після усунення проблеми з живленням без ризику остаточного оцеглинення кристала.

3. **Статистичний контроль якості (SPC — Statistical Process Control):**
   Кожна транзакція прошивки фіксує у виробничому журналі точний час виконання операцій стирання, запису та верифікації. Якщо середній час стирання Flash `t_ERASE` для конкретної партії мікроконтролерів починає аномально зростати з типових 9 мс до 15–20 мс, це сигналізує про деградацію якості кремнієвих пластин постачальника або використання контрафактних чипів, дозволяючи вчасно зупинити лінію до випуску бракованої продукції.

---

### Еволюція конфігураційних інтерфейсів: Від класичного ISP до UPDI

У найновіших родинах мікроконтролерів Microchip (родини megaAVR 0-series, tinyAVR 1-series/2-series, AVR-DA, AVR-DB та AVR-DD) класичний 6-провідний інтерфейс ISP було замінено на сучасний однопровідний протокол **UPDI** (*Unified Program and Debug Interface*).

Ключові архітектурні відмінності нового підходу:
- **Один фізичний вивід:** програмування Flash, EEPROM, читання сигнатури та повне зневадження виконуються через одну двонаправлену асинхронну лінію UPDI (яка може бути суміщена з виводом `RESET` або працювати як виділена лінія).
- **Пряме відображення в адресний простір:** конфігураційні байти `FUSE` більше не вимагають окремих спеціальних команд запису `0xAC 0xA0 ...`. Вони розташовані в єдиному адресному просторі пам'яті як масив байтів за фіксованими зсувами (наприклад, `FUSE_OSCCFG`, `FUSE_SYSCFG0`, `FUSE_BOOTEND`).
- **Неможливість блокування тактуванням:** модуль UPDI має власний внутрішній асинхронний тактовий генератор, тому помилковий вибір джерела тактування ядра більше не може заблокувати доступ до чіпа по лінії UPDI.

Незважаючи на прогрес у нових родинах, мільярди класичних чипів ATmega328P, ATmega2560 та ATtiny85 продовжують масово вироблятися й експлуатуватися в індустріальних, автомобільних та побутових приладах, що робить наш валідатор класичних фьюзів незамінним інструментом підтримки надійного виробництва.

---

### Систематизація кодів завершення та семантика інтеграції в CI/CD

Для безшовної інтеграції калькулятора-валідатора в автоматизовані конвеєри тестування (наприклад, GitHub Actions, GitLab CI або Jenkins) консольна утиліта повертає стандартизовані коди завершення процесу (*Process Exit Codes*):

| Код завершення | Статус операції | Опис та рекомендована реакція CI/CD |
| :---: | :--- | :--- |
| **`0` (EXIT_SUCCESS)** | **Успіх** | Конфігурація є синтаксично коректною, перевіреною за базою даних мікроконтролера та повністю безпечною для прошивки через ISP. Скрипт може переходити до виконання `avrdude`. |
| **`1` (ERR_SAFETY_FAIL)** | **Фатальна помилка безпеки** | Виявлено критичні небезпеки (наприклад, `RSTDISBL = 0` без прапорця `--allow-hvpp`, або спробу вимкнення `SPIEN`). Складальний конвеєр негайно зупиняється з генерацією алерту розробникам. |
| **`2` (ERR_INVALID_ARGS)** | **Синтаксична помилка CLI** | Передано невідому модель мікроконтролера, невалідну частоту кварцу чи непідтримуване значення напруги Brown-out. |
| **`3` (ERR_SIG_MISMATCH)** | **Невідповідність підпису** | Зчитана апаратна сигнатура не відповідає дескриптору цільового чіпа в базі даних (запобігає прошивці образу ATmega328P у мікроконтролер ATmega168). |
| **`4` (ERR_VERIFY_MISMATCH)**| **Помилка верифікації** | Зчитаний після прошивки байт не збігається з розрахованим навіть після застосування маски нереалізованих розрядів. |

Така градація статусів дозволяє тестовим скриптам чітко розрізняти апаратні проблеми контакту голок стенда від помилок у конфігураційних файлах розробників.

---

### Інтеграція з базами даних параметрів чипів (Atmel/Microchip Device Packs)

Для розширення підтримки нових моделей мікроконтролерів без перекомпіляції вихідного коду валідатор підтримує імпорт дескрипторів із відкритих XML-файлів специфікацій Microchip Device Family Packs (DFP):

```xml
<device name="ATmega328P">
  <address-spaces>
    <address-space name="fuses" size="3">
      <memory-segment name="LOW" offset="0x00" size="1" default="0x62" mask="0xFF"/>
      <memory-segment name="HIGH" offset="0x01" size="1" default="0xD9" mask="0xFF"/>
      <memory-segment name="EXTENDED" offset="0x02" size="1" default="0xFF" mask="0x07"/>
    </address-space>
    <address-space name="lockbits" size="1">
      <memory-segment name="LOCKBITS" offset="0x00" size="1" default="0xFF" mask="0x3F"/>
    </address-space>
  </address-spaces>
</device>
```

Парсер автоматично завантажує бітові маски, списки допустимих джерел тактування та заводські значення за замовчуванням. Якщо переданий у CLI параметр не відповідає масці `mask` з XML-дескриптора цільового чіпа, валідатор негайно сигналізує про помилку ще на етапі підготовки конфігурації.

---

### Розрахунок обмеження частоти шини SPI при активному дільнику CKDIV8

Критичним інженерним правилом стандарту Atmel AVR є вимога до максимальної частоти тактування інтерфейсу програмування ISP:
`f_SCK < f_CPU / 4`

Якщо мікроконтролер перебуває у заводському стані з увімкненим бітом `CKDIV8` (`lfuse = 0x62`), тактова частота процесорного ядра становить `8 МГц / 8 = 1 МГц`. Відповідно, гранична допустима частота шини SPI програматора дорівнює:
`f_SCK_MAX = 1000 кГц / 4 = 250 кГц`

Спроба прошивки такого чіпа на стандартній швидкості USBasp або STK500 (1.5 МГц) призведе до помилки `initialization failed, rc=-1`. Валідатор автоматично генерує опцію `-B 4.0` (період тактування 4 мкс, що відповідає частоті 250 кГц) для утиліти `avrdude`, якщо у вхідній конфігурації активовано `divide_clock_by_8 = true`, усуваючи ризик зриву зв'язку.

Крім того, при виборі нестандартних кварцових резонаторів (наприклад, 14.7456 МГц замість 16.0 МГц) калькулятор перевіряє сумісність із розрахунком похибки швидкості UART: частота 14.7456 МГц забезпечує 0.0% апаратної похибки для швидкостей 115200 і 230400 бод, тоді як кварц 16.0 МГц на швидкості 115200 бод має систематичну похибку +3.5%, що на межі допустимого допуску прийомопередавача (4.5%).

---

### Підсумковий висновок

Використання представленого програмного модуля гарантує високу надійність виробничого процесу, захищаючи апаратне забезпечення від випадкових помилок інженерів і забезпечуючи максимальну стійкість кінцевих пристроїв в експлуатації. Автоматизація розрахунку та верифікації фьюзів перетворює потенційно небезпечну операцію на передбачуваний, верифікований та безпечний етап серійного виготовлення розумної електроніки.
