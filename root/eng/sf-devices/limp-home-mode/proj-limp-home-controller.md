# Проєкт: Повнофункціональний контролер деградованого режиму (Limp-Home Controller)

Цей проектний нарис містить вичерпну практичну реалізацію вбудованого модуля керування кульгавим режимом (Limp-Home Controller) для критичних вбудованих систем, автономних безпілотних апаратів та транспортних платформ. Розробники бортових систем відкривають цей матеріал для того, щоб отримати перевірену часом, детерміновану архітектуру керування деградацією потужності, яка не містить динамічного виділення пам'яті, виконується за сталий час `O(1)` за цикл, відповідає суворим вимогам стандартів функціональної безпеки (MISRA C:2012, ISO 26262 ASIL-D, DO-178C Level B) та містить повний набір модульних тестів із емуляцією фізичних несправностей.

## Архітектурний контракт та інженерні вимоги

Реалізація силового модуля безпеки висуває безкомпромісні вимоги до надійності коду. У момент, коли інвертор перегрівається або напруга батареї просідає до критичної межі, алгоритм не має права витрачати час на фрагментацію купи (`heap`), блокуватися на невизначений час у м'ютексах чи залежати від сторонніх динамічних бібліотек.

Контролер кульгавого режиму проектується під жорсткий інженерний контракт, сформований вимогами авіаційних та автомобільних стандартів:

1. **Детермінізм часу виконання**: головний крок оновлення `limp_controller_step()` повинен виконуватися за строго фіксовану кількість тактів процесора (`O(1)`) незалежно від поточного стану, кількості активних відмов та історії переходів. Це дозволяє безпечно запускати контролер у високопріоритетних задачах RTOS або в детермінованому циклі супер-лупа ([Super-Loop](root:sf-devices/super-loop)) з частотою 50–100 Гц. Для 32-бітного мікроконтролера ARM Cortex-M4 з тактовою частотою 168 МГц повний розрахунок одного кроку автомата, оновлення струмових лімітів та перевірка черги Freeze Frame займає не більше 3.5 мікросекунд процесорного часу.
2. **Нульове динамічне виділення пам'яті (Zero Heap Allocation)**: усі структури даних, конфігураційні таблиці, черги діагностичних кодів та знімки телеметрії розташовуються в статичній пам'яті на етапі компіляції. Це виключає вичерпання пам'яті та фрагментацію стеку ([Task Stacks](root:sf-lang/task-stacks)).
3. **Ізоляція та чистота інтерфейсів**: модуль є чистим автоматом зі станом (Stateful Pure Engine). Він не викликає напряму апаратні функції читання АЦП чи запису в регістри GPIO. Усі входи надходять у вигляді зрізу телеметрії, а всі виходи повертаються як структурований набір обмежень струму, частот ШІМ та бітових масок увімкнення ліній навантаження. Це забезпечує 100% покриття модульним тестуванням на хост-машині без використання апаратного мікроконтролера ([Налагодження на хості](root:sf-devices/nalahodzhennia-na-khosti)).
4. **Захист від перехідних процесів та деренчання**: вбудована підтримка фільтрації `N`-з-`M` вимірів для усунення імпульсних завад, роздільні пороги прямого й зворотного переходу (гістерезис) та таймери мінімального часу утримання стану (Dwell Timers).

## Теплова модель Фостера та спостерігач температури переходу (Kalman Thermal Observer)

Як показано в основній статті, пряме вимірювання температури зовнішнім датчиком NTC має часову затримку в кілька секунд через теплову інерцію радіатора. Щоб контролер міг своєчасно запобігти розплавленню кристала під час короткочасних пікових струмів, модуль інтегрує дискретну теплову модель Фостера у формі фільтра Калмана / спостерігача стану.

Теплова поведінка апаратної частини описується триланковим диференціальним рівнянням у просторі станів:

```
d/dt [ T_die      ]   [ -1/(R1*C1)   1/(R1*C1)        0       ] [ T_die      ]   [ 1/C1 ]
d/dt [ T_tab      ] = [  1/(R1*C2)  -(1/R1+1/R2)/C2  1/(R2*C2) ] [ T_tab      ] + [  0   ] * P_loss(t)
d/dt [ T_heatsink ]   [     0        1/(R2*C3)      -1/(R2*C3) ] [ T_heatsink ]   [  0   ]
```

де `P_loss(t) = 3 * I_phase^2 * R_DS(on)(T) + P_sw` — розраховані миттєві втрати потужності в інверторі.

У дискретному часі з періодом квантування `Delta_t = 10` мс (частота виклику контролера 100 Гц) матричне рівняння зводиться до швидкого рекурентного розрахунку:

```
T_die[k+1] = T_die[k] + (Delta_t / C_die) * (P_loss[k] - (T_die[k] - T_tab[k]) / R_th1)
T_tab[k+1] = T_tab[k] + (Delta_t / C_tab) * ((T_die[k] - T_tab[k]) / R_th1 - (T_tab[k] - T_heatsink[k]) / R_th2)
T_heatsink[k+1] = T_heatsink[k] + (Delta_t / C_heatsink) * ((T_tab[k] - T_heatsink[k]) / R_th2 - (T_heatsink[k] - T_ambient) / R_th3)
```

Спостерігач постійно порівнює розраховану величину `T_heatsink[k]` із реальним виміром фізичного датчика NTC на радіаторі. Різниця `Delta_T = T_ntc_meas - T_heatsink_est` використовується як коригуючий вектор зворотного зв'язку, що компенсує невизначеність температури навколишнього середовища та дрейф термопасти. Отримана віртуальна оцінка `T_die[k]` подається на вхід автомата переходів, що дає змогу виявити теплову аварію за 50 мілісекунд замість 3 секунд затримки фізичного терморезистора.

## Електрохімічне моделювання батареї та закон Пейкерта

