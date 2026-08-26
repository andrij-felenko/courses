# Причина скидання як діагноз

<preknowlist>
- [Послідовність graceful reset](root:embedded/reset-sequence) — чому впорядковане згортання роботи вимагає збереження діагностичного сліду перед перезапуском
- [Сторожовий таймер (Watchdog)](root:sf-devices/watchdog) — як апаратний сторож захищає систему від тихих зависань і чому його спрацьовування є аварійним симптомом
- [Аналіз адрес аварій через addr2line](root:embedded/addr2line-workflow) — техніка зіставлення збереженого лічильника команд (PC) та адреси повернення (LR) з вихідним кодом прошивки за допомогою ELF-файлу
- [Петля перезапусків: мотор, просадка, скидання](root:embedded/petlia-perezapuskiv) — як фізичні просадки напруги та апаратні перезапуски утворюють нескінченний цикл відмов
- [HAL, LL та робота з регістрами](root:embedded/hal-ll-registers) — прямий доступ до системних контролерів SCB та RCC на рівні апаратних бітів
</preknowlist>

Безпілотний апарат у польоті на мить сіпнувся й перейшов у режим аварійного вимкнення двигунів. Промисловий контролер у шафі керування раптово обірвав сесію зв'язку Modbus і через вісімдесят мілісекунд почав завантажуватися з нуля. Автономний телеметричний давач у полі, який мав надсилати звіти раз на добу, несподівано вийшов на зв'язок посеред ночі з лічильником аптайму в три секунди. У всіх цих випадках сталася одна й та сама подія — мікроконтролер зазнав перезавантаження.

У настільних операційних системах аварійне падіння процесу супроводжується записом core dump, трасуванням стека в системний журнал та кодом завершення. У голому мікроконтролері (bare-metal) або системі під керуванням RTOS перезавантаження за замовчуванням виглядає безслідним: апаратний тригер скидає ядро, лічильник команд стрибає на вектор `Reset_Handler`, стартап-код затирає пам'ять `.bss` нулями, переініціалізує `.data` і викликає `main()`. Для розробника, який не заклав механізмів фіксації аварій, пристрій просто «якось перезавантажився», а спроба відтворити дефект на столі під дебагером нічого не дає.

Проте сам кремній ніколи не скидається «просто так». Апаратні вузли мікроконтролера фіксують точну фізичну причину кожної події скидання в спеціальних регістрах стану (RCC, RMU, RCM, RSTSRC). Коли ж процесорне ядро зазнає фатального краху — ділення на нуль, звернення за нульовим покажчиком, виконання сміття замість інструкцій чи спроби запису у вимкнену периферію — ядро ARM Cortex-M перед входом у HardFault автоматично зберігає повний контекст виконання на стек. Якщо зберегти цей контекст у спеціальній енергонезалежній ділянці оперативної пам'яті (Retention RAM), що не очищується під час перезавантаження, пристрій отримує повноцінну «чорну скриньку» (Flight Recorder). Перезапуск перетворюється з містичної поломки на вичерпний діагностичний звіт.

---

### Класифікація апаратних прапорців скидання MCU

Усі події, здатні скинути мікроконтролер, сходяться в єдиний апаратний блок — контролер скидання та тактування (у STM32 це `RCC`, у Silicon Labs EFM32 — `RMU`, у NXP Kinetis — `RCM`, у ESP32 — `RTC_CNTL`). Цей блок містить регістр статусу (наприклад, `RCC_CSR` або `RCC_RSR`), окремі біти якого є тригерами-защіпками для кожного фізичного джерела скидання.

```
 Джерела скидання              Регістр RCC_CSR                  Стан системи
 ──────────────────            ────────────────                 ────────────
 [ Подача 3.3 В   ] ───► [ bit 30: PORRSTF  ] ───► Холодний старт (Power-On)
 [ Просадка VDD   ] ───► [ bit 25: BORRSTF  ] ───► Аварія живлення (Brownout)
 [ Сторож IWDG    ] ───► [ bit 29: IWDGRSTF ] ───► Зависання задачі (Watchdog)
 [ Сторож WWDG    ] ───► [ bit 30: WWDGRSTF ] ───► Порушення таймінгу вікна
 [ NVIC_System    ] ───► [ bit 28: SFTRSTF  ] ───► Програмний ресет / Assert
 [ Ніжка NRST     ] ───► [ bit 26: PINRSTF  ] ───► Кнопка / SWD / Супервізор
```

Кожен із цих прапорців відповідає за конкретну фізичну чи програмну природу події:

1. **POR / PDR (Power-On Reset / Power-Down Reset)**. Сигналізує про подачу напруги живлення від нуля до робочого рівня або її повне зникнення. Це нормальний «холодний старт» пристрою при вмиканні батареї чи блоку живлення.
2. **BOR (Brown-Out Reset)**. Спрацьовує, коли напруга живлення `VDD` не зникла повністю, але просіла нижче критичного порогу стабільної роботи логіки ядра (типово 2.1–2.7 В залежно від конфігурації Option Bytes). Це діагноз проблем із фізичним живленням: пусковий струм колекторного мотора, увімкнення потужного радіомодуля на слабкій батареї або недостатня ємність блокувальних конденсаторів.
3. **IWDG (Independent Watchdog Reset)**. Фіксує тайм-аут незалежного сторожового таймера, що тактується від окремого низькочастотного генератора (LSI, ~32 кГц). Це свідчення мертвого зависання: код застряг у нескінченному блокуючому циклі, RTOS увійшла в стан взаємного блокування (deadlock), або пріоритетне переривання монополізувало процесорний час і не віддає його фоновим задачам.
4. **WWDG (Window Watchdog Reset)**. Прапорець віконного сторожового таймера. На відміну від IWDG, він вимагає скидання не просто «до вичерпання тайм-ауту», а суворо всередині часового вікна (не зарано й не запізно). Його спрацьовування викриває джиттер часових інтервалів, порушення порядку виконання задач або спробу зловмисного зламу прошивки з прискореним пропуском інструкцій.
5. **SFT / SFTRST (Software Reset)**. Програмне скидання, ініційоване самим ядром через запис у регістр `AIRCR` викликом `NVIC_SystemReset()`. Це наслідок свідомого рішення коду: завершення оновлення по повітрю (OTA), реакція на спрацьовування макросу `ASSERT()`, або вимушене перезавантаження після виявлення фатального винятку HardFault.
6. **PIN / PINRST / NRST**. Скидання через зміну логічного рівня на зовнішньому фізичному виводі NRST. Джерелом може бути ручне натискання кнопки користувачем, зовнішня мікросхема супервізора напруги, дебагер по інтерфейсу SWD/JTAG або електромагнітна завада, наведена на довгий провідник лінії ресету.
7. **LPWRRST (Low-Power Reset)**. Виникає при спробі несанкціонованого переходу в глибокі режими сну (Stop / Standby), коли в Option Bytes активний апаратний захист від засинання.

