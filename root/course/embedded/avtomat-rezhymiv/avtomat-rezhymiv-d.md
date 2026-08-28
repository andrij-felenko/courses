# Автомат режимів: переходи, охоронці, заборонені стрибки

<preknowlist>
- [Ручні режими](root:sys-dron/manual-stabilized-modes) — відмінності між прямим керуванням кутовими швидкостями, автогоризонтом та утриманням висоти.
- [Режими з позицією](root:sys-dron/position-modes) — побудова каскадних контурів регулювання швидкості й координат за супутниковими та інерційними даними.
- [Команди MAVLink](root:embedded/mavlink-commands) — транспорт і протокол запиту зміни польотного режиму через команди SET_MODE та COMMAND_LONG.
- [Failsafe](root:sys-dron/failsafe) — логіка реагування бортового автопілота на апаратні збої та втрату каналів зв'язку.
- [RC-лінк](root:sys-dron/rc-link) — передача позицій тумблерів вибору режиму та стіків керування з пульта оператора.
</preknowlist>

Політ мультиротора чи безпілотного літака — це безперервна взаємодія каскадних контурів зворотного зв'язку, де кожен вищий рівень автоматизації надбудовує власні регулятори над базовими контурами стабілізації. Якщо оператор перемикає трипозиційний тумблер на пульті з режиму стабілізації горизонту в режим утримання позиції, коли супутниковий приймач ще не зафіксував надійного просторового положення або розширений фільтр Калмана має розбіжність оцінки швидкості у кілька метрів на секунду, система не має права сліпо активувати навігаційний контур. Наївне перемикання прапорця стану призведе до того, що інтегратор позиційного PID-регулятора спробує миттєво скомпенсувати уявну помилку координат, видасть граничний кут нахилу в 45 градусів і кине апарат у землю на повній тязі. Щоб виключити катастрофічні стани, перемикання між алгоритмами керування довіряють не простим змінним, а детермінованому скінченному автомату польотних режимів (англ. *Flight Mode Finite State Machine*, FSM).

Автомат польотних режимів — це програмне ядро автопілота, яке визначає, які саме сенсори опитуються, які контури регулювання активні в поточну мілісекунду, звідки надходять цільові уставки (зі стіків пульта, від планувальника автономної місії чи від алгоритмів аварійного порятунку) і за яких умов дозволено змінити цей стан.

## Ієрархія режимів: від сирих кутових швидкостей до автономної навігації

Кожен польотний режим являє собою конкретну конфігурацію замкнених контурів регулювання. Усі режими можна розділити на три фундаментальні класи за ступенем автономності та вимогами до сенсорного забезпечення:

1. **Ручні та стабілізовані режими (Manual / Angular Control):**
   - `Manual / Acro` (акробатичний режим): найнижчий рівень програмного втручання. Стіки пульта напряму задають цільові кутові швидкості обертання навколо осей крену, тангажу та рискання (градуси за секунду). Працює виключно внутрішній контур демпфування кутових швидкостей (Rate PID) за даними гіроскопа. За відсутності впливу на стіки апарат зберігає поточний кутовий нахил, не намагаючись повернутися до горизонту.
   - `Stabilize` (автогоризонт): над контуром кутових швидкостей замикається зовнішній контур кутового положення (Attitude PID) за даними акселерометра та гіроскопа. Відхилення стіка задає цільовий кут нахилу (наприклад, до ±35°), а нейтральне положення стіка автоматично повертає апарат у горизонтальне положення. Вертикальний канал (тяга моторів) залишається під прямим пропорційним контролем ручки газу пілота.
   - `AltHold` (утримання висоти): над контуром стабілізації горизонту активується вертикальний регулятор положення (Z-axis PID). Висота та вертикальна швидкість оцінюються за даними барометра, вертикального каналу акселерометра або далекоміра (LiDAR / ультразвук). Нейтральне положення ручки газу (центральна мертва зона 40–60%) означає нульову вертикальну швидкість (утримання поточної висоти), а відхилення вгору або вниз задає швидкість підйому чи спуску (наприклад, ±2.5 м/с). Канали крену й тангажу залишаються в режимі `Stabilize`.

2. **Навігаційні та позиційні режими (Position / Velocity Control):**
   - `PosHold / Loiter` (утримання позиції): над контурами стабілізації горизонту та утримання висоти активуються горизонтальні регулятори швидкості та просторових координат (XY-axis PID). Для роботи режиму критично необхідні достовірні дані глобальної супутникової навігації (GNSS) або оптичного потоку (Optical Flow) у поєднанні з магнітометром та інерціальною системою. Нейтральні стіки переводять дрон у режим зависання в точці з активним протистоянням вітровому зносу; відхилення стіків транслюються у вектори горизонтальної швидкості польоту (м/с).
   - `Guided` (керований / напівавтономний): апарат утримує просторову орієнтацію та висоту самостійно, але цільові точки (Setpoints) або просторові вектори швидкостей надходять у реальному часі через зовнішні інтерфейси зв'язку — від наземної станції керування (GCS) або бортового супровідного комп'ютера (Companion Computer) за протоколом MAVLink.

3. **Автономні та аварійні режими (Autonomous / Failsafe):**
   - `Auto` (автономна місія): повний автономний політ за попередньо завантаженим у пам'ять польотного контролера списком навігаційних точок (Waypoints). Автопілот сам розраховує траєкторію, кутові швидкості, швидкість польоту та висоту, керуючи корисним навантаженням і виконуючи просторові маневри.
   - `RTL / RTH` (повернення додому, Return-To-Launch / Return-To-Home): автономна рятувальна процедура. Апарат піднімається на безпечну заздалегідь налаштовану висоту повернення (`RTL_ALT`, наприклад 30 метрів), розвертається за курсом до збереженої точки зльоту (`Home Position`), летить по прямій лінії або записаному зворотному треку, зависає над точкою ініціалізації та переходить у режим посадки.
   - `Land` (автоматична посадка): контрольований вертикальний спуск із фіксованою швидкістю (наприклад, 0.7 м/с біля землі). Спеціальний алгоритм детекції торкання землі (Land Detector) фіксує зупинку зниження за показниками барометра/акселерометра разом із падінням споживаного струму та автоматично знеструмлює мотори (Disarm).
   - `Emergency Land / Terminate` (аварійна посадка або відсічка): примусове зниження при відмові сенсорів навігації або аварійне вимкнення силової установки при катастрофічних руйнуваннях.