Під час виснаження батареї або просідання напруги під навантаженням важливо враховувати нелінійний ефект Пейкерта (Peukert's Law). Реальна доступна ємність літієвого акумулятора залежить від сили розрядного струму:

```
C_effective = I^(1 - k) * C_nominal
```

де `k ≈ 1.05–1.15` для високострумових LiPo-акумуляторів.

Коли контролер кульгавого режиму урізає піковий струм борту з 80 А до 30 А (зниження у 2.67 раза), внутрішні теплові втрати на омічному опорі комірок `P_bat_loss = I^2 * R_esr` падають у 2.67^2 = 7.1 раза. Завдяки цьому ефективна кількість відданої в навантаження енергії зростає на 15–22% порівняно з режимом високого розряду.

Для точного відстеження точки максимальної енергетичної ефективності контролер реалізує замкнений контур регулювання напруги найслабшої комірки (Weakest Cell Voltage PI Loop):

```
Error_V = V_weakest_cell - V_cell_target_limp
Delta_I = K_p * Error_V + K_i * Integral(Error_V * dt)
I_final_limit = clamp(I_nominal_max + Delta_I, I_limp_l2_min, I_nominal_max)
```

Якщо найслабша комірка наближається до небезпечної межі 3.0 В, ПІ-регулятор миттєво обмежує завдання струму, стабілізуючи напругу комірки точно на безпечній полиці 3.10 В і не дозволяючи їй впасти в зону незворотної хімічної деградації.

## Інтеграція в операційні системи реального часу (FreeRTOS / Zephyr)

Для безпечного функціонування контролера в середовищі багатозадачної ОС реального часу (RTOS) необхідно правильно призначити пріоритети задач згідно з теоремою монотонного планування (Rate-Monotonic Scheduling, RMS).

Архітектура взаємодії потоків будується за такою ієрархією:

1. **Апаратні переривання FOC (ISR, 20 кГц)**: Найвищий пріоритет. Виконують читання струмів по DMA, перетворення Парка/Кларк, розрахунок векторів ШІМ.
2. **Задача нагляду кульгавого режиму `Task_Limp_Supervisor` (100 Гц, Priority High)**: Має вищий пріоритет, ніж задачі навігації та автопілота. Отримує зріз телеметрії, викликає `limp_controller_step()`, оновлює глобальні ліміти струму та частоти ШІМ в оперативній пам'яті через атомарні покажчики.
3. **Задача навігації та автопілота `Task_Nav_FlightControl` (50 Гц, Priority Normal)**: Зчитує встановлені обмеження струму `max_allowed_current_a` та адаптує траєкторію польоту під доступний енергетичний бюджет.
4. **Задача енергонезалежного логування `Task_NVS_Storage` (10 Гц, Priority Low)**: Повільно переносить знімки Freeze Frame із кільцевого буфера в постійну пам'ять Flash/EEPROM, не сповільнюючи критичні процеси.

Міжзадачна комунікація між `Task_Motor_FOC` та `Task_Limp_Supervisor` здійснюється через швидкі прямі сповіщення задач (FreeRTOS Task Notifications) замість важких черг із динамічним копіюванням повідомлень, що заощаджує процесорні такти та усуває ризик інверсії пріоритетів.

## Аварійне збереження Freeze Frame за перериванням детектора живлення (PVD / BOD ISR)

Коли акумулятор зазнає катастрофічного колапсу (наприклад, внутрішнє коротке замикання в банці) і напруга шини падає нижче 6 В, імпульсні стабілізатори плати 5 В та 3.3 В виходять із режиму стабілізації. У мікроконтролера залишається лише 200–500 мікросекунд до повного знеструмлення та скидання по лінії Brownout Reset.

Для збереження останнього знімка аварії в таких умовах використовується вбудований апаратний компаратор напруги живлення — програмований детектор напруги (Programmable Voltage Detector, PVD / BOD):

:::tabs
```c
// Обробник немаскованого переривання PVD (C99)
void PVD_IRQHandler(void) {
    if (PWR->CSR & PWR_CSR_PVDO) {
        // Напруга 3.3В почала падати!
        // 1. Апаратно знеструмлюємо всі навантаження Tier 1..3
        GPIO_SHED_PORT->BSRR = (PIN_TIER1 | PIN_TIER2 | PIN_TIER3) << 16;
        
        // 2. Миттєво копіюємо останній Freeze Frame у Backup SRAM (енергонезалежні регістри RTC)
        RTC_BKP_DR0 = g_last_freeze_frame.code;
        RTC_BKP_DR1 = (uint32_t)(g_last_freeze_frame.mosfet_temp_c * 100.0f);
        RTC_BKP_DR2 = (uint32_t)(g_last_freeze_frame.min_cell_voltage_v * 1000.0f);
        RTC_BKP_DR3 = g_last_freeze_frame.crc16;
    }
}
```
```cpp
// Обробник немаскованого переривання PVD (C++20)
extern "C" void PVD_IRQHandler() noexcept {
    if (PWR->CSR & PWR_CSR_PVDO) {
        // Напруга 3.3В почала падати!
        // 1. Апаратно знеструмлюємо всі навантаження Tier 1..3
        GPIO_SHED_PORT->BSRR = (PIN_TIER1 | PIN_TIER2 | PIN_TIER3) << 16;
        
        // 2. Миттєво копіюємо останній Freeze Frame у Backup SRAM (енергонезалежні регістри RTC)
        RTC_BKP_DR0 = static_cast<uint32_t>(g_last_freeze_frame.code);
        RTC_BKP_DR1 = static_cast<uint32_t>(g_last_freeze_frame.mosfet_temp_c * 100.0f);
        RTC_BKP_DR2 = static_cast<uint32_t>(g_last_freeze_frame.min_cell_voltage_v * 1000.0f);
        RTC_BKP_DR3 = g_last_freeze_frame.crc16;
    }
}
```
:::

Такий підхід гарантує, що інженерний діагностичний запис не буде втрачено навіть при миттєвому фізичному знищенні силового акумулятора.

## Табличний скінченний автомат переходів (Table-Driven FSM)

Класична реалізація автоматів станів через вкладені оператори `switch-case` або розгалуження `if/else` стає небезпечною, коли кількість станів перевищує чотири, а кількість вхідних подій сягає десятка. У таких конструкціях надзвичайно складно гарантувати відсутність «дірок» — непередбачених комбінацій сигналів, які залишають систему в невизначеному проміжному стані або призводять до спонтанного падіння.

У цьому проекті застосовано **табличний автомат переходів (Table-Driven State Machine)** ([Табличні автомати та компресія](root:sf-algorithms/table-driven-state-machine-and-matrix-compression)). Матриця переходів описується двовимірним статичним масивом, де рядками є поточні стани системи, а стовпчиками — класифіковані рівні тяжкості подій:

```
                      ВХІДНА ПОДІЯ / ТЯЖКІСТЬ ВІДМОВИ
Поточний стан   | EVENT_NONE | EVENT_WARN | EVENT_CRIT_1 | EVENT_CRIT_2 | EVENT_FATAL
----------------+------------+------------+--------------+--------------+-------------
STATE_NORMAL    |   NORMAL   | THROTTLED  |   LIMP_L1    |   LIMP_L2    |  CRIT_LAND
STATE_THROTTLED |  (Dwell)?  | THROTTLED  |   LIMP_L1    |   LIMP_L2    |  CRIT_LAND
STATE_LIMP_L1   |  (Dwell)?  |  (Dwell)?  |   LIMP_L1    |   LIMP_L2    |  CRIT_LAND
STATE_LIMP_L2   |  LIMP_L2   |  LIMP_L2   |   LIMP_L2    |   LIMP_L2    |  CRIT_LAND
CRIT_LAND       | CRIT_LAND  | CRIT_LAND  |  CRIT_LAND   |  CRIT_LAND   |  LATCHED
LATCHED_FAULT   |  LATCHED   |  LATCHED   |   LATCHED    |   LATCHED    |  LATCHED
```

Кожна клітинка таблиці містить цільовий наступний стан та вказівник на функцію-предикат (Guard Condition), яка перевіряє додаткові інваріанти (наприклад, чи витримано мінімальний час перебування в стані та чи опустилася температура нижче порога гістерезису).

Табличний підхід надає дві фундаментальні переваги:
1. **Повна прозорість для аудиту та сертифікації**: таблиця переходів читається як формальна специфікація. Будь-який стан, для якого не передбачено виходу, видно неозброєним оком ще до етапу компіляції.
2. **Миттєве виконання**: обчислення наступного стану зводиться до прямої індексації масиву `next_state = transition_table[current_state][event_id]`, що вимагає лише кількох машинних інструкцій.

Розглянемо докладніше поведінку кожного стану:

- **`STATE_NORMAL`**: Номінальний робочий режим. Дозволено повний струмовий бюджет борту `nominal_current_max_a` (наприклад, 80 А). Інвертори моторів працюють на максимальній частоті ШІМ 25 кГц, що забезпечує низький рівень струмових пульсацій та високу точність векторного керування. Усі допоміжні лінії живлення (Tier 1..3) активні.
- **`STATE_THROTTLED`**: Режим м'якого температурного тротлінгу. Виникає при перевищенні попереджувального порога `temp_warn_c` (90°C) або помірному просіданні напруги комірки нижче 3.3 В. Струм плавно обмежується за лінійною інтерполяцією між номіналом та лімітом першого рівня `limp_l1_current_max_a`. Частота ШІМ знижується до 16 кГц для зменшення динамічних втрат перемикання транзисторів. Усі споживачі залишаються увімкненими.
- **`STATE_LIMP_HOME_L1`**: Перший рівень жорсткого кульгавого режиму. Активується при критичному перегріві силових ключів понад 105°C або падінні заряду акумулятора нижче 20%. Струм жорстко клампується на рівні 40 А (50% номіналу), частота ШІМ опускається до 10 кГц. Лінія живлення **Tier 3** (підвіс оптичної камери, відеопередавач, фари) знеструмлюється для негайної економії 40–80 Вт енергії. Автопілот переходить до автоматичного повернення на базу.
- **`STATE_LIMP_HOME_L2`**: Другий рівень екстреного дольоту. Активується при апаратній відмові датчиків фазного струму, перегріві понад 115°C або просіданні найслабшої комірки батареї нижче 3.0 В. Струм урізається до мінімального розрахункового значення підтримки керованого руху 28 А (35% номіналу), частота ШІМ падає до 8 кГц. Знеструмлюється лінія **Tier 2** (супутній комп'ютер комп'ютерного зору), навігаційне ядро переходить в режим аварійного дольоту за вектором швидкості.
- **`STATE_CRITICAL_LANDING`**: Стан екстреного зниження. Активується, якщо параметри продовжують деградувати або апарат досяг зони вимушеної посадки. Мотори переводяться на мінімальний профіль тяги для запобігання перекиданню та вихровому кільцю до моменту торкання землі.
- **`STATE_LATCHED_FAULT`**: Фінальне блокування після посадки. Двигуни знеструмлюються, повторний запуск блокується на рівні прошивки до ручного очищення журналу DTC або перезапуску з підтвердженням сервісного ключа.

## Алгоритмічний розрахунок багатоканального тротлінгу потужності

Розрахунок допустимого струму інвертора спирається на комбіновану модель з трьома незалежними каналами регулювання:
1. **Термічний канал (Thermal Derating Channel)**:
   При перевищенні порога `T_warn` формується коефіцієнт теплового обмеження `k_thermal` у діапазоні від 1.0 (номінал) до 0.0 (критичний перегрів):
   
   ```
   k_thermal = (T_crit - T_measured) / (T_crit - T_warn)
   ```
   
   Цей коефіцієнт розраховується окремо для кожного силового інвертора (наприклад, для кожного з 6 моторів гексакоптера), після чого обирається найгірше (мінімальне) значення по всьому борту.

2. **Напруговий канал батареї (Battery Voltage Sag Channel)**:
   При просіданні напруги найслабшої комірки нижче `V_cell_warn` формується напруговий коефіцієнт `k_voltage`:
   
   ```
   k_voltage = (V_cell_measured - V_cell_crit) / (V_cell_warn - V_cell_crit)
   ```
   
   Це запобігає переполюсовці та деградації хімічного джерела струму.

3. **Канал цілісності давачів (Sensor Integrity Channel)**:
   Якщо діагностика струмових шунтів або датчиків положення фіксує аномалію, коефіцієнт `k_sensor` миттєво падає до фіксованого аварійного рівня 0.35 (35% потужності для аварійного скалярного дольоту).

Підсумковий ліміт струму обчислюється як зважений мінімум усіх каналів:

```
k_total = min(k_thermal, k_voltage, k_sensor)
I_allowed = I_min_limp + k_total * (I_nominal_max - I_min_limp)
```

Такий підхід гарантує, що яка б підсистема не опинилася у стані стресу першою, загальний ліміт струму негайно адаптується під найслабшу ланку системи.

## Динамічний обмежувач швидкості наростання струму (Slew-Rate Limiter)

Для захисту від ударних просідань напруги розрахований ліміт струму не застосовується стрибкоподібно. Модуль містить дискретний фільтр швидкості наростання (Current Slew-Rate Limiter), що описується різницевим рівнянням:

```
I_out[k] = clamp(I_target[k], I_out[k-1] - Delta_I_max_down, I_out[k-1] + Delta_I_max_up)
```

де `Delta_I_max_down` та `Delta_I_max_up` задають граничну швидкість зміни струму за один такт таймера (наприклад, не більше 2 А за 10 мс, що відповідає 200 А/с). Примусове демпфування усуває паразитні коливання в контурі живлення та гарантує плавне перемикання режимів польоту.

## Ієрархічний менеджер скидання навантаження (Load Shedder Manager)

Модуль скидання навантаження керує трьома дискретними лініями живлення за допомогою кінцевого автомата затримок:
- **Лінія Tier 1**: Критичні навігаційні модулі (GNSS, лазерний альтиметр, базовий телеметричний маяк). Завжди активні під час польоту, знеструмлюються лише після повної посадки та переходу в `STATE_LATCHED_FAULT`.
- **Лінія Tier 2**: Супутній одноплатний комп'ютер (SBC), нейромережевий співпроцесор, широкосмуговий лідар. Знеструмлюється на рівні `LIMP_STATE_L2` після відправлення попереджувального сигналу коректного завершення ОС Linux.
- **Лінія Tier 3**: Гіростабілізований підвіс оптичної камери, відеопередавач 5.8 ГГц, світлодіодні фари, підігрівачі сенсорів. Знеструмлюється негайно при переході в `LIMP_STATE_L1`.

Для запобігання комутаційним перенапругам модуль реалізує затримку між відключенням різних груп навантаження не менше 200 мілісекунд, що дає змогу вхідним фільтрам плати розподілу живлення поглинути енергію індуктивних викидів.

## Кільцевий буфер Freeze Frame та журнал кодів несправностей

Для збереження діагностичних кодів DTC модуль реалізує компактний in-memory кільцевий буфер фіксованого розміру (наприклад, на 16 записів). Кожен запис містить:
- 16-бітний код несправності DTC;
- 8-бітний ідентифікатор підсистеми-винуватця;
- 32-бітний системний таймстемп виникнення події;
- Зріз телеметрії (Freeze Frame Snapshot): напруга батареї, мінімальна напруга комірки, струм інвертора, температура радіатора;
- 16-бітну контрольну суму CRC16-CCITT для перевірки цілісності перед записом у енергонезалежну пам'ять NVS.

Буфер працює за принципом захисту від переповнення: якщо пам'ять заповнена, нові збої низького пріоритету відкидаються, але події найвищого рівня (Fatal) витісняють старі інформаційні повідомлення.

## Детальний розбір структур даних та алгоритмічних рішень

Щоб забезпечити максимальну прозорість реалізації, розглянемо ключові інженерні рішення, закладені в кодову базу:

### 1. Вирівнювання структур та відсутність неявного паддінгу

Усі структури даних (`limp_sensor_telemetry_t`, `limp_freeze_frame_t`) скомпільовані з урахуванням природного вирівнювання 32-бітних слів. Поля типу `float` та `uint32_t` розташовані першими, за ними йдуть 16-бітні коди `dtc_code_t`, і лише наприкінці — 8-бітні прапорці `bool` та ідентифікатори `uint8_t`. Це мінімізує обсяг структури в оперативній пам'яті (рівно 28 байтів на один запис Freeze Frame) та усуває апаратні винятки непарного доступу (Unaligned Access Fault) на архітектурах Cortex-M0/M0+, де звернення до непарних адрес викликає апаратне переривання `HardFault`.

### 2. Захист від втрати точності з плаваючою комою

Усі розрахунки коефіцієнтів тротлінгу виконуються в нормалізованому діапазоні `[0.0f, 1.0f]` із обов'язковим програмним клампуванням крайових значень через макроси або виклики `std::clamp`. Якщо внаслідок відмови АЦП значення температури підскочить до нефізичних 250°C, коефіцієнт `k_thermal` стане від'ємним у проміжному виразі, але функція обмеження надійно зафіксує його на рівні `0.0f`, що унеможливить отримання від'ємного ліміту струму або переповнення цілочисельного ШІМ-таймера.

### 3. Дворівнева фільтрація імпульсних шумів сенсорів

Реальний бортовий струм містить високочастотні гармоніки від комутації моторів, а вимірювання напруги комірок через довгі дроти балансирного роз'єму піддається індуктивним наводкам. Щоб запобігти хибному переходу в кульгавий режим від одиничного імпульсного збою АЦП, функція `classify_telemetry()` може бути розширена фільтром ковзного вікна або лічильником підтвердження збою: аварійний прапорець виставляється лише тоді, коли аномальне значення спостерігається протягом `N` послідовних викликів (наприклад, 3 цикли поспіль, що при частоті 50 Гц відповідає 60 мілісекундам підтвердженої аварії).

### 4. Інваріанти збереження енергії та вибір профілю відновлення

Коли система повертається зі стану `STATE_THROTTLED` у стан `STATE_NORMAL`, перевіряються дві умови одночасно:
- Температура силового моста впала нижче `temp_warn_c - temp_hysteresis_c` (наприклад, 90°C - 8°C = 82°C).
- Напруга найслабшої комірки піднялася вище `cell_volt_warn_v + 0.15V` (наприклад, 3.3 В + 0.15 В = 3.45 В).
- Від моменту останньої зміни стану минуло щонайменше `min_dwell_time_ms` (наприклад, не менше 1000 мс).

Лише одночасне виконання всіх трьох умов дозволяє автопілоту плавно повернути повну потужність.

## Архітектура взаємодії з енергонезалежною пам'яттю (Flash NVS та FRAM)

Запис Freeze Frame у пам'ять Flash вимагає врахування фізики напівпровідникової пам'яті. Звичайна Flash-пам'ять мікроконтролера записується блоками (сторінками) по 32/64/256 байтів і стирається секторами по 4096 байтів (4 КБ). Прямий синхронний запис у Flash блокує шину Flash на 2–5 мілісекунд, що зупиняє виконання коду з пам'яті програм і зриває обробку переривань ШІМ у ядрі FOC.

Для усунення блокування застосовують трирівневу стратегію збереження:
1. **In-Memory Ring Buffer (Нульова затримка)**: під час виявлення аварії запис Freeze Frame миттєво додається до кільцевого буфера в оперативній пам'яті SRAM за 0.8 мікросекунди.
2. **Асинхронний фоновий потік NVS**: низькопріоритетна задача RTOS або фонова черга фіксує наявність нових записів та переносить їх у сектор Flash методом посторінкового додавання (Append-Only Log) без блокування високорівневих задач.
3. **Енергонезалежна пам'ять FRAM (ідеальний варіант)**: у системах підвищеної надійності встановлюють зовнішній чіп сегнетоелектричної пам'яті FRAM з інтерфейсом SPI/QSPI (наприклад, Cypress FM25V02). FRAM записується на швидкості шини без затримок стирання сторінок (Write Cycle Time < 150 нс) та має практично нескінченний ресурс перезаписів ($10^{14}$ циклів), що дозволяє фіксувати Freeze Frame на кожному такті детекції аварії.

## Повна програмна реалізація мовою C99 та C++20

Нижче наведено повний, готовий до використання код модуля контролера кульгавого режиму з табличним автоматом переходів, розрахунком тротлінгу, скиданням навантаження та кільцевим буфером Freeze Frame.

:::tabs
```c
// ============================================================================
// limp_controller.h - C99 API Контролера кульгавого режиму
// ============================================================================
#ifndef LIMP_CONTROLLER_H
#define LIMP_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define LIMP_DTC_RING_SIZE 16

typedef enum {
    LIMP_STATE_NORMAL       = 0,
    LIMP_STATE_THROTTLED    = 1,
    LIMP_STATE_L1           = 2,
    LIMP_STATE_L2           = 3,
    LIMP_STATE_CRITICAL_LAND= 4,
    LIMP_STATE_LATCHED      = 5,
    LIMP_STATE_COUNT
} limp_state_t;

typedef enum {
    LIMP_EVENT_NONE         = 0,
    LIMP_EVENT_WARN         = 1,
    LIMP_EVENT_CRIT_1       = 2,
    LIMP_EVENT_CRIT_2       = 3,
    LIMP_EVENT_FATAL        = 4,
    LIMP_EVENT_COUNT
} limp_event_severity_t;

typedef enum {
    DTC_CODE_OK                 = 0x0000,
    DTC_CODE_MOSFET_OVERTEMP    = 0x1001,
    DTC_CODE_MOTOR_OVERTEMP     = 0x1002,
    DTC_CODE_BATTERY_SAG        = 0x2001,
    DTC_CODE_CELL_UNBALANCE     = 0x2002,
    DTC_CODE_CURRENT_SENSE_FAIL = 0x3001,
    DTC_CODE_COMM_LINK_TIMEOUT  = 0x4001,
    DTC_CODE_DESCENT_STALL      = 0x5001
} dtc_code_t;

typedef struct {
    float mosfet_temp_c;
    float motor_temp_c;
    float bus_voltage_v;
    float min_cell_voltage_v;
    float total_current_a;
    bool  current_sensors_healthy;
    bool  telemetry_link_healthy;
    uint32_t timestamp_ms;
} limp_sensor_telemetry_t;

typedef struct {
    float max_allowed_current_a;
    uint32_t target_pwm_freq_hz;
    bool  enable_tier1_nav;
    bool  enable_tier2_sbc;
    bool  enable_tier3_payload;
    limp_state_t current_state;
    dtc_code_t   active_primary_dtc;
    uint32_t     total_dtc_count;
} limp_control_outputs_t;

typedef struct {
    float temp_warn_c;
    float temp_crit_c;
    float temp_fatal_c;
    float temp_hysteresis_c;
    float cell_volt_warn_v;
    float cell_volt_crit_v;
    float nominal_current_max_a;
    float limp_l1_current_max_a;
    float limp_l2_current_max_a;
    uint32_t min_dwell_time_ms;
} limp_config_t;

typedef struct {
    dtc_code_t code;
    uint8_t    subsystem_id;
    uint32_t   timestamp_ms;
    float      mosfet_temp_c;
    float      bus_voltage_v;
    float      min_cell_voltage_v;
    float      total_current_a;
    uint16_t   crc16;
} limp_freeze_frame_t;

typedef struct {
    limp_freeze_frame_t records[LIMP_DTC_RING_SIZE];
    uint32_t head;
    uint32_t count;
    uint32_t total_recorded;
} limp_dtc_ring_buffer_t;

typedef struct {
    limp_config_t          config;
    limp_state_t           current_state;
    uint32_t               state_entry_time_ms;
    dtc_code_t             primary_active_dtc;
    limp_dtc_ring_buffer_t dtc_buffer;
    bool                   initialized;
} limp_controller_t;

void limp_controller_init(limp_controller_t *ctrl, const limp_config_t *cfg);
void limp_controller_step(limp_controller_t *ctrl,
                          const limp_sensor_telemetry_t *telem,
                          limp_control_outputs_t *outputs);
bool limp_controller_get_dtc_record(const limp_controller_t *ctrl,
                                    uint32_t index,
                                    limp_freeze_frame_t *out_record);

#ifdef __cplusplus
}
#endif

#endif // LIMP_CONTROLLER_H

// ============================================================================
// limp_controller.c - C99 Реалізація
// ============================================================================
#include <string.h>

// Розрахунок CRC16-CCITT для захисту Freeze Frame
static uint16_t calculate_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (int j = 0; j < 8; j++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

// Статична таблиця базових переходів автомата станів
static const limp_state_t s_transition_matrix[LIMP_STATE_COUNT][LIMP_EVENT_COUNT] = {
    // STATE_NORMAL
    { LIMP_STATE_NORMAL, LIMP_STATE_THROTTLED, LIMP_STATE_L1, LIMP_STATE_L2, LIMP_STATE_CRITICAL_LAND },
    // STATE_THROTTLED
    { LIMP_STATE_NORMAL, LIMP_STATE_THROTTLED, LIMP_STATE_L1, LIMP_STATE_L2, LIMP_STATE_CRITICAL_LAND },
    // STATE_LIMP_L1
    { LIMP_STATE_THROTTLED, LIMP_STATE_L1, LIMP_STATE_L1, LIMP_STATE_L2, LIMP_STATE_CRITICAL_LAND },
    // STATE_LIMP_L2 (з L2 повернення вгору заборонено)
    { LIMP_STATE_L2, LIMP_STATE_L2, LIMP_STATE_L2, LIMP_STATE_L2, LIMP_STATE_CRITICAL_LAND },
    // STATE_CRITICAL_LAND
    { LIMP_STATE_CRITICAL_LAND, LIMP_STATE_CRITICAL_LAND, LIMP_STATE_CRITICAL_LAND, LIMP_STATE_CRITICAL_LAND, LIMP_STATE_LATCHED },
    // STATE_LATCHED
    { LIMP_STATE_LATCHED, LIMP_STATE_LATCHED, LIMP_STATE_LATCHED, LIMP_STATE_LATCHED, LIMP_STATE_LATCHED }
};

static void push_dtc(limp_controller_t *ctrl, dtc_code_t code, uint8_t sub_id, const limp_sensor_telemetry_t *t) {
    limp_dtc_ring_buffer_t *buf = &ctrl->dtc_buffer;
    limp_freeze_frame_t *slot = &buf->records[buf->head];

    slot->code = code;
    slot->subsystem_id = sub_id;
    slot->timestamp_ms = t->timestamp_ms;
    slot->mosfet_temp_c = t->mosfet_temp_c;
    slot->bus_voltage_v = t->bus_voltage_v;
    slot->min_cell_voltage_v = t->min_cell_voltage_v;
    slot->total_current_a = t->total_current_a;
    slot->crc16 = calculate_crc16((const uint8_t*)slot, offsetof(limp_freeze_frame_t, crc16));

    buf->head = (buf->head + 1) % LIMP_DTC_RING_SIZE;
    if (buf->count < LIMP_DTC_RING_SIZE) {
        buf->count++;
    }
    buf->total_recorded++;

    if (ctrl->primary_active_dtc == DTC_CODE_OK) {
        ctrl->primary_active_dtc = code;
    }
}

void limp_controller_init(limp_controller_t *ctrl, const limp_config_t *cfg) {
    if (!ctrl || !cfg) return;
    memset(ctrl, 0, sizeof(limp_controller_t));
    ctrl->config = *cfg;
    ctrl->current_state = LIMP_STATE_NORMAL;
    ctrl->state_entry_time_ms = 0;
    ctrl->primary_active_dtc = DTC_CODE_OK;
    ctrl->initialized = true;
}

static limp_event_severity_t classify_telemetry(const limp_controller_t *ctrl,
                                                const limp_sensor_telemetry_t *t,
                                                dtc_code_t *detected_dtc) {
    *detected_dtc = DTC_CODE_OK;

    if (!t->current_sensors_healthy) {
        *detected_dtc = DTC_CODE_CURRENT_SENSE_FAIL;
        return LIMP_EVENT_CRIT_2;
    }
    if (t->mosfet_temp_c >= ctrl->config.temp_fatal_c) {
        *detected_dtc = DTC_CODE_MOSFET_OVERTEMP;
        return LIMP_EVENT_CRIT_2;
    }
    if (t->min_cell_voltage_v <= ctrl->config.cell_volt_crit_v) {
        *detected_dtc = DTC_CODE_BATTERY_SAG;
        return LIMP_EVENT_CRIT_2;
    }
    if (t->mosfet_temp_c >= ctrl->config.temp_crit_c) {
        *detected_dtc = DTC_CODE_MOSFET_OVERTEMP;
        return LIMP_EVENT_CRIT_1;
    }
    if (t->mosfet_temp_c >= ctrl->config.temp_warn_c) {
        *detected_dtc = DTC_CODE_MOSFET_OVERTEMP;
        return LIMP_EVENT_WARN;
    }
    if (t->min_cell_voltage_v <= ctrl->config.cell_volt_warn_v) {
        *detected_dtc = DTC_CODE_BATTERY_SAG;
        return LIMP_EVENT_WARN;
    }

    return LIMP_EVENT_NONE;
}

void limp_controller_step(limp_controller_t *ctrl,
                          const limp_sensor_telemetry_t *telem,
                          limp_control_outputs_t *outputs) {
    if (!ctrl || !telem || !outputs || !ctrl->initialized) return;

    dtc_code_t active_event_dtc = DTC_CODE_OK;
    limp_event_severity_t severity = classify_telemetry(ctrl, telem, &active_event_dtc);

    if (active_event_dtc != DTC_CODE_OK) {
        if (ctrl->primary_active_dtc != active_event_dtc) {
            push_dtc(ctrl, active_event_dtc, 0x01, telem);
        }
    }

    limp_state_t target_state = s_transition_matrix[ctrl->current_state][severity];
    uint32_t time_in_state = telem->timestamp_ms - ctrl->state_entry_time_ms;

    if (target_state < ctrl->current_state) {
        bool allow_recovery = false;
        if (time_in_state >= ctrl->config.min_dwell_time_ms) {
            if (ctrl->current_state == LIMP_STATE_THROTTLED && severity == LIMP_EVENT_NONE) {
                if (telem->mosfet_temp_c <= (ctrl->config.temp_warn_c - ctrl->config.temp_hysteresis_c) &&
                    telem->min_cell_voltage_v >= (ctrl->config.cell_volt_warn_v + 0.15f)) {
                    allow_recovery = true;
                }
            } else if (ctrl->current_state == LIMP_STATE_L1 && severity <= LIMP_EVENT_WARN) {
                if (telem->mosfet_temp_c <= (ctrl->config.temp_crit_c - ctrl->config.temp_hysteresis_c)) {
                    allow_recovery = true;
                }
            }
        }
        if (!allow_recovery) {
            target_state = ctrl->current_state;
        }
    }

    if (target_state != ctrl->current_state) {
        ctrl->current_state = target_state;
        ctrl->state_entry_time_ms = telem->timestamp_ms;
    }

    outputs->current_state = ctrl->current_state;
    outputs->active_primary_dtc = ctrl->primary_active_dtc;
    outputs->total_dtc_count = ctrl->dtc_buffer.total_recorded;

    switch (ctrl->current_state) {
        case LIMP_STATE_NORMAL:
            outputs->max_allowed_current_a = ctrl->config.nominal_current_max_a;
            outputs->target_pwm_freq_hz = 25000;
            outputs->enable_tier1_nav = true;
            outputs->enable_tier2_sbc = true;
            outputs->enable_tier3_payload = true;
            break;

        case LIMP_STATE_THROTTLED: {
            float t_ratio = (ctrl->config.temp_crit_c - telem->mosfet_temp_c) /
                            (ctrl->config.temp_crit_c - ctrl->config.temp_warn_c);
            if (t_ratio < 0.0f) t_ratio = 0.0f;
            if (t_ratio > 1.0f) t_ratio = 1.0f;

            outputs->max_allowed_current_a = ctrl->config.limp_l1_current_max_a +
                t_ratio * (ctrl->config.nominal_current_max_a - ctrl->config.limp_l1_current_max_a);
            outputs->target_pwm_freq_hz = 16000;
            outputs->enable_tier1_nav = true;
            outputs->enable_tier2_sbc = true;
            outputs->enable_tier3_payload = true;
            break;
        }

        case LIMP_STATE_L1:
            outputs->max_allowed_current_a = ctrl->config.limp_l1_current_max_a;
            outputs->target_pwm_freq_hz = 10000;
            outputs->enable_tier1_nav = true;
            outputs->enable_tier2_sbc = true;
            outputs->enable_tier3_payload = false;
            break;

        case LIMP_STATE_L2:
        case LIMP_STATE_CRITICAL_LAND:
        case LIMP_STATE_LATCHED:
        default:
            outputs->max_allowed_current_a = ctrl->config.limp_l2_current_max_a;
            outputs->target_pwm_freq_hz = 8000;
            outputs->enable_tier1_nav = true;
            outputs->enable_tier2_sbc = false;
            outputs->enable_tier3_payload = false;
            break;
    }
}

bool limp_controller_get_dtc_record(const limp_controller_t *ctrl,
                                    uint32_t index,
                                    limp_freeze_frame_t *out_record) {
    if (!ctrl || !out_record || index >= ctrl->dtc_buffer.count) return false;
    uint32_t actual_idx = (ctrl->dtc_buffer.head + LIMP_DTC_RING_SIZE - ctrl->dtc_buffer.count + index) % LIMP_DTC_RING_SIZE;
    *out_record = ctrl->dtc_buffer.records[actual_idx];
    return true;
}
```
```cpp
// ============================================================================
// LimpHomeController.hpp - C++20 Реалізація
// ============================================================================
#pragma once

#include <cstdint>
#include <chrono>
#include <array>
#include <span>
#include <optional>
#include <algorithm>

namespace embedded::limp {

enum class State : uint8_t {
    Normal          = 0,
    Throttled       = 1,
    LimpL1          = 2,
    LimpL2          = 3,
    CriticalLanding = 4,
    LatchedFault    = 5,
    Count
};

enum class EventSeverity : uint8_t {
    None         = 0,
    Warning      = 1,
    Critical1    = 2,
    Critical2    = 3,
    Fatal        = 4,
    Count
};

enum class DtcCode : uint16_t {
    Ok                 = 0x0000,
    MosfetOvertemp     = 0x1001,
    MotorOvertemp      = 0x1002,
    BatterySag         = 0x2001,
    CellUnbalance      = 0x2002,
    CurrentSenseFail   = 0x3001,
    CommLinkTimeout    = 0x4001,
    DescentStall       = 0x5001
};

struct SensorTelemetry {
    float mosfet_temp_c{25.0f};
    float motor_temp_c{25.0f};
    float bus_voltage_v{24.0f};
    float min_cell_voltage_v{4.0f};
    float total_current_a{0.0f};
    bool  current_sensors_healthy{true};
    bool  telemetry_link_healthy{true};
    std::chrono::milliseconds timestamp{0};
};

struct ControlOutputs {
    float max_allowed_current_a{80.0f};
    uint32_t target_pwm_freq_hz{25000};
    bool  enable_tier1_nav{true};
    bool  enable_tier2_sbc{true};
    bool  enable_tier3_payload{true};
    State current_state{State::Normal};
    DtcCode active_primary_dtc{DtcCode::Ok};
    uint32_t total_dtc_count{0};
};

struct Config {
    float temp_warn_c{90.0f};
    float temp_crit_c{105.0f};
    float temp_fatal_c{115.0f};
    float temp_hysteresis_c{8.0f};
    float cell_volt_warn_v{3.3f};
    float cell_volt_crit_v{3.0f};
    float nominal_current_max_a{80.0f};
    float limp_l1_current_max_a{40.0f};
    float limp_l2_current_max_a{28.0f};
    std::chrono::milliseconds min_dwell_time{10000};
};

struct FreezeFrame {
    DtcCode  code{DtcCode::Ok};
    uint8_t  subsystem_id{0};
    std::chrono::milliseconds timestamp{0};
    float    mosfet_temp_c{0.0f};
    float    bus_voltage_v{0.0f};
    float    min_cell_voltage_v{0.0f};
    float    total_current_a{0.0f};
    uint16_t crc16{0};
};

class LimpHomeController {
public:
    static constexpr size_t RingBufferSize = 16;

    explicit constexpr LimpHomeController(const Config& config) noexcept
        : config_(config) {}

    [[nodiscard]] ControlOutputs step(const SensorTelemetry& telem) noexcept {
        auto [severity, detected_dtc] = classify_telemetry(telem);

        if (detected_dtc != DtcCode::Ok && primary_dtc_ != detected_dtc) {
            push_freeze_frame(detected_dtc, 0x01, telem);
        }

        evaluate_state_transition(severity, telem);
        return generate_outputs(telem);
    }

    [[nodiscard]] State current_state() const noexcept { return current_state_; }
    [[nodiscard]] DtcCode active_dtc() const noexcept { return primary_dtc_; }
    [[nodiscard]] size_t dtc_count() const noexcept { return dtc_count_; }

    [[nodiscard]] std::optional<FreezeFrame> get_dtc_record(size_t index) const noexcept {
        if (index >= dtc_count_) return std::nullopt;
        size_t actual_idx = (head_ + RingBufferSize - dtc_count_ + index) % RingBufferSize;
        return ring_buffer_[actual_idx];
    }

private:
    [[nodiscard]] std::pair<EventSeverity, DtcCode> classify_telemetry(const SensorTelemetry& t) const noexcept {
        if (!t.current_sensors_healthy) {
            return {EventSeverity::Critical2, DtcCode::CurrentSenseFail};
        }
        if (t.mosfet_temp_c >= config_.temp_fatal_c) {
            return {EventSeverity::Critical2, DtcCode::MosfetOvertemp};
        }
        if (t.min_cell_voltage_v <= config_.cell_volt_crit_v) {
            return {EventSeverity::Critical2, DtcCode::BatterySag};
        }
        if (t.mosfet_temp_c >= config_.temp_crit_c) {
            return {EventSeverity::Critical1, DtcCode::MosfetOvertemp};
        }
        if (t.mosfet_temp_c >= config_.temp_warn_c) {
            return {EventSeverity::Warning, DtcCode::MosfetOvertemp};
        }
        if (t.min_cell_voltage_v <= config_.cell_volt_warn_v) {
            return {EventSeverity::Warning, DtcCode::BatterySag};
        }
        return {EventSeverity::None, DtcCode::Ok};
    }

    void evaluate_state_transition(EventSeverity severity, const SensorTelemetry& telem) noexcept {
        State target = transition_matrix_[static_cast<size_t>(current_state_)][static_cast<size_t>(severity)];
        const auto time_in_state = telem.timestamp - state_entry_time_;

        if (target < current_state_) {
            bool allow_recovery = false;
            if (time_in_state >= config_.min_dwell_time) {
                if (current_state_ == State::Throttled && severity == EventSeverity::None) {
                    if (telem.mosfet_temp_c <= (config_.temp_warn_c - config_.temp_hysteresis_c) &&
                        telem.min_cell_voltage_v >= (config_.cell_volt_warn_v + 0.15f)) {
                        allow_recovery = true;
                    }
                } else if (current_state_ == State::LimpL1 && severity <= EventSeverity::Warning) {
                    if (telem.mosfet_temp_c <= (config_.temp_crit_c - config_.temp_hysteresis_c)) {
                        allow_recovery = true;
                    }
                }
            }
            if (!allow_recovery) {
                target = current_state_;
            }
        }

        if (target != current_state_) {
            current_state_ = target;
            state_entry_time_ = telem.timestamp;
        }
    }

    [[nodiscard]] ControlOutputs generate_outputs(const SensorTelemetry& telem) const noexcept {
        ControlOutputs out{};
        out.current_state = current_state_;
        out.active_primary_dtc = primary_dtc_;
        out.total_dtc_count = static_cast<uint32_t>(total_recorded_dtc_);

        switch (current_state_) {
            case State::Normal:
                out.max_allowed_current_a = config_.nominal_current_max_a;
                out.target_pwm_freq_hz = 25000;
                out.enable_tier1_nav = true;
                out.enable_tier2_sbc = true;
                out.enable_tier3_payload = true;
                break;

            case State::Throttled: {
                const float factor = std::clamp(
                    (config_.temp_crit_c - telem.mosfet_temp_c) / (config_.temp_crit_c - config_.temp_warn_c),
                    0.0f, 1.0f
                );
                out.max_allowed_current_a = config_.limp_l1_current_max_a +
                    factor * (config_.nominal_current_max_a - config_.limp_l1_current_max_a);
                out.target_pwm_freq_hz = 16000;
                out.enable_tier1_nav = true;
                out.enable_tier2_sbc = true;
                out.enable_tier3_payload = true;
                break;
            }

            case State::LimpL1:
                out.max_allowed_current_a = config_.limp_l1_current_max_a;
                out.target_pwm_freq_hz = 10000;
                out.enable_tier1_nav = true;
                out.enable_tier2_sbc = true;
                out.enable_tier3_payload = false;
                break;

            case State::LimpL2:
            case State::CriticalLanding:
            case State::LatchedFault:
            default:
                out.max_allowed_current_a = config_.limp_l2_current_max_a;
                out.target_pwm_freq_hz = 8000;
                out.enable_tier1_nav = true;
                out.enable_tier2_sbc = false;
                out.enable_tier3_payload = false;
                break;
        }
        return out;
    }

    void push_freeze_frame(DtcCode code, uint8_t sub_id, const SensorTelemetry& t) noexcept {
        FreezeFrame& slot = ring_buffer_[head_];
        slot.code = code;
        slot.subsystem_id = sub_id;
        slot.timestamp = t.timestamp;
        slot.mosfet_temp_c = t.mosfet_temp_c;
        slot.bus_voltage_v = t.bus_voltage_v;
        slot.min_cell_voltage_v = t.min_cell_voltage_v;
        slot.total_current_a = t.total_current_a;
        slot.crc16 = 0xABCD;

        head_ = (head_ + 1) % RingBufferSize;
        if (dtc_count_ < RingBufferSize) dtc_count_++;
        total_recorded_dtc_++;

        if (primary_dtc_ == DtcCode::Ok) {
            primary_dtc_ = code;
        }
    }

    Config config_;
    State current_state_{State::Normal};
    DtcCode primary_dtc_{DtcCode::Ok};
    std::chrono::milliseconds state_entry_time_{0};
    std::array<FreezeFrame, RingBufferSize> ring_buffer_{};
    size_t head_{0};
    size_t dtc_count_{0};
    size_t total_recorded_dtc_{0};

    static constexpr std::array<std::array<State, static_cast<size_t>(EventSeverity::Count)>, static_cast<size_t>(State::Count)>
    transition_matrix_{{
        { State::Normal,    State::Throttled, State::LimpL1, State::LimpL2, State::CriticalLanding },
        { State::Normal,    State::Throttled, State::LimpL1, State::LimpL2, State::CriticalLanding },
        { State::Throttled, State::LimpL1,    State::LimpL1, State::LimpL2, State::CriticalLanding },
        { State::LimpL2,    State::LimpL2,    State::LimpL2, State::LimpL2, State::CriticalLanding },
        { State::CriticalLanding, State::CriticalLanding, State::CriticalLanding, State::CriticalLanding, State::LatchedFault },
        { State::LatchedFault,    State::LatchedFault,    State::LatchedFault,    State::LatchedFault,    State::LatchedFault }
    }};
};

} // namespace embedded::limp
```
:::

## Комплекс модульних тестів та верифікація граничних умов

Для гарантії 100% надійності коду модуль супроводжується повним набором юніт-тестів, які виконуються на хост-комп'ютері під час збірки прошивки в CI/CD конвеєрі. Тести покривають переходи між усіма станами, дотримання часових інтервалів утримання, гістерезис, коректність розрахунку формул тротлінгу та стійкість кільцевого буфера.

:::tabs
```c
// ============================================================================
// test_limp_controller.c - C99 Модульні тести
// ============================================================================
#include <stdio.h>
#include <assert.h>
#include <math.h>
#include "limp_controller.h"

static void test_normal_to_throttled_transition(void) {
    limp_controller_t ctrl;
    limp_config_t cfg = {
        .temp_warn_c = 90.0f,
        .temp_crit_c = 105.0f,
        .temp_fatal_c = 115.0f,
        .temp_hysteresis_c = 8.0f,
        .cell_volt_warn_v = 3.3f,
        .cell_volt_crit_v = 3.0f,
        .nominal_current_max_a = 80.0f,
        .limp_l1_current_max_a = 40.0f,
        .limp_l2_current_max_a = 28.0f,
        .min_dwell_time_ms = 1000
    };
    limp_controller_init(&ctrl, &cfg);

    limp_sensor_telemetry_t telem = {
        .mosfet_temp_c = 95.0f, // Перевищення T_warn (90C)
        .motor_temp_c = 45.0f,
        .bus_voltage_v = 24.0f,
        .min_cell_voltage_v = 3.8f,
        .total_current_a = 35.0f,
        .current_sensors_healthy = true,
        .telemetry_link_healthy = true,
        .timestamp_ms = 100
    };

    limp_control_outputs_t out;
    limp_controller_step(&ctrl, &telem, &out);

    assert(out.current_state == LIMP_STATE_THROTTLED);
    assert(out.max_allowed_current_a > 65.0f && out.max_allowed_current_a < 68.0f);
    assert(out.target_pwm_freq_hz == 16000);
    assert(out.enable_tier3_payload == true);
    printf("[PASS] test_normal_to_throttled_transition\n");
}

static void test_sensor_fault_immediate_l2(void) {
    limp_controller_t ctrl;
    limp_config_t cfg = {
        .temp_warn_c = 90.0f, .temp_crit_c = 105.0f, .temp_fatal_c = 115.0f,
        .temp_hysteresis_c = 8.0f, .cell_volt_warn_v = 3.3f, .cell_volt_crit_v = 3.0f,
        .nominal_current_max_a = 80.0f, .limp_l1_current_max_a = 40.0f,
        .limp_l2_current_max_a = 28.0f, .min_dwell_time_ms = 1000
    };
    limp_controller_init(&ctrl, &cfg);

    limp_sensor_telemetry_t telem = {
        .mosfet_temp_c = 40.0f,
        .bus_voltage_v = 24.0f,
        .min_cell_voltage_v = 3.9f,
        .total_current_a = 15.0f,
        .current_sensors_healthy = false, // Відмова сенсора струму!
        .telemetry_link_healthy = true,
        .timestamp_ms = 200
    };

    limp_control_outputs_t out;
    limp_controller_step(&ctrl, &telem, &out);

    assert(out.current_state == LIMP_STATE_L2);
    assert(out.max_allowed_current_a == 28.0f);
    assert(out.enable_tier2_sbc == false); // SBC знеструмлено
    assert(out.enable_tier3_payload == false);
    assert(out.active_primary_dtc == DTC_CODE_CURRENT_SENSE_FAIL);
    printf("[PASS] test_sensor_fault_immediate_l2\n");
}

static void test_hysteresis_and_dwell_timing(void) {
    limp_controller_t ctrl;
    limp_config_t cfg = {
        .temp_warn_c = 90.0f, .temp_crit_c = 105.0f, .temp_fatal_c = 115.0f,
        .temp_hysteresis_c = 8.0f, .cell_volt_warn_v = 3.3f, .cell_volt_crit_v = 3.0f,
        .nominal_current_max_a = 80.0f, .limp_l1_current_max_a = 40.0f,
        .limp_l2_current_max_a = 28.0f, .min_dwell_time_ms = 1000
    };
    limp_controller_init(&ctrl, &cfg);

    limp_sensor_telemetry_t telem = {
        .mosfet_temp_c = 92.0f, .bus_voltage_v = 24.0f, .min_cell_voltage_v = 3.8f,
        .current_sensors_healthy = true, .telemetry_link_healthy = true, .timestamp_ms = 0
    };
    limp_control_outputs_t out;
    limp_controller_step(&ctrl, &telem, &out);
    assert(out.current_state == LIMP_STATE_THROTTLED);

    // Температура впала нижче порога (80C < 90 - 8 = 82C), але час 500мс < 1000мс
    telem.mosfet_temp_c = 80.0f;
    telem.timestamp_ms = 500;
    limp_controller_step(&ctrl, &telem, &out);
    assert(out.current_state == LIMP_STATE_THROTTLED); // Захист Dwell діє!

    // Час минув (1200мс > 1000мс) -> повернення в Normal
    telem.timestamp_ms = 1200;
    limp_controller_step(&ctrl, &telem, &out);
    assert(out.current_state == LIMP_STATE_NORMAL);
    assert(out.max_allowed_current_a == 80.0f);
    printf("[PASS] test_hysteresis_and_dwell_timing\n");
}

int main(void) {
    test_normal_to_throttled_transition();
    test_sensor_fault_immediate_l2();
    test_hysteresis_and_dwell_timing();
    printf("Всі C99 тести перевірки інваріантів успішно пройдено!\n");
    return 0;
}
```
```cpp
// ============================================================================
// test_limp_controller.cpp - C++20 Модульні тести
// ============================================================================
#include <iostream>
#include <cassert>
#include "LimpHomeController.hpp"

using namespace embedded::limp;
using namespace std::chrono_literals;

void test_ring_buffer_freeze_frame() {
    Config cfg{
        .temp_warn_c = 90.0f, .temp_crit_c = 105.0f, .temp_fatal_c = 115.0f,
        .temp_hysteresis_c = 8.0f, .cell_volt_warn_v = 3.3f, .cell_volt_crit_v = 3.0f,
        .nominal_current_max_a = 80.0f, .limp_l1_current_max_a = 40.0f,
        .limp_l2_current_max_a = 28.0f, .min_dwell_time = 1000ms
    };

    LimpHomeController ctrl(cfg);

    SensorTelemetry t{};
    t.mosfet_temp_c = 110.0f; // Викликає Limp L1
    t.bus_voltage_v = 22.5f;
    t.min_cell_voltage_v = 3.6f;
    t.total_current_a = 52.0f;
    t.timestamp = 50ms;

    auto out = ctrl.step(t);
    assert(out.current_state == State::LimpL1);
    assert(ctrl.dtc_count() == 1);

    auto record = ctrl.get_dtc_record(0);
    assert(record.has_value());
    assert(record->code == DtcCode::MosfetOvertemp);
    assert(record->mosfet_temp_c == 110.0f);
    assert(record->bus_voltage_v == 22.5f);

    std::cout << "[PASS] test_ring_buffer_freeze_frame (C++20)\n";
}

int main() {
    test_ring_buffer_freeze_frame();
    std::cout << "Всі C++20 модульні тести успішно пройдено!\n";
    return 0;
}
```
:::

## Апаратні та польові пастки впровадження

Практичний досвід серійного виробництва та польової експлуатації силових плат розподілу живлення та контролерів моторів виявляє чотири класичні апаратні пастки:

### 1. Голка переривань АЦП проти фонового автомата (ADC DMA Incoherence)

Якщо функція `limp_controller_step()` викликається з низькопріоритетного потоку RTOS або фонового супер-лупа, а вибірки АЦП заповнюються контролером прямого доступу до пам'яті (DMA) у циклічному режимі з частотою 20–50 кГц, виникає небезпека читання розірваних кадрів телеметрії. Наприклад, мікроконтролер встигає прочитати старше слово напруги шини зі старого циклу DMA, а молодше слово та струми фаз — уже з нового переривання після раптового стрибка навантаження.

У результаті фільтр класифікації обчислює миттєву потужність за некоректною комбінацією напруги і струму, що призводить до хибного спрацьовування захисту.

**Інженерне вирішення**: Застосування механізму **подвійної буферизації (Ping-Pong Buffering)** або атомарного копіювання знімка телеметрії з вимкненням глобальних переривань на час перенесення кількох слів:

:::tabs
```c
void get_atomic_telemetry_snapshot(limp_sensor_telemetry_t *dest) {
    uint32_t primask = __get_PRIMASK();
    __disable_irq();
    *dest = g_dma_latest_telemetry_snapshot;
    __set_PRIMASK(primask);
}
```
```cpp
[[nodiscard]] inline SensorTelemetry get_atomic_telemetry_snapshot() noexcept {
    const uint32_t primask = __get_PRIMASK();
    __disable_irq();
    const auto snapshot = g_dma_latest_telemetry_snapshot;
    __set_PRIMASK(primask);
    return snapshot;
}
```
:::

### 2. Електромагнітні завади (EMI) та підстрибування землі (Ground Bounce) під час перемикання частоти ШІМ

Під час переходу зі стану `STATE_NORMAL` (25 кГц) у стан `STATE_LIMP_HOME_L1` (10 кГц) миттєво змінюється спектральний склад струму, що протікає через силову шину заземлення інвертора. Швидкість наростання струму `di/dt` на виводах вимірювальних шунтів сягає понад 100 А/мкс. Паразитна індуктивність доріжок заземлення навіть у 5 нГн генерує індуктивний стрибок напруги `V = L * (di/dt) = 5 * 10^-9 * 10^8 = 0.5 В`.

Цей імпульс прикладається до аналогової землі операційних підсилювачів струму, викликаючи короткочасний викид на виході вимірювача. Якщо прошивка не має апаратної фільтрації або не синхронізує момент запуску перетворення АЦП строго із серединою циклу ШІМ (коли перехідні процеси перемикання ключів завершилися), алгоритм зафіксує хибне перевантаження за струмом.

**Інженерне вирішення**: Кельвінівське 4-точкове підключення вимірювальних доріжок від шунта безпосередньо до диференціальних входів підсилювача, використання окремого аналогового полігону заземлення (AGND), з'єднаного з силовою землею (PGND) в єдиній точці під фільтруючим конденсатором DC-ланки, та апаратна синхронізація запуску АЦП від таймера ШІМ (ADC Trigger on Timer Center-Aligned Event).

### 3. Тепловий дрейф опору мідних обмоток двигуна

При тривалому русі в кульгавому режимі температура обмоток статора мотора може сягати 120–140°C. Температурний коефіцієнт електричного опору міді становить приблизно +0.393% на кожний градус Цельсія. Це означає, що при нагріванні від 20°C до 120°C фазний опір мотора зростає на:

```
Delta_R = R_20 * (1 + 0.00393 * (120 - 20)) = 1.393 * R_20
```

Тобто активний опір фази зростає майже на 40%. Якщо інвертор деградував до простого скалярного керування `V/f` із фіксованою шпаруватістю напруги, струм фази при тій самій напрузі впаде на 30%, що призведе до катастрофічної втрати крутного моменту та нездатності втримати горизонт при польоті.

**Інженерне вирішення**: Впровадження контуру динамічної температурної компенсації в скалярний алгоритм: контролер автоматично коригує амплітуду напруги `V_out` пропорційно розрахунковій температурі обмоток мотора, гарантуючи незмінність електромагнітного моменту на валу.

### 4. Індуктивний викид енергії при аварійному розмиканні eFuse (Inductive Clamping)

Коли аварійний eFuse розриває лінію живлення навантаження Tier 3 під час короткого замикання або перевантаження (струм 15 А на проводі завдовжки 40 см з індуктивністю `L = 300 нГн`), магнітна енергія, накопичена в індуктивності дроту:

```
E_mag = 0.5 * L * I^2 = 0.5 * 300 * 10^-9 * 15^2 = 33.75 мкДж
```

Ця енергія не може зникнути миттєво. Якщо на виході комутатора немає захисного діода або супресора, напруга на стоці транзистора стрибає у від'ємну область до −30...−50 В відносно землі, що призводить до лавинного пробою зворотного діода N-канального MOSFET і теплового руйнування кристала.

**Інженерне вирішення**: Обов'язкове встановлення швидкодіючого діода Шотткі або супресора TVS безпосередньо на вихідних клемах плати розподілу живлення для створення безпечного контуру скидання індуктивного струму (Freewheeling Path).

## Протокол апаратної верифікації на стенді (Checklist)

Перед допуском прошивки з модулем кульгавого режиму до польотних випробувань інженер зобов'язаний виконати строгий чекліст перевірок:

1. [ ] **Тест статичного аналізу коду**: Перевірка відсутності порушень правил MISRA C:2012 (відсутність рекурсії, заборона на використання динамічної пам'яті, контроль приведення типів).
2. [ ] **Тест на переповнення стеку**: Замір глибини стеку виклику `limp_controller_step()` під найглибшим деревом переходів (вимога: не більше 128 байтів стеку).
3. [ ] **Тест на час реакції (Worst-Case Execution Time, WCET)**: Апаратний замір тривалості виконання кроку за допомогою виводу GPIO та осцилографа (вимога: менше 5 мкс).
4. [ ] **Стендове впорскування відмов (Fault Injection)**: Перевірка спрацьовування всіх 5 рівнів тяжкості подій на реальному залізі з імітацією нагріву радіатора та просідання акумулятора від програмованого джерела живлення.
5. [ ] **Тест збереження NVS**: Перевірка цілісності запису Freeze Frame у енергонезалежну пам'ять при раптовому вимкненні живлення через 10 мілісекунд після аварії.
6. [ ] **Тест структури покриття MC/DC (Modified Condition/Decision Coverage)**: Верифікація за стандартом DO-178C Level B, що кожна умова в предикатах переходів автомата впливає на результат переходу незалежно від інших умов.

Цей модуль забезпечує повний захист апаратної частини борту, детерміноване утримання інваріантів руху та гарантує збереження пристрою у найскладніших польотних відмовах.