![Апаратні джерела скидання та мультиплексор RCC_CSR](/root/course/embedded/prychyna-skydannia-iak-diahnoz/img/reset-reason-flags.svg)
*Схема мультиплексування тригерів скидання в регістрах MCU. Прапорці є апаратно липкими: якщо не очистити регістр бітом RMVF під час першого запуску, попередні причини ресету накопичуються й спотворюють подальшу діагностику.*

#### Пастка накопичення «липких» прапорців

Головна підводна камінь апаратних регістрів скидання полягає в тому, що їхні біти є **накопичувальними (sticky bits)**. Апаратне скидання процесора не очищує біти попередніх ресетів.

Якщо мікроконтролер увімкнули вперше, у регістрі `RCC_CSR` встановлюються біти `PORRSTF` та `PINRSTF`. Якщо після цього прошивка працюватиме три дні, а потім зависне й буде перезапущена сторожовим таймером IWDG, після перезавантаження регістр міститиме `PORRSTF | PINRSTF | IWDGRSTF`. Якщо прошивка не скине ці прапорці, а пізніше розробник натисне кнопку Reset на платі, у регістрі залишаться всі чотири біти одночасно. Зрозуміти, яка саме подія спричинила *останній* перезапуск, стає неможливо.

Звідси випливає залізне правило архітектури завантаження:

> 💡 **Правило точки входу:** Регістр причин скидання необхідно зчитати в оперативну пам'ять на найпершому кроці функції `main()` (до ініціалізації периферії та запуску ОС) і **негайно очистити апаратний регістр** записом біта `RMVF` (Reset Flag Remove, `RCC->CSR |= RCC_CSR_RMVF`).

Очищення бітом `RMVF` гарантує, що наступний перезапуск принесе в регістр виключно свіжі прапорці, породжені конкретним інцидентом.

---

### Анатомія краху в ядрі ARM Cortex-M

Коли мікроконтролер падає не через зовнішнє живлення чи сторожовий таймер, а через програмну помилку, усередині процесорного ядра ARM Cortex-M розгортається складна послідовність апаратних подій.

Архітектура ARMv7-M (Cortex-M3, M4, M7) та ARMv8-M (Cortex-M23, M33) має багаторівневу систему апаратних винятків (Exceptions):