![Граф станів автомата польотних режимів з умовами-охоронцями та деградацією](/root/course/embedded/avtomat-rezhymiv/img/flight-mode-fsm-graph.svg)
*Граф станів польотного автомата: горизонтальна ієрархія від сирих ручних режимів до автономних місій та аварійних процедур із виділеними переходами деградації*

З графа станів видно ключову закономірність: будь-який рух зліва направо (від ручних режимів до позиційних та автономних) підвищує вимоги до працездатності сенсорного стека і накладає суворі обмеження на можливість здійснення переходу.

## Умови-охоронці: математичний бар'єр перед зміною стану

Перехід між станами скінченного автомата не може відбуватися лише за фактом отримання сигналу зміни положення тумблера чи отримання мережевого пакету. Між подією запиту (Event) та безпосередньою зміною стану стоїть логічний предикат — **умова-охоронець** (англ. *Guard Condition*).

Умова-охоронець — це детермінована функція без побічних ефектів, яка аналізує поточний вектор стану системи (телеметрію, стан сенсорів, оцінки фільтра Калмана, наявність місії) і повертає булеве значення: `true`, якщо перехід безпечний і допустимий, або `false`, якщо умови не виконані.

```
                    ┌─────────────────────────┐
                    │  Поточний стан: AltHold │
                    └────────────┬────────────┘
                                 │
                 Подія: Запит переходу в PosHold
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Умова-охоронець guard() │
                    └────────────┬────────────┘
                                 │
               ┌─────────────────┴─────────────────┐
               │                                   │
      Умова виконана (true)              Умова провалена (false)
               │                                   │
               ▼                                   ▼
┌─────────────────────────────┐     ┌─────────────────────────────┐
│  Новий стан: PosHold        │     │  Збереження стану: AltHold  │
│  Атомарний запуск XY-PID    │     │  Генерація MAV_RESULT_DENIED│
└─────────────────────────────┘     └─────────────────────────────┘
```

Розглянемо параметричні критерії основних умов-охоронців, які застосовуються у промислових автопілотах (зокрема ArduPilot та PX4).

### 1. Охоронець переходу в PosHold / Loiter

Для активації утримання координат автопілот повинен гарантувати, що контур позиційного регулювання володіє достовірною абсолютною оцінкою положення у тривимірному просторі. Охоронець перевіряє такі умови:

- **Фіксація супутникового сигналу (GNSS Fix):** статус супутникового приймача повинен бути не нижчим за `3D Fix` (або `RTK Fixed/Float` для високоточних систем). Кількість захоплених супутників повинна задовольняти умові:

```
N_satellites ≥ 6
```

- **Геометричний фактор зниження точності (HDOP / VDOP):** горизонтальний фактор розмиття точності взаємного розташування супутників повинен бути в межах норми. При високому значенні HDOP навіть за наявності багатьох супутників похибка обчислення координат може сягати десятків метрів:

```
HDOP < 1.5
VDOP < 2.0
```

- **Сходження оцінок розширеного фільтра Калмана (EKF Innovations):** формальної наявності GPS-фіксу недостатньо — сам модуль GNSS може видавати зашумлені або запізнілі дані під час міських каньйонів чи супутникового дрейфу. Фільтр Калмана EKF обчислює нев'язку (інновацію) між інерціальним інтегруванням акселерометра та вимірами супутника. Математично нормалізований квадрат інновацій (Normalized Innovation Squared, NIS) визначається як:

```
NIS = y · S⁻¹ · y
```

де `y` — вектор нев'язки між вимірами GNSS та прогнозом моделі, а `S` — коваріаційна матриця інновації. Охоронець перевіряє, щоб нормалізовані інновації швидкості та положення перебували в допустимому гейті:

```
EKF_innov_pos_norm < 0.3
EKF_innov_vel_norm < 0.5
```

Якщо інновація перевищує 1.0, фільтр вважає виміри взаємно суперечливими (EKF Variance Glitch), і охоронець безумовно блокує перехід у `PosHold`.

- **Достовірність магнітометра (Compass Heading Healthy):** без знання точного кута курсу (Yaw) автопілот не здатний перетворити вектор зміщення в системі координат Північ-Схід (NED) у внутрішню систему координат апарата (Body Frame). Розбіжність між оцінкою компаса та гіроскопа повинна бути менше порогового значення (зазвичай < 15°).

### 2. Охоронець переходу в Auto

Автономний режим вимагає виконання всіх охоронців позиційного режиму (`PosHold`), а також додаткової перевірки стану місії:

- **Кількість точок місії:** навігаційний буфер повинен містити валідну польотну програму:

```
mission_items_count > 0
```

- **Контрольна сума та валідність плану:** список точок повинен бути верифікований за CRC, містити коректні висоти та досяжні координати в межах дозволеного радіуса польотів.
- **Фіксація точки повернення (Home Position Set):** точка зльоту мусить бути коректно зафіксована в оперативній пам'яті автопілота до переходу в автономний рух, щоб апарат мав можливість виконати аварійне повернення.

### 3. Охоронець переходу в Guided

- **Наявність живого джерела цілевказівок:** вік останнього отриманого пакету MAVLink з цільовою позицією (`SET_POSITION_TARGET_GLOBAL_INT` або `SET_POSITION_TARGET_LOCAL_NED`) або серцебиттям від бортового супровідного комп'ютера не повинен перевищувати тайм-аут:

```
t_now - t_last_guided_heartbeat < 1.0 s
```

- **EKF Status:** повна валідність просторових оцінок положення та швидкості.

### 4. Охоронець переходу в RTL

- **Наявність зафіксованої точки Home:** якщо точка старту не була зафіксована через відсутність GPS перед зльотом у ручному режимі, перехід у RTL неможливий (у цьому випадку охоронець відхиляє запит і перенаправляє автопілот у режим `Land`).
- **Стійкість навігації:** наявність робочого горизонтального оцінювача положення.

### Протокол поведінки при відхиленні переходу

Якщо оператор або автоматика надсилає команду зміни режиму, але відповідна умова-охоронець повертає `false`:

1. **Атомарність відмови:** поточний режим залишається незмінним. Не відбувається жодного переривання поточної генерації керуючих сигналів на виконавчі механізми (ESC / сервоприводи).
2. **MAVLink-квитування:** на команду `COMMAND_LONG (MAV_CMD_DO_SET_MODE)` станції повертається пакет `COMMAND_ACK` із кодом результату `MAV_RESULT_DENIED` або `MAV_RESULT_FAILED`.
3. **Текстова діагностика:** у канал телеметрії негайно відправляється високопріоритетне інформаційне повідомлення `STATUSTEXT` із зазначенням точної причини блокування, наприклад:
   - `Mode change failed: PosHold requires 3D Fix & HDOP < 1.5`
   - `Mode change failed: Auto requires loaded mission`
   - `Mode change failed: RTL requires Home position`

## Заборонені та неприпустимі переходи

Окрім перевірки наявності сенсорних даних, автомат польотних режимів повинен гарантувати захист від несумісних динамічних стрибків та людських помилок у критичні фази польоту.

```
       ┌──────────────────────────────┐
       │     Заборонений перехід      │
       │    Land ───► Manual (Acro)   │
       │  (при спущеному стіку газу)  │
       └──────────────┬───────────────┘
                      │
                      ▼
     Стрибок сигналу тяги PWM: 48% ──► 0%
                      │
                      ▼
      Миттєва втрата підйомної сили,
     перекидання та некероване падіння!
```

### Динамічний стрибок газу (Throttle Jump Disaster)

У режимах `AltHold`, `PosHold`, `Auto` або `Land` керування вертикальною тягою здійснюється автоматичним Z-регулятором. Для утримання сталої висоти або контрольованого спуску регулятор підтримує шпаруватість сигналів двигунів, близьку до точки висіння (наприклад, 45–55% тяги).

При цьому положення фізичного стіка газу на пульті оператора може перебувати в довільній точці: наприклад, під час автоматичної посадки (`Land`) пілоти часто за звичкою скидають ручку газу в крайнє нижнє положення (0%).

Якщо в цей момент оператор помилково або навмисно перемкне тумблер у режим прямого керування `Manual / Acro`, де вихідна тяга моторів жорстко прив'язана до положення стіка, станеться наступне:

1. Z-регулятор миттєво вимикається.
2. Значення тяги на моторах стрибкоподібно падає з 48% до 0% за 2–4 мілісекунди (один цикл розрахунку контуру).
3. Пропелери втрачають оберти, дрон втрачає стабілізуючий момент, перекидається і розбивається об землю за частки секунди.

Аналогічно, якщо стік перебував у положенні 100%, перехід у `Manual` викликає вибуховий стрибок тяги, який може вивести апарат на закритичні швидкості або спалити силові ключі регуляторів швидкості (ESC).

### Захисні інтерлоки: узгодження заслінки газу (Throttle Interlock)

Щоб унеможливити подібний сценарій, у FSM закладається механізм блокування переходу за рівнем газу (**Throttle Matching Guard**):

- Перехід з будь-якого режиму з автоматичним утриманням висоти (`AltHold`, `PosHold`, `Auto`, `Guided`, `Land`) у режим прямого керування тягою (`Manual`, `Stabilize`, `Acro`) блокується доти, доки фізичне положення стіка газу на пульті не потрапить у зону узгодження з поточним віртуальним дроселем:

```
|Stick_Throttle - Current_Auto_Throttle| ≤ Throttle_Deadband
```

де `Throttle_Deadband` зазвичай обирається в діапазоні 0.10–0.15 (10–15% шкали).

- Поки оператор не зведе ручку у відповідну позицію, автопілот ігнорує запит тумблера, видає звуковий сигнал зумера, сповіщення на екран наземної станції і залишається в поточному автоматичному стабілізованому режимі.
- Додатково в системі реалізується алгоритм обмеження швидкості наростання сигналу тяги (**Throttle Slew Rate Limiter**), який усуває східчасті стрибки навіть після проходження охоронця.

### Блокування випадкового роззброєння в польоті (In-Flight Disarm Prevention)

У стані польоту перехід автомата з підсистеми `Armed` у `Disarmed` (повна зупинка генерації сигналів керування моторами) суворо заборонений:

- Будь-які комбінації стіків роззброєння (наприклад, стік газу вниз і рудер ліворуч) ігноруються FSM, якщо детектор польоту (`In-Air Detector`) сигналізує, що апарат перебуває у повітрі.
- Детектор польоту аналізує інтегральну динаміку: перевищення висоти над точкою старту (> 1.5 м), швидкість обертання двигунів вище холостого ходу та наявність ненульових прискорень відриву.
- Єдиним винятком є виділений апаратний тумблер аварійної відсічки (**Emergency Kill Switch**), який функціонує в обхід софтового автомата польотних режимів на рівні апаратного таймера або мікроконтролера захисту введення-виведення (I/O Co-processor).

![Послідовність верифікації охоронців та захисту від заборонених стрибків](/root/course/embedded/avtomat-rezhymiv/img/guard-verification-and-throttle-lock.svg)
*Алгоритм перевірки: відхилення аварійних запитів, перевірка параметричних охоронців та блокування заслінки газу перед зміною стану*

## Детектор посадки (Land Detector) і завершення автономного циклу

Окремою критичною фазою роботи автомата є фінал польоту в режимах `Land` та `RTL`. Автопілот не може просто вимкнути мотори на заданій висоті за барометром, оскільки зміна атмосферного тиску під час польоту або завихрення повітряного потоку під пропелерами біля самої землі (ефект екрана, Ground Effect) створюють похибку висоти у 1–3 метри.

Вимкнення моторів на висоті 1.5 метра призведе до жорсткого удару об землю і пошкодження рами. Навпаки, спроба продовжувати спуск після фактичного торкання землі призведе до того, що регулятор крену й тангажу спробує вирівняти дрон, опершись пропелерами об ґрунт, накопичить інтегральну помилку I-терма і перекине апарат.