* **MemManage (Memory Management Fault)** — виникає при порушенні прав доступу, сконфігурованих у модулі захисту пам'яті (MPU), спробі виконання коду з ділянок пам'яті з прапорцем eXecute Never (XN) або зверненні до неіснуючої пам'яті, якщо MPU це відстежує.
* **BusFault** — виникає при апаратній помилці шини AHB/AXI під час вибірки інструкції, читання або запису даних (наприклад, звернення за адресою, де фізично немає пам'яті, або читання регістрів модуля, чиє тактування в RCC не було ввімкнене).
* **UsageFault** — виникає при спробі виконати невизначену інструкцію (Undefined Instruction), переході на адресу з парним LSB (порушення обов'язкового біта Thumb State T у регістрі EPSR), спробі цілочисельного ділення на нуль (якщо ввімкнено біт `DIV_0_TRP`) або несинхронізованому доступі за невирівняною адресою (біт `UNALIGN_TRP`).
* **HardFault** — загальний катастрофічний виняток найвищого пріоритету.

За замовчуванням після скидання MCU окремі обробники `MemManage`, `BusFault` та `UsageFault` **вимкнені** в системному регістрі `SCB->SHCSR` (System Handler Control and State Register). Якщо стається будь-яка з цих помилок, ядро виконує **ескалацію (Fault Escalation)** і перенаправляє виконання в універсальний `HardFault_Handler`. Більше того, якщо помилка стається всередині самого обробника винятку, відбувається подвійний збій (Double Fault), який також безумовно падає в HardFault.

#### Регістри діагностики збоїв System Control Block (SCB)

Щоб з'ясувати причину катастрофи, ядро містить групу спеціалізованих 32-бітних діагностичних регістрів у блоці SCB (базова адреса `0xE000ED00`):

```
       ┌─────────────────────────────────────────────────────────────┐
       │     CFSR (Configurable Fault Status Register, 0xE000ED28)   │
       ├──────────────────────────────┬───────────────┬──────────────┤
       │ UFSR (Bits 31..16)           │ BFSR (15..8)  │ MMFSR (7..0) │
       │ [DIVBYZERO, UNDEFINSTR...]   │ [PRECISERR..] │ [IACCVIOL..] │
       └──────────────────────────────┴───────────────┴──────────────┘
       ┌─────────────────────────────────────────────────────────────┐
       │     HFSR (HardFault Status Register, 0xE000ED2C)            │
       │     [FORCED (ескалація), VECTTBL (помилка вектора)]         │
       └─────────────────────────────────────────────────────────────┘
       ┌─────────────────────────────────────────────────────────────┐
       │     BFAR (BusFault Address Register, 0xE000ED38)            │
       │     Точна 32-бітна адреса шини, де стався збій              │
       └─────────────────────────────────────────────────────────────┘
```

1. **CFSR (Configurable Fault Status Register, `0xE000ED28`)**. Складається з трьох об'єднаних субрегістрів:
   * `UFSR` (UsageFault Status, старші 16 біт): біт `DIVBYZERO` сигналізує про ділення на нуль; `UNALIGNED` — незважаючи на підтримку несинхронного доступу, операція `LDRD`/`STRD` була викликана не по межі 4/8 байт; `UNDEFINSTR` — спроба ядра декодувати сміття (зазвичай через пошкоджений покажчик на функцію або збій Flash); `INVSTATE` — спроба виконати ARM-інструкцію замість Thumb (біт 0 адреси переходу дорівнював `0`).
   * `BFSR` (BusFault Status, біти 15..8): біт `PRECISERR` означає, що точну адресу збою зафіксовано в регістрі `BFAR`; біт `IMPRECISERR` вказує на асинхронний шинний збій; біт `STKERR`/`UNSTKERR` свідчить про те, що стек вийшов за межі пам'яті безпосередньо під час збереження або відновлення контексту переривання.
   * `MMFSR` (MemManage Status, молодші 8 біт): біти `DACCVIOL` та `IACCVIOL` фіксують спроби читання/запису даних або вибірки інструкцій із захищеної ділянки MPU.
2. **HFSR (HardFault Status Register, `0xE000ED2C`)**. Біт `FORCED` (біт 30) свідчить про те, що HardFault виник не сам по собі, а був викликаний ескалацією іншого винятку, обробник якого був неактивний або не зміг обробити ситуацію. Біт `VECTTBL` (біт 1) вказує на фатальне пошкодження самої таблиці векторів переривань у Flash/RAM.
3. **BFAR (`0xE000ED38`) та MMFAR (`0xE000ED34`)**. Якщо в `BFSR` встановлено біт `BFARVALID` (біт 7), 32-бітний регістр `BFAR` містить точну фізичну адресу пам'яті чи периферії, звернення до якої зруйнувало виконання програми.

#### Імпрецизійні шинні помилки (Imprecise Bus Faults)

Найпідступніший різновид апаратного краху в Cortex-M3/M4/M7 — це **імпрецизійний шинний збій (Imprecise BusFault)**.

Ядра Cortex-M оптимізують операції запису за допомогою внутрішнього асинхронного буфера запису (Write Buffer). Коли процесор виконує інструкцію збереження `STR R0, [R1]`, значення передається в буфер запису шини AHB, а лічильник команд `PC` негайно крокує далі, не чекаючи фізичного підтвердження від шини пам'яті. Якщо адреса в `R1` виявилася невалідною (наприклад, звернення до вимкненого блоку SPI або за межі RAM), шина генерує сигнал помилки через 2–5 тактів.

У цей момент ядро вже встигло виконати наступні кілька інструкцій. Коли виникає переривання BusFault, збережений на стеку лічильник команд `PC` вказує **не на інструкцію `STR`, яка спричинила аварію, а на довільну наступну інструкцію**. Біт `BFSR.IMPRECISERR` встановлюється в `1`, а біт `BFARVALID` залишається рівним `0` — регістр `BFAR` не містить адреси збою.

> 🔧 **Інженерний прийом:** Під час налагодження плаваючих HardFault ввімкніть біт `DISDEFWBUF` (біт 1) у системному регістрі `SCB->ACTLR` (`SCB->ACTLR |= SCB_ACTLR_DISDEFWBUF_Msk`). Це вимикає буфер запису AHB. Усі шинні операції стають суворо синхронними (Precise): ядро зупиняється на кожній інструкції запису до отримання відповіді шини, `BFSR.PRECISERR` стає рівним `1`, а `BFAR` завжди фіксує точну винну адресу. Плата платить за це ~5–10% швидкодії, але закриває проблему локалізації асинхронних збоїв.

---

### Апаратний стековий кадр та асемблерний трамплін

У момент виникнення винятку апаратний блок ядра Cortex-M автоматично зберігає 8 регістрів на поточний активний стек:

```
 Адреса пам'яті                Збережений регістр
 ──────────────                ──────────────────
 [SP + 28] ──────────────────► xPSR (Program Status Register)
 [SP + 24] ──────────────────► PC   (Program Counter — адреса збою!)
 [SP + 20] ──────────────────► LR   (Link Register — адреса повернення)
 [SP + 16] ──────────────────► R12  (Intra-Procedure Scratch Register)
 [SP + 12] ──────────────────► R3   (Argument / Scratch Register 3)
 [SP + 8]  ──────────────────► R2   (Argument / Scratch Register 2)
 [SP + 4]  ──────────────────► R1   (Argument / Scratch Register 1)
 [SP + 0]  ──────────────────► R0   (Argument / Scratch Register 0) ◄── Новий SP
```

Якщо в ядрі активний блок апаратної плаваючої коми (FPU, Cortex-M4F/M7) і перерваний код виконував операції з регістрами `S0`–`S15`, апаратний механізм Lazy Stacking додає до цього кадру ще 18 слів (регістри `S0`–`S15`, `FPSCR` та резервне слово вирівнювання).

#### Загадка регістра LR всередині HardFault_Handler

Коли ядро передає керування функції `HardFault_Handler`, вміст регістра `LR` більше не вказує на адресу повернення в коді. Замість цього апаратура записує в `LR` спеціальне магічне значення — **`EXC_RETURN`** (типово `0xFFFFFFFx`).

Аналіз бітів `EXC_RETURN` є критично важливим:

* **Біт 2 (SPSEL)**: `0` — кадр винятку був збережений на **Main Stack Pointer (MSP)**; `1` — кадр був збережений на **Process Stack Pointer (PSP)**. Якщо в проекті використовується FreeRTOS або Zephyr, виняток у задачі завжди складає стек на `PSP`, тоді як виняток усередині переривання — на `MSP`.
* **Біт 4 (FTYPE)**: `0` — було збережено розширений апаратний кадр FPU (26 слів); `1` — базовий стандартний кадр (8 слів).

Через це написати надійний обробник HardFault виключно мовою C неможливо: стандартний пролог C-функції збереже на стек власні змінні, змінить регістр `SP` і зіпсує відносні зміщення кадру до того, як код встигне їх прочитати.

Рішення полягає у створенні **голого асемблерного трампліна (`__attribute__((naked))`)**, який перевіряє `EXC_RETURN`, витягує правильний покажчик стека в регістр `R0` і передає його першим аргументом у діагностичну функцію.

![Апаратне зняття стекового кадру та регістри винятків ARM Cortex-M](/root/course/embedded/prychyna-skydannia-iak-diahnoz/img/cortex-m-stack-frame.svg)
*Анатомія автоматичного збереження стекового кадру ядром Cortex-M під час HardFault. Асемблерний трамплін перевіряє біт 2 регістра LR (EXC_RETURN), витягує покажчик активного стека (MSP або PSP) та передає збережені значення PC, LR і R0-R3 у C-обробник разом із діагностичними регістрами SCB.*

---

### Збереження даних краху: Retention RAM та .noinit секція

Ми отримали всі дані про аварію: регістри SCB, лічильник команд `PC`, адресу виклику `LR`, стан регістрів `R0`–`R12` і прапорці `RCC_CSR`. Але HardFault не дозволяє продовжувати звичайну роботу — ядро зобов'язане перезапуститися через `NVIC_SystemReset()`. Як передати зібраний знімок через перезапуск новому екземпляру прошивки?

Фізична пам'ять SRAM побудована на тригерах із перехресними КМОН-інверторами. Поки напруга `VDD` не падає нижче порогу утримання даних (~1.0–1.2 В), **гарячий перезапуск (Software Reset, Watchdog Reset, Pin Reset) фізично не руйнує стан комірок SRAM**.

Головний ворог збережених даних — це не кремній, а стандартний файл ініціалізації середовища C/C++ (`startup_stm32.s` / `Reset_Handler`). Стандартний стартап після кожного ресету проходить у циклі по адресах секції `.bss` і безумовно заповнює їх нулями `0x00`, а секцію `.data` перезаписує початковими значеннями з Flash.

#### Конфігурація Linker Script (.noinit)

Щоб захистити структуру аварійного дампу від затирання стартапом, у скрипті компонувальника (Linker Script, `.ld`) створюють спеціальну секцію з атрибутом `NOLOAD`:

```ld
/* memory.ld — додавання секції неініціалізованої пам'яті */
MEMORY
{
  FLASH (rx)      : ORIGIN = 0x08000000, LENGTH = 512K
  RAM (xrw)       : ORIGIN = 0x20000000, LENGTH = 128K
}

SECTIONS
{
  /* Стандартні секції .text, .data, .bss ... */

  /* Секція, яку C-стартап НЕ повинен затирати при скиданні */
  .noinit (NOLOAD) :
  {
    . = ALIGN(4);
    _snoinit = .;
    *(.noinit .noinit.*)
    . = ALIGN(4);
    _enoinit = .;
  } > RAM
}
```

У коді C та C++ буфер аварійної скриньки прив'язується до цієї секції за допомогою атрибута компілятора:

:::tabs

@tab C

```c
__attribute__((section(".noinit"))) static crash_dump_t g_crash_dump;
```

@tab C++

```cpp
[[gnu::section(".noinit")]] alignas(4) inline CrashRecord g_crashRecord;
```

:::

#### Захист від шуму холодного старту (Magic & CRC)

Оскільки секція `.noinit` ніколи не затирається стартапом, при першому холодному вмиканні живлення (Power-On Reset) у ній знаходиться випадкове цифрове сміття — хаотичний розподіл нулів та одиниць, зумовлений технологічною асиметрією транзисторів кристала.

Щоб відрізнити валідний аварійний дамп від випадкового шуму холодного старту, структура дампу обов'язково захищається двома полями:
1. **Magic Signature (`0x43525348` — ASCII «CRSH»)** у першому 32-бітному слові.
2. **Контрольна сума CRC32**, що розраховується по всьому тілу структури (апаратним модулем CRC мікроконтролера або швидкою табличною функцією).

При завантаженні прошивка перевіряє: якщо `dump.magic == CRASH_MAGIC` і `calculate_crc32(&dump) == dump.crc32`, у пам'яті лежить справжній знімок аварії, що пережив перезавантаження. Якщо хоча б один біт не сходиться — пам'ять вважається неініціалізованим сміттям, зануляється й готується до запису майбутніх подій.

---

### Організація чорної скриньки (Flight Recorder)

Структура аварійного журналу має бути компактною (щоб вміститися в 128–512 байтів Retention RAM), але вичерпною для повного відновлення ланцюга подій.

![Життєвий цикл аварійного дампу](/root/course/embedded/prychyna-skydannia-iak-diahnoz/img/crash-dump-lifecycle.svg)
*Повний життєвий цикл чорної скриньки: від перехоплення винятку в ядрі та фіксації знімка в Retention RAM (.noinit) до збереження крізь апаратний ресет, валідації за CRC32 та передачі телеметрії при наступному сеансі зв'язку.*

#### Повний життєвий цикл чорної скриньки

1. **Фаза аварії**: Спрацьовує виняток HardFault, сторож IWDG або макрос `ASSERT()`. Обробник перехоплює виконання, забороняє всі інші переривання (`__disable_irq()`), вимикає небезпечні виконавчі механізми (мотори, нагрівачі), формує структуру `crash_dump_t` у секції `.noinit`, розраховує CRC32, виконує бар'єр пам'яті `__DSB()` та викликає `NVIC_SystemReset()`.
2. **Фаза перезавантаження**: Відбувається апаратне скидання. Стартап-код ініціалізує стек і системні змінні, пропускаючи секцію `.noinit`.
3. **Фаза ранньої перевірки**: На перших рядках `main()` викликається функція перевірки причин скидання. Вона зчитує та зберігає сирі прапорці `RCC->CSR`, скидає регістр апаратури бітом `RMVF`, після чого валідує дамп у `.noinit`.
4. **Фаза телеметрії**:
   * Якщо виявлено свіжий аварійний дамп, система формує з нього бінарний або JSON-пакет телеметрії.
   * Пакет записується в постійний лог на Flash-пам'ять або надсилається в пріоритетній черзі відправки (через UART, CAN, LoRaWAN, Cellular або Wi-Fi), щойно підніметься мережевий стек.
5. **Фаза квитування**: Після успішної відправки або запису в постійне сховище сигнатура `magic` у Retention RAM стирається, щоб уникнути повторного відправлення того самого звіту при планових перезапусках.

---

### Реалізація модуля діагностики аварій на C та C++

Розглянемо повну промислову реалізацію модуля: заголовок структури даних, асемблерний трамплін HardFault, обробник зняття знімка та процедуру аналізу причин скидання при старті.

:::tabs

@tab C

```c
// crash_dump.h — структури та інтерфейс діагностики крахів
#ifndef CRASH_DUMP_H
#define CRASH_DUMP_H

#include <stdint.h>
#include <stdbool.h>

#define CRASH_DUMP_MAGIC    0x43525348U  // ASCII 'CRSH'
#define CRASH_STACK_WORDS   16U

// Класифікована причина скидання MCU
typedef enum {
    RESET_CAUSE_UNKNOWN     = 0,
    RESET_CAUSE_COLD_BOOT   = 1,  // Power-on reset (POR/PDR)
    RESET_CAUSE_BROWNOUT    = 2,  // Просадка напруги живлення (BOR)
    RESET_CAUSE_WATCHDOG    = 3,  // Таймаут сторожового таймера (IWDG/WWDG)
    RESET_CAUSE_SOFTWARE    = 4,  // Програмний ресет / Assert (SFTRST)
    RESET_CAUSE_PIN_RESET   = 5,  // Зовнішня кнопка / сигнал NRST
    RESET_CAUSE_HARDFAULT   = 6   // Апаратний виняток HardFault
} reset_cause_t;

// Структура збереженого контексту аварії
typedef struct __attribute__((packed)) {
    uint32_t magic;                 // CRASH_DUMP_MAGIC
    uint32_t rcc_csr;               // Сирий стан регістру RCC_CSR
    uint32_t reset_cause;           // Розкодована причина reset_cause_t
    uint32_t uptime_ms;             // Час роботи до збою (SysTick)
    
    // Регістри ядра, збережені апаратурою на стек
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;                    // Адреса повернення (хто викликав)
    uint32_t pc;                    // Адреса інструкції, де стався крах
    uint32_t xpsr;
    
    // Регістри діагностики SCB
    uint32_t cfsr;                  // UFSR + BFSR + MMFSR
    uint32_t hfsr;                  // HardFault Status
    uint32_t bfar;                  // Bus Fault Address
    uint32_t mmfar;                 // MemManage Fault Address
    uint32_t exc_return;            // Значення LR при вході у Fault Handler
    
    // Знімок верхівки стека
    uint32_t stack_dump[CRASH_STACK_WORDS];
    
    // Інформація про Assert (якщо збій програмний)
    char assert_file[32];
    uint32_t assert_line;
    
    uint32_t crc32;                 // Контрольна сума структури
} crash_dump_t;

void crash_dump_early_init(void);
bool crash_dump_has_valid_record(void);
const crash_dump_t* crash_dump_get(void);
void crash_dump_clear(void);
void crash_dump_software_assert(const char* file, uint32_t line);

#endif // CRASH_DUMP_H
```

```c
// crash_dump.c — реалізація перехоплення та збереження краху
#include "crash_dump.h"
#include <string.h>

// Макроси базових регістрів ARM Cortex-M та STM32 RCC
#define SCB_CFSR    (*(volatile uint32_t*)0xE000ED28U)
#define SCB_HFSR    (*(volatile uint32_t*)0xE000ED2CU)
#define SCB_MMFAR   (*(volatile uint32_t*)0xE000ED34U)
#define SCB_BFAR    (*(volatile uint32_t*)0xE000ED38U)
#define SCB_AIRCR   (*(volatile uint32_t*)0xE000ED0CU)

#define RCC_CSR     (*(volatile uint32_t*)0x40023874U) // Приклад адреси для STM32F4
#define RCC_CSR_RMVF_BIT    (1U << 24)
#define RCC_CSR_BOR_BIT     (1U << 25)
#define RCC_CSR_PIN_BIT     (1U << 26)
#define RCC_CSR_POR_BIT     (1U << 27)
#define RCC_CSR_SFT_BIT     (1U << 28)
#define RCC_CSR_IWDG_BIT    (1U << 29)
#define RCC_CSR_WWDG_BIT    (1U << 30)

// Розміщення в секції Retention RAM (.noinit)
__attribute__((section(".noinit"))) static crash_dump_t g_crash_dump;
static uint32_t g_saved_rcc_csr = 0;
static reset_cause_t g_detected_cause = RESET_CAUSE_UNKNOWN;

// Простий швидкий CRC32 (IEEE 802.3)
static uint32_t calc_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1U)));
        }
    }
    return ~crc;
}

// Рання ініціалізація та фіксація прапорців RCC_CSR
void crash_dump_early_init(void) {
    g_saved_rcc_csr = RCC_CSR;
    
    // Негайне очищення накопичувальних прапорців
    RCC_CSR |= RCC_CSR_RMVF_BIT;
    
    // Перевірка наявності валідного дампу HardFault у .noinit
    if (crash_dump_has_valid_record()) {
        g_detected_cause = (reset_cause_t)g_crash_dump.reset_cause;
        return;
    }
    
    // Розкодування апаратних прапорців контролера скидання
    if (g_saved_rcc_csr & RCC_CSR_BOR_BIT) {
        g_detected_cause = RESET_CAUSE_BROWNOUT;
    } else if (g_saved_rcc_csr & RCC_CSR_POR_BIT) {
        g_detected_cause = RESET_CAUSE_COLD_BOOT;
    } else if ((g_saved_rcc_csr & RCC_CSR_IWDG_BIT) || (g_saved_rcc_csr & RCC_CSR_WWDG_BIT)) {
        g_detected_cause = RESET_CAUSE_WATCHDOG;
    } else if (g_saved_rcc_csr & RCC_CSR_SFT_BIT) {
        g_detected_cause = RESET_CAUSE_SOFTWARE;
    } else if (g_saved_rcc_csr & RCC_CSR_PIN_BIT) {
        g_detected_cause = RESET_CAUSE_PIN_RESET;
    } else {
        g_detected_cause = RESET_CAUSE_UNKNOWN;
    }
}

bool crash_dump_has_valid_record(void) {
    if (g_crash_dump.magic != CRASH_DUMP_MAGIC) {
        return false;
    }
    size_t payload_len = sizeof(crash_dump_t) - sizeof(uint32_t); // Без поля crc32
    uint32_t expected_crc = calc_crc32((const uint8_t*)&g_crash_dump, payload_len);
    return (g_crash_dump.crc32 == expected_crc);
}

const crash_dump_t* crash_dump_get(void) {
    return &g_crash_dump;
}

void crash_dump_clear(void) {
    g_crash_dump.magic = 0;
    g_crash_dump.crc32 = 0;
}

// C-обробник аварії, що викликається з асемблерного трампліна
void prv_c_hardfault_handler(const uint32_t *stack_frame, uint32_t exc_return) {
    // 1. Заборона всіх переривань
    __asm volatile("cpsid i" : : : "memory");
    
    // 2. Заповнення структури дампу
    g_crash_dump.magic = CRASH_DUMP_MAGIC;
    g_crash_dump.rcc_csr = g_saved_rcc_csr;
    g_crash_dump.reset_cause = RESET_CAUSE_HARDFAULT;
    g_crash_dump.uptime_ms = 0; // Якщо доступний таймер SysTick
    
    g_crash_dump.r0   = stack_frame[0];
    g_crash_dump.r1   = stack_frame[1];
    g_crash_dump.r2   = stack_frame[2];
    g_crash_dump.r3   = stack_frame[3];
    g_crash_dump.r12  = stack_frame[4];
    g_crash_dump.lr   = stack_frame[5];
    g_crash_dump.pc   = stack_frame[6];
    g_crash_dump.xpsr = stack_frame[7];
    
    g_crash_dump.cfsr  = SCB_CFSR;
    g_crash_dump.hfsr  = SCB_HFSR;
    g_crash_dump.bfar  = SCB_BFAR;
    g_crash_dump.mmfar = SCB_MMFAR;
    g_crash_dump.exc_return = exc_return;
    
    // Копіювання слів стека аварії
    for (uint32_t i = 0; i < CRASH_STACK_WORDS; ++i) {
        g_crash_dump.stack_dump[i] = stack_frame[i];
    }
    
    g_crash_dump.assert_file[0] = '\0';
    g_crash_dump.assert_line = 0;
    
    // Розрахунок CRC32
    size_t payload_len = sizeof(crash_dump_t) - sizeof(uint32_t);
    g_crash_dump.crc32 = calc_crc32((const uint8_t*)&g_crash_dump, payload_len);
    
    // 3. Бар'єр пам'яті та системний перезапуск
    __asm volatile("dsb" : : : "memory");
    SCB_AIRCR = 0x05FA0000U | (1U << 2); // SYSRESETREQ
    for (;;) { }
}

// Голий асемблерний трамплін для перехоплення HardFault
__attribute__((naked)) void HardFault_Handler(void) {
    __asm volatile(
        "tst   lr, #4               \n" // Перевірка біта 2 EXC_RETURN (SPSEL)
        "ite   eq                   \n"
        "mrseq r0, msp              \n" // Якщо 0 -> стек MSP у R0
        "mrsne r0, psp              \n" // Якщо 1 -> стек PSP у R0
        "mov   r1, lr               \n" // EXC_RETURN у R1
        "b     prv_c_hardfault_handler \n"
    );
}

// Програмний Assert
void crash_dump_software_assert(const char* file, uint32_t line) {
    __asm volatile("cpsid i" : : : "memory");
    
    g_crash_dump.magic = CRASH_DUMP_MAGIC;
    g_crash_dump.rcc_csr = g_saved_rcc_csr;
    g_crash_dump.reset_cause = RESET_CAUSE_SOFTWARE;
    g_crash_dump.uptime_ms = 0;
    
    g_crash_dump.cfsr = 0;
    g_crash_dump.hfsr = 0;
    g_crash_dump.bfar = 0;
    g_crash_dump.mmfar = 0;
    
    strncpy(g_crash_dump.assert_file, file, sizeof(g_crash_dump.assert_file) - 1);
    g_crash_dump.assert_file[sizeof(g_crash_dump.assert_file) - 1] = '\0';
    g_crash_dump.assert_line = line;
    
    size_t payload_len = sizeof(crash_dump_t) - sizeof(uint32_t);
    g_crash_dump.crc32 = calc_crc32((const uint8_t*)&g_crash_dump, payload_len);
    
    __asm volatile("dsb" : : : "memory");
    SCB_AIRCR = 0x05FA0000U | (1U << 2);
    for (;;) { }
}
```

@tab C++

```cpp
// CrashDump.hpp — об'єктно-орієнтований діагностичний інтерфейс
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <array>

namespace Fault {

enum class ResetCause : uint32_t {
    Unknown     = 0,
    ColdBoot    = 1,
    Brownout    = 2,
    Watchdog    = 3,
    Software    = 4,
    PinReset    = 5,
    HardFault   = 6
};

struct alignas(4) CrashRecord {
    static constexpr uint32_t MagicValue = 0x43525348U; // 'CRSH'
    static constexpr size_t StackWordsCount = 16;

    uint32_t magic{0};
    uint32_t rawRccCsr{0};
    ResetCause cause{ResetCause::Unknown};
    uint32_t uptimeMs{0};

    // Стековий кадр ARM Cortex-M
    uint32_t r0{0};
    uint32_t r1{0};
    uint32_t r2{0};
    uint32_t r3{0};
    uint32_t r12{0};
    uint32_t lr{0};
    uint32_t pc{0};
    uint32_t xpsr{0};

    // Діагностичні регістри SCB
    uint32_t cfsr{0};
    uint32_t hfsr{0};
    uint32_t bfar{0};
    uint32_t mmfar{0};
    uint32_t excReturn{0};

    std::array<uint32_t, StackWordsCount> stackDump{};
    std::array<char, 32> assertFile{};
    uint32_t assertLine{0};

    uint32_t crc32{0};
};

class BlackBox {
public:
    static void earlyInit() noexcept;
    [[nodiscard]] static bool hasValidRecord() noexcept;
    [[nodiscard]] static const CrashRecord& getRecord() noexcept;
    static void clear() noexcept;
    
    static void reportAssert(std::string_view file, uint32_t line) noexcept;
    [[nodiscard]] static constexpr std::string_view causeToString(ResetCause cause) noexcept;

private:
    static uint32_t calculateCrc32(std::span<const uint8_t> data) noexcept;
};

constexpr std::string_view BlackBox::causeToString(ResetCause cause) noexcept {
    switch (cause) {
        case ResetCause::ColdBoot:  return "Power-On Reset (Cold Boot)";
        case ResetCause::Brownout:  return "Brown-Out Voltage Dip (BOR)";
        case ResetCause::Watchdog:  return "Watchdog Timeout (IWDG/WWDG)";
        case ResetCause::Software:  return "Software Reset / Assert";
        case ResetCause::PinReset:  return "External Pin Reset (NRST)";
        case ResetCause::HardFault: return "Hardware Exception (HardFault)";
        default:                    return "Unknown Reset Cause";
    }
}

} // namespace Fault
```

```cpp
// CrashDump.cpp — реалізація діагностичного реєстратора на C++
#include "CrashDump.hpp"
#include <cstring>
#include <algorithm>

namespace Fault {

namespace {
    // Апаратні адреси STM32 та ARM Cortex-M SCB
    constexpr uintptr_t ScbBase   = 0xE000ED00U;
    volatile uint32_t& scbCfsr    = *reinterpret_cast<volatile uint32_t*>(ScbBase + 0x28U);
    volatile uint32_t& scbHfsr    = *reinterpret_cast<volatile uint32_t*>(ScbBase + 0x2CU);
    volatile uint32_t& scbMmfar   = *reinterpret_cast<volatile uint32_t*>(ScbBase + 0x34U);
    volatile uint32_t& scbBfar    = *reinterpret_cast<volatile uint32_t*>(ScbBase + 0x38U);
    volatile uint32_t& scbAircr   = *reinterpret_cast<volatile uint32_t*>(ScbBase + 0x0CU);

    constexpr uintptr_t RccCsrAddr = 0x40023874U;
    volatile uint32_t& rccCsr     = *reinterpret_cast<volatile uint32_t*>(RccCsrAddr);

    constexpr uint32_t RccRmvfBit = 1U << 24;
    constexpr uint32_t RccBorBit  = 1U << 25;
    constexpr uint32_t RccPinBit  = 1U << 26;
    constexpr uint32_t RccPorBit  = 1U << 27;
    constexpr uint32_t RccSftBit  = 1U << 28;
    constexpr uint32_t RccIwdgBit = 1U << 29;
    constexpr uint32_t RccWwdgBit = 1U << 30;

    // Змінна дампу в Retention RAM
    __attribute__((section(".noinit"))) CrashRecord g_persistentRecord;
    uint32_t g_rawCsr = 0;
    ResetCause g_bootCause = ResetCause::Unknown;
}

uint32_t BlackBox::calculateCrc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFU;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (size_t bit = 0; bit < 8; ++bit) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1U)));
        }
    }
    return ~crc;
}

void BlackBox::earlyInit() noexcept {
    g_rawCsr = rccCsr;
    rccCsr |= RccRmvfBit; // Очищення липких прапорців

    if (hasValidRecord()) {
        g_bootCause = g_persistentRecord.cause;
        return;
    }

    if (g_rawCsr & RccBorBit) {
        g_bootCause = ResetCause::Brownout;
    } else if (g_rawCsr & RccPorBit) {
        g_bootCause = ResetCause::ColdBoot;
    } else if ((g_rawCsr & RccIwdgBit) || (g_rawCsr & RccWwdgBit)) {
        g_bootCause = ResetCause::Watchdog;
    } else if (g_rawCsr & RccSftBit) {
        g_bootCause = ResetCause::Software;
    } else if (g_rawCsr & RccPinBit) {
        g_bootCause = ResetCause::PinReset;
    } else {
        g_bootCause = ResetCause::Unknown;
    }
}

bool BlackBox::hasValidRecord() noexcept {
    if (g_persistentRecord.magic != CrashRecord::MagicValue) {
        return false;
    }
    const auto payload = std::span<const uint8_t>(
        reinterpret_cast<const uint8_t*>(&g_persistentRecord),
        sizeof(CrashRecord) - sizeof(uint32_t)
    );
    return g_persistentRecord.crc32 == calculateCrc32(payload);
}

const CrashRecord& BlackBox::getRecord() noexcept {
    return g_persistentRecord;
}

void BlackBox::clear() noexcept {
    g_persistentRecord.magic = 0;
    g_persistentRecord.crc32 = 0;
}

void BlackBox::reportAssert(std::string_view file, uint32_t line) noexcept {
    asm volatile("cpsid i" ::: "memory");

    g_persistentRecord.magic = CrashRecord::MagicValue;
    g_persistentRecord.rawRccCsr = g_rawCsr;
    g_persistentRecord.cause = ResetCause::Software;
    g_persistentRecord.uptimeMs = 0;

    g_persistentRecord.cfsr = 0;
    g_persistentRecord.hfsr = 0;
    g_persistentRecord.bfar = 0;
    g_persistentRecord.mmfar = 0;

    const size_t copyLen = std::min(file.size(), g_persistentRecord.assertFile.size() - 1);
    std::memcpy(g_persistentRecord.assertFile.data(), file.data(), copyLen);
    g_persistentRecord.assertFile[copyLen] = '\0';
    g_persistentRecord.assertLine = line;

    const auto payload = std::span<const uint8_t>(
        reinterpret_cast<const uint8_t*>(&g_persistentRecord),
        sizeof(CrashRecord) - sizeof(uint32_t)
    );
    g_persistentRecord.crc32 = calculateCrc32(payload);

    asm volatile("dsb" ::: "memory");
    scbAircr = 0x05FA0000U | (1U << 2);
    while (true) { }
}

} // namespace Fault

// C++ зв'язка з асемблерним трампліном
extern "C" void prv_c_hardfault_handler(const uint32_t* stackFrame, uint32_t excReturn) {
    asm volatile("cpsid i" ::: "memory");

    using namespace Fault;
    g_persistentRecord.magic = CrashRecord::MagicValue;
    g_persistentRecord.rawRccCsr = g_rawCsr;
    g_persistentRecord.cause = ResetCause::HardFault;
    g_persistentRecord.uptimeMs = 0;

    g_persistentRecord.r0   = stackFrame[0];
    g_persistentRecord.r1   = stackFrame[1];
    g_persistentRecord.r2   = stackFrame[2];
    g_persistentRecord.r3   = stackFrame[3];
    g_persistentRecord.r12  = stackFrame[4];
    g_persistentRecord.lr   = stackFrame[5];
    g_persistentRecord.pc   = stackFrame[6];
    g_persistentRecord.xpsr = stackFrame[7];

    g_persistentRecord.cfsr  = scbCfsr;
    g_persistentRecord.hfsr  = scbHfsr;
    g_persistentRecord.bfar  = scbBfar;
    g_persistentRecord.mmfar = scbMmfar;
    g_persistentRecord.excReturn = excReturn;

    for (size_t i = 0; i < CrashRecord::StackWordsCount; ++i) {
        g_persistentRecord.stackDump[i] = stackFrame[i];
    }

    g_persistentRecord.assertFile[0] = '\0';
    g_persistentRecord.assertLine = 0;

    const auto payload = std::span<const uint8_t>(
        reinterpret_cast<const uint8_t*>(&g_persistentRecord),
        sizeof(CrashRecord) - sizeof(uint32_t)
    );
    g_persistentRecord.crc32 = BlackBox::calculateCrc32(payload);

    asm volatile("dsb" ::: "memory");
    scbAircr = 0x05FA0000U | (1U << 2);
    while (true) { }
}
```

:::

---

### Розкодування та аналіз аварій: від дампа до рядка коду

Отримавши з дампу шістнадцяткові значення `PC`, `LR`, `CFSR` та `BFAR`, розробник переходить до локалізації дефекту у вихідному коді прошивки.

Головний інструмент дешифрування адрес — утиліта крос-компілятора **`arm-none-eabi-addr2line`**. Вона зіставляє числову адресу інструкції з налагоджувальними символами ELF-файлу компіляції (`.elf`):

```bash
# Розкодування адреси аварії (PC) та адреси повернення (LR)
arm-none-eabi-addr2line -e build/firmware.elf -a -f -C 0x08001a42 0x08002df8
```

Вивід команди показує точну назву функції, вихідний файл та номер рядка:

```
0x08001a42
sensor_read_pressure
/home/dev/src/drivers/bmp280.c:142
0x08002df8
telemetry_task_step
/home/dev/src/tasks/telemetry.c:89
```

#### Типові діагностичні патерни (Crash Signatures)

Зіставлення значень регістрів дозволяє миттєво визначити клас проблеми:

```
  Симптом у дампах                       Причина в коді
 ──────────────────────────────────      ───────────────────────────────────────
  PC = 0x00000000, UFSR = INVSTATE  ───► Виклик NULL-покажчика на функцію
  CFSR = PRECISERR, BFAR = периферія───► Звернення до модуля без тактування RCC
  CFSR = STKERR / UNSTKERR          ───► Переповнення стека (Stack Overflow)
  UFSR = DIVBYZERO                  ───► Цілочисельне ділення на 0
  HFSR = FORCED, CFSR = IMPRECISERR ───► Асинхронний збій буфера запису шини
```

1. **`PC = 0x00000000` або непарне сміття, `UFSR.INVSTATE = 1`**.
   * *Механізм:* Код спробував викликати функцію через покажчик `p_fn()`, який був рівний `NULL` або містив неініціалізоване сміття. Значення `LR` у дампі вказує на точний рядок, де відбувся небезпечний виклик.
2. **`CFSR.PRECISERR = 1`, `BFAR = 0x40011000`**.
   * *Механізм:* Звернення до пам'яті за адресою `0x40011000` (базова адреса блоку `USART1`). Прошивка спробувала налаштувати регістри передавача до того, як викликала `RCC->APB2ENR |= RCC_APB2ENR_USART1EN`. Шина APB відповіла помилкою шини (Bus Error).
3. **`CFSR.STKERR = 1` або `CFSR.UNSTKERR = 1`**.
   * *Механізм:* Переповнення стека (Stack Overflow). Стек задачі або переривання перетнув нижню межу RAM. Коли виникло чергове переривання, апаратний блок ядра спробував покласти 8 регістрів у неіснуючу пам'ять і звалився в HardFault.
4. **`UFSR.DIVBYZERO = 1`, `PC = 0x08003412`**.
   * *Механізм:* Інструкція `SDIV` або `UDIV` виконала ділення на змінну, значення якої дорівнювало нулю.

---

### Підсумковий інженерний чекліст

1. **Не втрачайте прапорці скидання при старті**: зчитуйте регістр `RCC_CSR` (або еквівалент вашого MCU) на першому рядку функції `main()` і негайно очищуйте апаратний регістр бітом `RMVF`.
2. **Виділіть секцію `.noinit` у Linker Script**: переконайтеся, що буфер чорної скриньки захищений атрибутом `NOLOAD` і не стирається стандартним циклом ініціалізації C-середовища.
3. **Завжди валідуйте дамп через CRC32 та магічну сигнатуру**: це єдиний надійний спосіб відрізнити справжній аварійний знімок від випадкового цифрового шуму в неініціалізованій пам'яті при холодному старті.
4. **Використовуйте асемблерний трамплін для HardFault**: аналізуйте біт 2 у регістрі `LR` (`EXC_RETURN`), щоб коректно обрати покажчик стека (`MSP` чи `PSP`) перед викликом C/C++ обробника.
5. **Вмикайте діагностичні прапорці ядра в `SCB->CCR` та `SCB->SHCSR`**: активуйте окремі обробники `UsageFault`, `BusFault`, `MemManage` та пастки ділення на нуль `DIV_0_TRP`.
6. **Зберігайте артефакти збірки (.elf) для кожного виробничого релізу**: без точного ELF-файлу розкодувати збережені адреси `PC` та `LR` у вихідні рядки коду буде неможливо.