Щоб вийти з цієї дилеми, FSM містить внутрішній трирівневий детектор посадки:

1. **Фаза зниження (Descent):** вертикальна швидкість стабілізується на рівні `LAND_SPEED` (0.5–0.7 м/с).
2. **Фаза контакту з поверхнею (Ground Contact):**
   - Вертикальна швидкість наближається до нуля: `|Vz| < 0.2 м/с`.
   - Вихід Z-регулятора тяги падає до мінімального порогу `LAND_THR_MIN` (15–20% від тяги висіння), оскільки апарат більше не просідає.
   - Дисперсія акселерометра по осі Z падає нижче порогу вібрацій.
   - Стан фіксується таймером витримки (Debounce Timer, тривалість 1.0 с).
3. **Фаза остаточної посадки (Landed):**
   - Усі три умови утримуються стабільно протягом 1.5–2.0 секунд.
   - Автомат переводить двигуни на мінімальний холостий хід (Spin When Armed).
   - FSM відправляє подію `EVENT_DISARM`, мотори повністю зупиняються, а поточний режим перемикається в безпечний стан очікування на землі.

## Пріоритети аварійних режимів: витіснення та каскадна деградація

Коли на борту виникає аварійна ситуація (розряджання батареї нижче критичного рівня, втрата зв'язку з пультом, збій супутникової навігації під час виконання автономної місії), рішення про вибір режиму більше не може залежати від оператора чи поточної місії. FSM повинен реалізувати механізм **пріоритетного витіснення** (англ. *Failsafe Preemption*).

### Сходинка пріоритетів (Preemption Hierarchy)

Усі джерела запитів на зміну режиму поділяються на 5 рівнів пріоритету:

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ Рівень 5 (Абсолютний): Hardware Kill / Emergency Terminate                   ║
║ Знеструмлення двигунів, відстріл піропатрона парашута.                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Рівень 4 (Критичний Failsafe): Battery Stage 2 / Critical EKF Crash           ║
║ Примусовий Land або керований спуск. Блокує всі команди оператора та місію.   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Рівень 3 (Навігаційний Failsafe): RC Loss / GCS Loss / Geofence Breach        ║
║ Активація RTL або повернення по треку. Може бути перехоплений пілотом.       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Рівень 2 (Ручне перехоплення пілота): Pilot Stick Override                   ║
║ Рух стіків у Stabilize негайно скасовує Auto/Guided (пріоритет людини).      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Рівень 1 (Штатні запити): RC Switch / MAVLink Mode Change                     ║
║ Звичайне перемикання оператором, вимагає виконання всіх охоронців.            ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

Якщо активується умова вищого рівня, автомат польотних режимів негайно призупиняє поточний режим і переводить апарат у відповідний захисний стан:

1. **Критичне розряджання акумулятора (Battery Failsafe Stage 2):** якщо напруга на комірці падає нижче 3.3 В під навантаженням або розрахований залишковий заряд падає нижче 10%, FSM негайно витісняє поточний режим `Auto` чи `PosHold` і переходить у `Land`. Будь-які спроби перемкнути режим назад в `Auto` блокуються.
2. **Втрата сигналу радіокерування (RC Failsafe):** якщо приймач не отримує валідних пакетів довше порогового часу (наприклад, 1.5 секунди), активується Failsafe рівня 3 (`RTL`). Якщо водночас відсутній GPS-фікс, FSM каскадно переводить дрон у режим `Land` або утримання висоти зі спуском.

![Сходинка пріоритетів і витіснення аварійних режимів польотного автомата](/root/course/embedded/avtomat-rezhymiv/img/failsafe-preemption-ladder.svg)
*Сходинка арбітражу польотного автомата: вищі рівні безумовно блокують виконання нижчих запитів*

### Каскадна деградація (Graceful Degradation)

Що відбувається, коли відмова сенсорів стається прямо під час польоту у високорівневому режимі?

Припустимо, апарат виконує місію в режимі `Auto` або завис у точці в режимі `PosHold`. Раптово супутниковий приймач зазнає радіозавад: кількість супутників падає до 3, інновації EKF виходять за межі допустимого. Залишатися в `Auto` чи `PosHold` неможливо — регулятор положення позбавлений зворотного зв'язку. Переходити в `Manual` смертельно небезпечно.

FSM запускає алгоритм **керованої каскадної деградації**:

```
[Політ у режимі AUTO / POSHOLD]
             │
             ▼ (Втрата GNSS Fix / Збій EKF)
[Деградація до режиму ALT_HOLD]
- Вимикаються XY-PID регулятори
- Залишається активним Z-баро регулятор
- Повна стабілізація кутів горизонту
- Звуковий сигнал тривоги та сповіщення GCS
             │
             ▼ (Відмова барометра / LiDAR)
[Деградація до режиму STABILIZE]
- Перехід на ручне керування тягою
- Збереження автогоризонту за IMU
             │
             ▼ (Повна відмова IMU)
[Аварійне розкриття парашута / Апаратна відсічка]
```

Автомат не панікує і не скидає керування в нуль, а покроково спускається на той рівень ієрархії, сенсорне забезпечення якого залишається повністю працездатним.

## Повна реалізація відмовостійкого автомата польотних режимів

Нижче наведено промисловий варіант реалізації відмовостійкого автомата польотних режимів. Код містить повну структуру перевірки сенсорного стану, логіку умов-охоронців, алгоритм детекції посадки (Land Detector), механізм пріоритетного витіснення аварійними режимами та захист від стрибків газу.

:::tabs
```c
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

/* Перелік польотних режимів автопілота */
typedef enum {
    FLIGHT_MODE_MANUAL = 0,
    FLIGHT_MODE_STABILIZE,
    FLIGHT_MODE_ALT_HOLD,
    FLIGHT_MODE_POS_HOLD,
    FLIGHT_MODE_AUTO,
    FLIGHT_MODE_GUIDED,
    FLIGHT_MODE_RTL,
    FLIGHT_MODE_LAND,
    FLIGHT_MODE_EMERGENCY_LAND,
    FLIGHT_MODE_TERMINATE,
    FLIGHT_MODE_COUNT
} FlightMode;

/* Коди результатів запиту на зміну режиму (MAVLink сумісні) */
typedef enum {
    TRANSITION_OK = 0,
    TRANSITION_DENIED_NO_GPS,
    TRANSITION_DENIED_BAD_HDOP,
    TRANSITION_DENIED_EKF_UNHEALTHY,
    TRANSITION_DENIED_NO_MISSION,
    TRANSITION_DENIED_NO_HOME,
    TRANSITION_DENIED_THROTTLE_MISMATCH,
    TRANSITION_DENIED_FAILSAFE_ACTIVE,
    TRANSITION_DENIED_INVALID_MODE
} TransitionResult;

/* Структура знімка стану сенсорів та телеметрії */
typedef struct {
    bool armed;
    bool in_air;
    uint8_t gps_fix_type;      /* 0: No Fix, 2: 2D, 3: 3D Fix */
    uint8_t gps_num_sats;
    float gps_hdop;
    float gps_vdop;
    bool ekf_pos_horiz_valid;
    bool ekf_pos_vert_valid;
    float ekf_innov_pos;
    bool compass_healthy;
    uint16_t mission_item_count;
    bool home_position_set;
    float current_throttle;    /* 0.0f - 1.0f поточний вихід регулятора */
    float stick_throttle;      /* 0.0f - 1.0f положення ручки на пульті */
    float vertical_velocity;   /* м/с, додатна вгору */
    bool rc_link_lost;
    bool gcs_link_lost;
    uint8_t battery_failsafe_stage; /* 0: OK, 1: Low, 2: Critical */
    bool hardware_kill_switch;
} TelemetrySnapshot;

/* Стан детектора посадки */
typedef struct {
    bool ground_contact;
    bool landed;
    uint32_t contact_start_ms;
} LandDetector;

/* Стан автомата режимів */
typedef struct {
    FlightMode current_mode;
    FlightMode previous_mode;
    uint32_t last_transition_ms;
    bool failsafe_locked;
    LandDetector land_detector;
} FlightModeFSM;

/* Ініціалізація автомата польотних режимів */
void fsm_init(FlightModeFSM* fsm) {
    if (!fsm) return;
    fsm->current_mode = FLIGHT_MODE_STABILIZE;
    fsm->previous_mode = FLIGHT_MODE_STABILIZE;
    fsm->last_transition_ms = 0;
    fsm->failsafe_locked = false;
    fsm->land_detector.ground_contact = false;
    fsm->land_detector.landed = false;
    fsm->land_detector.contact_start_ms = 0;
}

/* Умова-охоронець для режиму PosHold / Loiter */
static TransitionResult guard_pos_hold(const TelemetrySnapshot* t) {
    if (t->gps_fix_type < 3 || t->gps_num_sats < 6) {
        return TRANSITION_DENIED_NO_GPS;
    }
    if (t->gps_hdop > 1.5f || t->gps_vdop > 2.0f) {
        return TRANSITION_DENIED_BAD_HDOP;
    }
    if (!t->ekf_pos_horiz_valid || !t->compass_healthy || t->ekf_innov_pos > 0.3f) {
        return TRANSITION_DENIED_EKF_UNHEALTHY;
    }
    return TRANSITION_OK;
}

/* Умова-охоронець для режиму Auto */
static TransitionResult guard_auto(const TelemetrySnapshot* t) {
    TransitionResult pos_res = guard_pos_hold(t);
    if (pos_res != TRANSITION_OK) {
        return pos_res;
    }
    if (t->mission_item_count == 0) {
        return TRANSITION_DENIED_NO_MISSION;
    }
    if (!t->home_position_set) {
        return TRANSITION_DENIED_NO_HOME;
    }
    return TRANSITION_OK;
}

/* Умова-охоронець для режиму RTL */
static TransitionResult guard_rtl(const TelemetrySnapshot* t) {
    if (!t->home_position_set) {
        return TRANSITION_DENIED_NO_HOME;
    }
    if (!t->ekf_pos_horiz_valid && !t->ekf_pos_vert_valid) {
        return TRANSITION_DENIED_EKF_UNHEALTHY;
    }
    return TRANSITION_OK;
}

/* Захист від стрибка газу при переході з автоматичних режимів у ручні */
static bool check_throttle_matching(FlightMode current, FlightMode target, const TelemetrySnapshot* t) {
    bool is_current_auto_thrust = (current == FLIGHT_MODE_ALT_HOLD ||
                                   current == FLIGHT_MODE_POS_HOLD ||
                                   current == FLIGHT_MODE_AUTO ||
                                   current == FLIGHT_MODE_GUIDED ||
                                   current == FLIGHT_MODE_LAND ||
                                   current == FLIGHT_MODE_RTL);

    bool is_target_manual_thrust = (target == FLIGHT_MODE_MANUAL ||
                                    target == FLIGHT_MODE_STABILIZE);

    if (t->in_air && is_current_auto_thrust && is_target_manual_thrust) {
        float diff = t->stick_throttle - t->current_throttle;
        if (diff < 0.0f) diff = -diff;
        /* Дозволений поріг неспівпадіння: 15% */
        if (diff > 0.15f) {
            return false;
        }
    }
    return true;
}

/* Детектор посадки: виявлення контакту з ґрунтом */
static void update_land_detector(FlightModeFSM* fsm, const TelemetrySnapshot* t, uint32_t now_ms) {
    if (!t->in_air || (fsm->current_mode != FLIGHT_MODE_LAND && fsm->current_mode != FLIGHT_MODE_EMERGENCY_LAND)) {
        fsm->land_detector.ground_contact = false;
        fsm->land_detector.landed = false;
        fsm->land_detector.contact_start_ms = 0;
        return;
    }

    float vz_abs = t->vertical_velocity < 0.0f ? -t->vertical_velocity : t->vertical_velocity;
    bool vz_stopped = vz_abs < 0.25f;
    bool throttle_min = t->current_throttle < 0.20f;

    if (vz_stopped && throttle_min) {
        if (!fsm->land_detector.ground_contact) {
            fsm->land_detector.ground_contact = true;
            fsm->land_detector.contact_start_ms = now_ms;
        } else if (now_ms - fsm->land_detector.contact_start_ms > 1500) {
            fsm->land_detector.landed = true;
        }
    } else {
        fsm->land_detector.ground_contact = false;
        fsm->land_detector.contact_start_ms = 0;
    }
}

/* Арбітраж аварійних станів: перевірка умов вищого пріоритету */
static bool check_failsafe_preemption(FlightModeFSM* fsm, const TelemetrySnapshot* t, uint32_t now_ms) {
    /* Рівень 5: Hardware Kill Switch */
    if (t->hardware_kill_switch) {
        fsm->previous_mode = fsm->current_mode;
        fsm->current_mode = FLIGHT_MODE_TERMINATE;
        fsm->failsafe_locked = true;
        fsm->last_transition_ms = now_ms;
        return true;
    }

    /* Рівень 4: Критичний Failsafe батареї або повний крах навігації під час посадки */
    if (t->battery_failsafe_stage >= 2 && fsm->current_mode != FLIGHT_MODE_EMERGENCY_LAND) {
        fsm->previous_mode = fsm->current_mode;
        fsm->current_mode = FLIGHT_MODE_EMERGENCY_LAND;
        fsm->failsafe_locked = true;
        fsm->last_transition_ms = now_ms;
        return true;
    }

    /* Рівень 3: Втрата зв'язку RC або геозона -> RTL */
    if (t->rc_link_lost && t->in_air) {
        if (fsm->current_mode != FLIGHT_MODE_RTL && fsm->current_mode != FLIGHT_MODE_LAND &&
            fsm->current_mode != FLIGHT_MODE_EMERGENCY_LAND) {
            if (guard_rtl(t) == TRANSITION_OK) {
                fsm->previous_mode = fsm->current_mode;
                fsm->current_mode = FLIGHT_MODE_RTL;
                fsm->last_transition_ms = now_ms;
                return true;
            } else {
                /* Каскадна деградація: немає умов для RTL -> негайна посадка Land */
                fsm->previous_mode = fsm->current_mode;
                fsm->current_mode = FLIGHT_MODE_LAND;
                fsm->last_transition_ms = now_ms;
                return true;
            }
        }
    }
    return false;
}

/* Запит на штатну зміну режиму від оператора чи GCS */
TransitionResult fsm_request_mode(FlightModeFSM* fsm, FlightMode target, const TelemetrySnapshot* t, uint32_t now_ms) {
    if (!fsm || !t) return TRANSITION_DENIED_INVALID_MODE;

    /* Якщо активне блокування критичного Failsafe — штатні запити відхиляються */
    if (fsm->failsafe_locked && target != FLIGHT_MODE_STABILIZE) {
        return TRANSITION_DENIED_FAILSAFE_ACTIVE;
    }

    if (target == fsm->current_mode) {
        return TRANSITION_OK;
    }

    /* 1. Перевірка заслінки газу (захист від стрибка тяги) */
    if (!check_throttle_matching(fsm->current_mode, target, t)) {
        return TRANSITION_DENIED_THROTTLE_MISMATCH;
    }

    /* 2. Перевірка параметричних охоронців цільового режиму */
    TransitionResult res = TRANSITION_OK;
    switch (target) {
        case FLIGHT_MODE_MANUAL:
        case FLIGHT_MODE_STABILIZE:
            /* Базові ручні режими не вимагають зовнішніх сенсорів навігації */
            res = TRANSITION_OK;
            break;

        case FLIGHT_MODE_ALT_HOLD:
            if (!t->ekf_pos_vert_valid) {
                res = TRANSITION_DENIED_EKF_UNHEALTHY;
            }
            break;

        case FLIGHT_MODE_POS_HOLD:
        case FLIGHT_MODE_GUIDED:
            res = guard_pos_hold(t);
            break;

        case FLIGHT_MODE_AUTO:
            res = guard_auto(t);
            break;

        case FLIGHT_MODE_RTL:
            res = guard_rtl(t);
            break;

        case FLIGHT_MODE_LAND:
        case FLIGHT_MODE_EMERGENCY_LAND:
            res = TRANSITION_OK;
            break;

        default:
            res = TRANSITION_DENIED_INVALID_MODE;
            break;
    }

    if (res == TRANSITION_OK) {
        fsm->previous_mode = fsm->current_mode;
        fsm->current_mode = target;
        fsm->last_transition_ms = now_ms;
        fsm->failsafe_locked = false; /* Скидання блокування при свідомому виборі пілота */
    }

    return res;
}

/* Головний періодичний крок автомата (викликається з частотою 50-100 Гц) */
void fsm_update(FlightModeFSM* fsm, const TelemetrySnapshot* t, uint32_t now_ms) {
    if (!fsm || !t) return;

    /* 1. Оновлення детектора посадки */
    update_land_detector(fsm, t, now_ms);

    /* 2. Обробка аварійних витіснень */
    if (check_failsafe_preemption(fsm, t, now_ms)) {
        return;
    }

    /* 3. Каскадна деградація сенсорів у польоті */
    if (t->in_air) {
        if (fsm->current_mode == FLIGHT_MODE_POS_HOLD || fsm->current_mode == FLIGHT_MODE_AUTO) {
            if (guard_pos_hold(t) != TRANSITION_OK) {
                /* Деградація: PosHold/Auto -> AltHold */
                fsm->previous_mode = fsm->current_mode;
                fsm->current_mode = FLIGHT_MODE_ALT_HOLD;
                fsm->last_transition_ms = now_ms;
            }
        }

        if (fsm->current_mode == FLIGHT_MODE_ALT_HOLD) {
            if (!t->ekf_pos_vert_valid) {
                /* Деградація: AltHold -> Stabilize */
                fsm->previous_mode = fsm->current_mode;
                fsm->current_mode = FLIGHT_MODE_STABILIZE;
                fsm->last_transition_ms = now_ms;
            }
        }
    }
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <string_view>
#include <optional>
#include <expected>

enum class FlightMode : uint8_t {
    Manual = 0,
    Stabilize,
    AltHold,
    PosHold,
    Auto,
    Guided,
    RTL,
    Land,
    EmergencyLand,
    Terminate
};

enum class TransitionError : uint8_t {
    NoGpsFix,
    BadHdop,
    EkfUnhealthy,
    NoMissionLoaded,
    NoHomePosition,
    ThrottleMismatch,
    FailsafeActive,
    InvalidMode
};

struct TelemetrySnapshot {
    bool armed{false};
    bool in_air{false};
    uint8_t gps_fix_type{0};      // 3: 3D Fix
    uint8_t gps_num_sats{0};
    float gps_hdop{99.0f};
    float gps_vdop{99.0f};
    bool ekf_pos_horiz_valid{false};
    bool ekf_pos_vert_valid{false};
    float ekf_innov_pos{1.0f};
    bool compass_healthy{false};
    uint16_t mission_item_count{0};
    bool home_position_set{false};
    float current_throttle{0.0f}; // 0.0f - 1.0f
    float stick_throttle{0.0f};   // 0.0f - 1.0f
    float vertical_velocity{0.0f}; // м/с
    bool rc_link_lost{false};
    bool gcs_link_lost{false};
    uint8_t battery_failsafe_stage{0}; // 0: OK, 1: Warning, 2: Critical
    bool hardware_kill_switch{false};
};

struct LandDetectorState {
    bool ground_contact{false};
    bool landed{false};
    uint32_t contact_start_ms{0};
};

class FlightModeFSM {
public:
    FlightModeFSM() = default;

    [[nodiscard]] FlightMode current_mode() const noexcept { return current_mode_; }
    [[nodiscard]] FlightMode previous_mode() const noexcept { return previous_mode_; }
    [[nodiscard]] bool is_failsafe_locked() const noexcept { return failsafe_locked_; }
    [[nodiscard]] bool is_landed() const noexcept { return land_detector_.landed; }

    // Запит на перемикання режиму зі строгою перевіркою охоронців
    std::expected<void, TransitionError> request_mode(FlightMode target, const TelemetrySnapshot& t, uint32_t now_ms) noexcept {
        if (failsafe_locked_ && target != FlightMode::Stabilize) {
            return std::unexpected(TransitionError::FailsafeActive);
        }

        if (target == current_mode_) {
            return {};
        }

        if (!check_throttle_matching(current_mode_, target, t)) {
            return std::unexpected(TransitionError::ThrottleMismatch);
        }

        auto guard_result = verify_guard(target, t);
        if (!guard_result.has_value()) {
            return std::unexpected(guard_result.error());
        }

        perform_transition(target, now_ms);
        failsafe_locked_ = false;
        return {};
    }

    // Періодичне оновлення логіки детектора посадки, арбітражу та деградації (50-100 Гц)
    void update(const TelemetrySnapshot& t, uint32_t now_ms) noexcept {
        update_land_detector(t, now_ms);

        if (handle_preemption(t, now_ms)) {
            return;
        }

        if (t.in_air) {
            handle_graceful_degradation(t, now_ms);
        }
    }

    static constexpr std::string_view mode_name(FlightMode mode) noexcept {
        switch (mode) {
            case FlightMode::Manual:        return "MANUAL";
            case FlightMode::Stabilize:     return "STABILIZE";
            case FlightMode::AltHold:       return "ALT_HOLD";
            case FlightMode::PosHold:       return "POS_HOLD";
            case FlightMode::Auto:          return "AUTO";
            case FlightMode::Guided:        return "GUIDED";
            case FlightMode::RTL:           return "RTL";
            case FlightMode::Land:          return "LAND";
            case FlightMode::EmergencyLand: return "EMERGENCY_LAND";
            case FlightMode::Terminate:     return "TERMINATE";
        }
        return "UNKNOWN";
    }

private:
    FlightMode current_mode_{FlightMode::Stabilize};
    FlightMode previous_mode_{FlightMode::Stabilize};
    uint32_t last_transition_ms_{0};
    bool failsafe_locked_{false};
    LandDetectorState land_detector_{};

    void perform_transition(FlightMode new_mode, uint32_t now_ms) noexcept {
        previous_mode_ = current_mode_;
        current_mode_ = new_mode;
        last_transition_ms_ = now_ms;
    }

    [[nodiscard]] static std::expected<void, TransitionError> guard_pos_hold(const TelemetrySnapshot& t) noexcept {
        if (t.gps_fix_type < 3 || t.gps_num_sats < 6) {
            return std::unexpected(TransitionError::NoGpsFix);
        }
        if (t.gps_hdop > 1.5f || t.gps_vdop > 2.0f) {
            return std::unexpected(TransitionError::BadHdop);
        }
        if (!t.ekf_pos_horiz_valid || !t.compass_healthy || t.ekf_innov_pos > 0.3f) {
            return std::unexpected(TransitionError::EkfUnhealthy);
        }
        return {};
    }

    [[nodiscard]] static std::expected<void, TransitionError> guard_auto(const TelemetrySnapshot& t) noexcept {
        auto pos_guard = guard_pos_hold(t);
        if (!pos_guard.has_value()) {
            return pos_guard;
        }
        if (t.mission_item_count == 0) {
            return std::unexpected(TransitionError::NoMissionLoaded);
        }
        if (!t.home_position_set) {
            return std::unexpected(TransitionError::NoHomePosition);
        }
        return {};
    }

    [[nodiscard]] static std::expected<void, TransitionError> guard_rtl(const TelemetrySnapshot& t) noexcept {
        if (!t.home_position_set) {
            return std::unexpected(TransitionError::NoHomePosition);
        }
        if (!t.ekf_pos_horiz_valid && !t.ekf_pos_vert_valid) {
            return std::unexpected(TransitionError::EkfUnhealthy);
        }
        return {};
    }

    [[nodiscard]] std::expected<void, TransitionError> verify_guard(FlightMode target, const TelemetrySnapshot& t) const noexcept {
        switch (target) {
            case FlightMode::Manual:
            case FlightMode::Stabilize:
                return {};
            case FlightMode::AltHold:
                if (!t.ekf_pos_vert_valid) {
                    return std::unexpected(TransitionError::EkfUnhealthy);
                }
                return {};
            case FlightMode::PosHold:
            case FlightMode::Guided:
                return guard_pos_hold(t);
            case FlightMode::Auto:
                return guard_auto(t);
            case FlightMode::RTL:
                return guard_rtl(t);
            case FlightMode::Land:
            case FlightMode::EmergencyLand:
            case FlightMode::Terminate:
                return {};
        }
        return std::unexpected(TransitionError::InvalidMode);
    }

    [[nodiscard]] static bool check_throttle_matching(FlightMode current, FlightMode target, const TelemetrySnapshot& t) noexcept {
        const bool is_current_auto = (current == FlightMode::AltHold ||
                                      current == FlightMode::PosHold ||
                                      current == FlightMode::Auto ||
                                      current == FlightMode::Guided ||
                                      current == FlightMode::Land ||
                                      current == FlightMode::RTL);

        const bool is_target_manual = (target == FlightMode::Manual ||
                                       target == FlightMode::Stabilize);

        if (t.in_air && is_current_auto && is_target_manual) {
            const float diff = std::abs(t.stick_throttle - t.current_throttle);
            if (diff > 0.15f) {
                return false;
            }
        }
        return true;
    }

    void update_land_detector(const TelemetrySnapshot& t, uint32_t now_ms) noexcept {
        if (!t.in_air || (current_mode_ != FlightMode::Land && current_mode_ != FlightMode::EmergencyLand)) {
            land_detector_ = {};
            return;
        }

        const bool vz_stopped = std::abs(t.vertical_velocity) < 0.25f;
        const bool throttle_min = t.current_throttle < 0.20f;

        if (vz_stopped && throttle_min) {
            if (!land_detector_.ground_contact) {
                land_detector_.ground_contact = true;
                land_detector_.contact_start_ms = now_ms;
            } else if (now_ms - land_detector_.contact_start_ms > 1500) {
                land_detector_.landed = true;
            }
        } else {
            land_detector_.ground_contact = false;
            land_detector_.contact_start_ms = 0;
        }
    }

    bool handle_preemption(const TelemetrySnapshot& t, uint32_t now_ms) noexcept {
        if (t.hardware_kill_switch) {
            perform_transition(FlightMode::Terminate, now_ms);
            failsafe_locked_ = true;
            return true;
        }

        if (t.battery_failsafe_stage >= 2 && current_mode_ != FlightMode::EmergencyLand) {
            perform_transition(FlightMode::EmergencyLand, now_ms);
            failsafe_locked_ = true;
            return true;
        }

        if (t.rc_link_lost && t.in_air) {
            if (current_mode_ != FlightMode::RTL && current_mode_ != FlightMode::Land && current_mode_ != FlightMode::EmergencyLand) {
                if (guard_rtl(t).has_value()) {
                    perform_transition(FlightMode::RTL, now_ms);
                } else {
                    perform_transition(FlightMode::Land, now_ms);
                }
                return true;
            }
        }
        return false;
    }

    void handle_graceful_degradation(const TelemetrySnapshot& t, uint32_t now_ms) noexcept {
        if (current_mode_ == FlightMode::PosHold || current_mode_ == FlightMode::Auto) {
            if (!guard_pos_hold(t).has_value()) {
                perform_transition(FlightMode::AltHold, now_ms);
            }
        }

        if (current_mode_ == FlightMode::AltHold) {
            if (!t.ekf_pos_vert_valid) {
                perform_transition(FlightMode::Stabilize, now_ms);
            }
        }
    }
};
```
:::

## Зміна режимів без удару по регуляторах: безривковий перехід

Фіксація нового стану всередині скінченного автомата — це лише половина завдання. У момент, коли змінна стану перемикається, наприклад, з `Stabilize` на `AltHold`, внутрішні контролери системи не повинні викликати ривка виконавчих механізмів (англ. *Bumpless Transfer*).

Якщо в момент активації `AltHold` інтегральна складова PID-регулятора висоти дорівнюватиме нулю, вихідна тяга миттєво просяде до значення пропорційного члена, викликаючи просідання дрона на 1–2 метри. Щоб перехід відбувався плавно:

1. **Ініціалізація цільових уставок (Setpoint Latching):** у момент входу в `AltHold` цільова висота `Z_target` прирівнюється до поточного значення висоти `Z_current`, зафіксованого саме в мілісекунду перемикання. Аналогічно для `PosHold` цільові просторові координати `(X_target, Y_target)` фіксуються в момент зупинки стіків пілота.
2. **Передустановка інтегратора (Integrator Pre-loading):** інтегратор Z-каналу ініціалізується поточним значенням тяги висіння, що запобігає будь-яким розривам першої похідної керуючого сигналу.
3. Докладний математичний розбір синхронізації станів інтеграторів та фільтрів подано в темі [Перехід без ривка](root:embedded/perekhid-bez-ryvka).

## Правила проектування надійного польотного автомата

При створенні та тестуванні автомата режимів автономного засобу слід дотримуватися чотирьох інженерних заповідей:

1. **Жодного невизначеного стану:** переходи в FSM мають бути абсолютно вичерпними. Будь-яка невідома подія чи некоректний вхідний код повинні оброблятися дефолтною гілкою з поверненням у безпечний базовий режим (`Stabilize` або `AltHold`).
2. **Атомарність верифікації:** оцінка стану сенсорів, EKF та положення органів керування здійснюється до зміни внутрішнього покажчика стану. Неприпустимо частково ініціалізувати новий режим і лише потім з'ясовувати, що супутниковий сигнал втрачено.
3. **Пріоритет фізичної безпеки над планом місії:** програмний автомат ніколи не повинен блокувати аварійні протоколи порятунку заради продовження виконання завдань місії.
4. **Відсутність циклічного деренчання переходів (Hysteresis):** якщо якість сенсорів балансує на межі порогового значення (наприклад, `HDOP` коливається між 1.49 та 1.51), автомат повинен застосовувати часову затримку (Debouncing, наприклад 1–2 секунди стійкого стану) перед дозволом зворотного переходу, щоб виключити високочастотне перемикання режимів.
