# Місії й точки

<preknowlist>
- [Пакет MAVLink](root:sys-dron/mavlink-packet) — бітова упаковка заголовків, вирівнювання полів та підрахунок CRC-16 MCRF4XX.
- [Протокол місій MAVLink](root:sys-dron/mavlink-mission-protocol) — автомат транзакційного обміну списком точок між бортом і наземною станцією.
- [Елементи місії й команди](root:sys-dron/mavlink-mission-items) — структура дескриптора `MISSION_ITEM_INT` та різниця координатних фреймів.
- [Навігація за маршрутними точками](root:sys-dron/waypoint-route-sequencing) — геометрія досягнення точок, радіуси допуску й перемикання цілей.
- [Зниження й посадка](root:sys-dron/failsafe) — аварійні процедури та алгоритми безпечного повернення.
</preknowlist>

Комплекс моніторингу на базі безпілотного літака з розмахом крила 2.4 метра виконує 120-кілометровий політ уздовж лінії високовольтних електропередач у гірській місцевості. Польотне завдання налічує 160 послідовних просторових точок: автоматичний зліт, вихід на висоту 450 метрів над рівнем моря, політ складним зигзагоподібним маршрутом зі змінними кутами нахилу камерного підвісу, проходження контрольних оглядових орбіт навколо трансформаторних підстанцій та фінальний вихід на посадковий курс. Якщо під час передачі місії по радіоканалу автопілот втратить хоча б одну проміжну точку або інтерпретує висоту відносно точки старту замість відносної висоти над цифровою картою рельєфу (AGL), апарат на 40-му кілометрі вріжеться в гірський хребет на крейсерській швидкості 28 м/с. Якщо ж через збій у Flash-пам'яті масив точок буде пошкоджений наполовину, автопілот раптово перейде в некероване зависання або аварійну посадку в лісовому масиві.

Автономний політ спирається на жорсткий контракт: місія в автопілоті — це строго типізована двійкова програма, завантажена в енергонезалежну пам'ять перед стартом і керована бортовим кінцевим автоматом незалежно від наявності телеметрійного радіозв'язку.

## Анатомія місії: послідовний масив елементів

Польотна місія в автопілотах класів ArduPilot та PX4 зберігається у вигляді лінійного масиву структур фіксованого розміру. Кожен елемент цього масиву (англ. *Mission Item*) є неподільною навігаційною або допоміжною інструкцією. Уніфікований дескриптор повідомлення протоколу MAVLink `MISSION_ITEM_INT` (`#73`) містить 38 байтів корисного навантаження.

![Анатомія структури елемента місії](/root/sys/sys-dron/missions-waypoints/img/mission-item-structure.svg)
*Двійкова структура корисного навантаження MISSION_ITEM_INT (#73, 38 байтів): поділ на параметри плаваючої коми, цілочисельні координати degE7 та службові поля послідовності.*

### Поля структури дескриптора точки

Дескриптор інструкції місії містить дванадцять полів, кожне з яких відповідає за просторову прив'язку, геометрію або умови переходу:

1. `seq` (`uint16_t`, 2 байти) — порядковий номер інструкції в масиві, що починається з нуля (`0 .. N-1`). В автопілотах ArduPilot точка з індексом `seq = 0` зарезервована під координати домашньої позиції (Home Position) та висоту точки старту; безпосереднє виконання починається з індексу `seq = 1`. У прошивці PX4 нульовий елемент також часто зберігає географічну точку старту, відносно якої розраховуються локальні зміщення.
2. `command` (`uint16_t`, 2 байти) — числовий код команди з переліку `MAV_CMD`. Команди поділяються на дві принципові групи: навігаційні накази (NAV commands: рух у просторі, зліт, посадка, кружляння) та допоміжні дії (DO commands: зміна швидкості, керування підвісом камери, спрацьовування реле або скидання корисного навантаження).
3. `frame` (`uint8_t`, 1 байт) — координатна система прив'язки просторових координат (перелік `MAV_FRAME`).
4. `current` (`uint8_t`, 1 байт) — бітовий прапорець поточної активної цілі. Якщо значення дорівнює `1`, ця точка є актуальним просторовим орієнтиром, до якого спрямований контур керування. Усі інші точки мають значення `0`.
5. `autocontinue` (`uint8_t`, 1 байт) — прапорець автоматичного переходу. Якщо значення дорівнює `1`, навігатор автопілота після досягнення радіуса прийняття цієї точки автоматично інкрементує індекс поточної цілі (`seq + 1`) і переходить до наступного відрізка. Якщо значення дорівнює `0`, апарат після досягнення координат переходить у режим кружляння (Loiter/Hold) або зависання і чекає явної команди оператора з наземної станції.
6. `param1 .. param4` (`float32`, 4 × 4 = 16 байтів) — універсальні числові параметри, зміст яких повністю визначається полем `command`. Наприклад, для команди звичайної точки маршруту `param1` задає час затримки (Hold Time) у секундах, а `param2` — радіус прийняття точки (Acceptance Radius) у метрах.
7. `x` (`int32_t`, 4 байти) — географічна широта цільової точки (Latitude), масштабована на коефіцієнт `10⁷` (`degE7`), або локальна координата X (метри на північ) у локальній декартовій системі NED.
8. `y` (`int32_t`, 4 байти) — географічна довгота цільової точки (Longitude), масштабована на коефіцієнт `10⁷` (`degE7`), або локальна координата Y (метри на схід).
9. `z` (`float32`, 4 байти) — висота цільової точки (Altitude) у метрах. Математичний нуль цієї висоти визначається значенням поля `frame`.
10. `mission_type` (`uint8_t`, 1 байт) — цільовий тип контейнера польотного завдання: `0` для основної місії (`MAV_MISSION_TYPE_MISSION`), `1` для вершин забороненої геозони (`MAV_MISSION_TYPE_FENCE`), `2` для точок аварійного збору (`MAV_MISSION_TYPE_RALLY`).

Повний список структурних полів, констант і прапорців наведено в [двійковій специфікації протоколу місій](root:sys-dron/missions-waypoints/api-mission-item-protocol.md).

### Подолання дискретності float32: цілочисельний формат degE7

У ранніх ревізіях протоколу MAVLink координати передавалися в повідомленні `MISSION_ITEM` (`#39`) як 32-бітні числа одинарної точності IEEE 754 (`float`). Формат `float32` виділяє на мантису 23 біти, що забезпечує приблизно 7 десяткових знаків точності.

Коли довгота апарата перевищує `128.0°` (наприклад, у Тихоокеанському регіоні, на Далекому Сході чи в Північній Америці), двійковий порядок числа дорівнює `2⁷ = 128`. Вага молодшого біта мантиси (ULP, Unit in the Last Place) розраховується як:

```text
ULP = 2^(7 - 23) = 2^(-16) = 1 / 65536 градуса ≈ 0.000015258789°
```

Довжина одного градуса дуги на екваторі Землі (радіус R = 6378137 м) становить:

```text
L_deg = (2 · π · 6378137) / 360 ≈ 111319.5 м
```

Множення ULP на довжину градуса дає просторову дискретність представлення координат:

```text
ΔL = (1 / 65536) · 111319.5 м ≈ 1.6985 м
```

Дискретність у 1.7 метра означає, що при використанні `float32` координата не може бути задана точніше, ніж із кроком майже два метри. При наближенні до точки контур навігації стикається з постійним квантуванням цілевказівки, що провокує ривки рулів і коливання в супутникових RTK-режимах (де точність позиціонування становить 1–2 см).

Для вирішення цієї проблеми повідомлення `MISSION_ITEM_INT` кодує широту й довготу цілими 32-бітними числами зі знаком `int32_t` як degE7 = round(deg · 10⁷). Крок квантування при такому масштабуванні становить:

```text
ΔL_int = 10^(-7) · 111319.5 м ≈ 0.01113 м = 1.113 см
```

Сантиметрова дискретність повністю усуває похибки представлення у будь-якій точці земної кулі, зберігаючи розмір поля у межах 4 байтів.

### Координатні фрейми висоти

Визначення просторової вертикалі Z залежить від рельєфу та типу безпілотного апарата. Протокол визначає три базові фрейми:

- `MAV_FRAME_GLOBAL` (код `0` або `MAV_FRAME_GLOBAL_INT` код `5`) — висота Z задається в абсолютних метрах над середнім рівнем моря (AMSL, Above Mean Sea Level) за гравітаційною моделлю геоїда WGS-84 / EGM96. Використовується у великій цивільній авіації та на великих висотах польоту.
- `MAV_FRAME_GLOBAL_RELATIVE_ALT` (код `3` або `MAV_FRAME_GLOBAL_RELATIVE_ALT_INT` код `6`) — висота Z відраховується відносно точки старту або армування (Home Position). У мить старту висота приймається за 0.0 м. Це найпоширеніший фрейм для візуальних оглядів та картографування рівнинної місцевості.
- `MAV_FRAME_GLOBAL_TERRAIN_ALT` (код `10` або `MAV_FRAME_GLOBAL_TERRAIN_ALT_INT` код `11`) — висота над рівнем поверхні рельєфу (AGL, Above Ground Level). Бортовий навігатор зчитує цифрову матрицю висот рельєфу (DEM/SRTM) з карти пам'яті SD або коригує траєкторію за показниками лазерного чи радарного далекоміра, динамічно додаючи висоту поверхні до заданої висоти ешелону.

---

## Типи навігаційних команд: траєкторії, таймери та геометрія

Навігаційний кінцевий автомат автопілота по-різному обробляє різні типи просторових інструкцій. Поведінка апарата на кожному сегменті залежить від геометричного закону руху, кінематичних обмежень кутових прискорень та критеріїв завершення етапу.

![Кінематичні профілі навігаційних команд](/root/sys/sys-dron/missions-waypoints/img/navigation-command-trajectories.svg)
*Кінематичні профілі та просторові криві виконання базових навігаційних команд: прямолінійний проліт, кубічний сплайн Hermite, кружляння на орбіті, траєкторія зльоту та двофазна посадка.*

### 1. Автоматичний зліт: MAV_CMD_NAV_TAKEOFF (код 22)

Команда зльоту є обов'язковою початковою навігаційною інструкцією для автономних місій. 

- **Параметри:** `param1` визначає мінімальний кут тангажу (Pitch) при наборі висоти для літаків фіксованого крила (у градусах); `param4` — бажаний кут курсу (Yaw); `x, y` — координати точки зльоту (якщо передано `0, 0`, зліт виконується з поточної позиції); `z` — цільова висота виходу з режиму зльоту.
- **Кінематика:** Мультироторні апарати вмикають вертикальний контур набору висоти з лінійним профілем швидкості (зазвичай 1.5–2.5 м/с). Для літаків запускається розгін на максимальній тязі до досягнення швидкості відриву (V_stall · 1.3), після чого літак переходить у набір висоти під фіксованим кутом тангажу.
- **Критерій завершення:** Апарат досягає заданої висоти Z ± ΔZ_acc (де похибка ΔZ_acc зазвичай становить 0.5–1.0 м). Щойно умова виконується, навігатор перемикає `seq` на наступну інструкцію.

### 2. Прямолінійний проліт та зрізання кутів: MAV_CMD_NAV_WAYPOINT (код 16)

Базова команда руху між двома просторовими точками W_0 та W_1.

- **Параметри:** `param1` — час затримки (Hold Time) у секундах після досягнення цілі; `param2` — радіус прийняття (Acceptance Radius R_acc) у метрах; `param3` — радіус наскрізного прольоту (Pass Radius R_pass); `param4` — бажаний кут курсу носа апарата.
- **Критерії досягнення:**
  - *Сферичний радіус допуску:* Якщо поточні координати P(t) задовольняють умову ‖P(t) - W_1‖ ≤ R_acc, точка вважається досягнутою.
  - *Перетин площини дотичної (Passing Plane):* Для швидкісних літаків радіус повороту на швидкості 25 м/с може перевищувати 30 метрів. Якщо літак пролітає повз точку, не потрапляючи всередину малої сфери R_acc, навігатор перевіряє перетин нормальної площини до відрізка W_0 W_1, проведеної через точку W_1. Проєкція вектора положення на вектор відрізка стає більшою за одиницю, що запобігає зацикленню літака на повторних спробах розвороту.
  - *Плавне сполучення відрізків (Fly-Through Waypoint Transition):* Якщо `param1 == 0`, автопілот не зупиняється в точці W_1, а починає плавний поворот заздалегідь. Радіус дуги повороту розраховується з обмеження максимального бічного прискорення a_lat_max:

```text
R_turn = V_ground² / a_lat_max
```

Дистанція випередження початку маневру до точки W_1 становить:

```text
d_anticipation = R_turn · tan(θ_turn / 2)
```

де θ_turn — кут зміни курсу між сегментами W_0 W_1 та W_1 W_2. Секвенсер перемикає активну ціль на точку W_2 у мить перетину дистанції випередження, забезпечуючи плавне сполучення траєкторій без ривків швидкості.

### 3. Сплайновий плавний проліт: MAV_CMD_NAV_SPLINE_WAYPOINT (код 82)

Звичайна ламана лінія між точками вимагає повного або часткового гальмування перед вершинами кутів. Це призводить до нерівномірної швидкості, вібрацій та додаткових витрат енергії акумулятора. Команда `NAV_SPLINE_WAYPOINT` генерує траєкторію у вигляді неперервного кубічного ермітового сплайна (Catmull-Rom Spline).

Траєкторія S(u) для нормалізованого параметра u ∈ [0, 1] на відрізку між точками P_i та P_{i+1} будується на основі дотичних векторів швидкості T_i та T_{i+1}:

```text
S(u) = (2u³ - 3u² + 1)·P_i + (u³ - 2u² + u)·T_i + (-2u³ + 3u²)·P_{i+1} + (u³ - u²)·T_{i+1}
```

Дотичний вектор T_i у кожній проміжній вершині розраховується з напрямків на сусідні точки:

```text
T_i = 0.5 · (P_{i+1} - P_{i-1})
```

Завдяки неперервності першої похідної вектор швидкості V(t) = dS/dt не зазнає стрибків на межах точок. Дрон проходить плавні віражі без гальмування до нуля, утримуючи постійну швидкість сканування поверхні або відеозйомки.

### 4. Режими очікування: MAV_CMD_NAV_LOITER_TIME (код 19) та LOITER_TURNS (код 18)

- **NAV_LOITER_TIME:** Апарат прибуває в координати (X, Y, Z) і переходить у кружляння за круговою орбітою радіуса R_orbit = param3 (якщо R_orbit > 0 — за годинниковою стрілкою, якщо R_orbit < 0 — проти). Відлік інтервалу `param1` (секунди) розпочинається лише в момент першого входу апарата всередину сфери прийняття цілі.
- **NAV_LOITER_TURNS:** Виконується фіксована кількість повних обертів навколо точки, задана в `param1`. Навігатор веде акумулятор інтегрованого кута положення θ_acc = ∫ ω dt. Щойно θ_acc ≥ 2π · param1, апарат залишає орбіту за дотичною в напрямку наступної точки.

Геометрія виходу на орбіту завжди розраховується як дотична до кола радіуса R_orbit. Це унеможливлює різкі перегини траєкторії, при яких апарат був би змушений виконувати розворот на 180 градусів у мить входу в зону очікування.

### 5. Автоматична посадка: MAV_CMD_NAV_LAND (код 21)

Процедура посадки реалізує двофазний алгоритм вертикального зниження:

1. **Фаза швидкого спуску:** Апарат знижується з крейсерською швидкістю спуску (1.5–2.5 м/с) до висоти вирівнювання (Flare Altitude, зазвичай 3–5 метрів над землею).
2. **Фаза дотику (Flare & Touchdown):** Вертикальна швидкість обмежується значенням 0.3–0.5 м/с. Навігаційний контур блокує горизонтальні переміщення та аналізує стан детектора землі (Land Detector).
3. **Детектування посадки та роззброєння:** Стан посадки визнається дійсним, якщо протягом 1.5–2.0 секунд одночасно виконуються три умови: інтеграл вертикального прискорення близький до 1g, висота за лідаром/барометром не змінюється, а керівний сигнал газу (throttle output) знаходиться на мінімальному упорі. Після цього автопілот надсилає команду автоматичного роззброєння моторів (`Auto Disarm`).

---

## Взаємодія елементів місії з контуром навігаційного супроводу

Коли активна точка обрана, секвенсер місії не керує моторами безпосередньо, а генерує просторовий відрізок для контуру відстеження траєкторії (Path Follower).

### Коридор відхилення від лінії шляху (Cross-Track Error)

Між попередньою точкою A та поточною ціллю B формується опорний вектор лінії шляху AB. Поточне положення апарата P проєктується на цю пряму. Відстань від точки P до проєкції P_proj називається бічним відхиленням від лінії шляху (Cross-Track Error, e_xtrack).

Алгоритми навігації (наприклад, L1 Controller для літаків або Pure Pursuit для мультироторів) розраховують точку випередження на відрізку AB на відстані випередження L_1:

```text
L_1 = 2 · ζ · V_ground / ω_0
```

де V_ground — шляхова швидкість апарата, ζ — коефіцієнт демпфування (зазвичай 0.75), а ω_0 — власна частота контуру навігації. Контур формує бічне прискорення, пропорційне куту між вектором швидкості та напрямком на точку випередження. Це забезпечує плавне повернення апарата на лінію шляху без перерегулювання та розгойдувань навіть при сильному бічному вітрі.

### Черга асинхронних допоміжних команд (DO Commands Pipeline)

Місія може містити не лише просторові переміщення, але й команди дій (наприклад, `MAV_CMD_DO_CHANGE_SPEED` для зміни швидкості польоту перед заходом на зону сканування, `MAV_CMD_DO_SET_CAM_TRIGG_DIST` для запуску серійної фотозйомки або `MAV_CMD_DO_SET_SERVO` для скидання корисного навантаження).

Секвенсер місії обробляє ці команди за конвеєрним принципом:

1. Якщо після навігаційної точки слідує одна або кілька команд групи `DO`, автопілот виконує їх миттєво в тому ж навігаційному циклі, не зупиняючи просторовий рух.
2. Якщо команда `DO` змінює швидкість, новий ліміт передається у профіль розгону/гальмування регулятора положення.
3. Якщо команда `DO_SET_CAM_TRIGG_DIST` активує камеру, бортовий менеджер корисного навантаження інтегрує пройдену дистанцію від GPS-приймача та надсилає імпульс на оптопару затвора камери через кожні S метрів польоту.

### Обробка переривання місії та відновлення траєкторії

У реальній експлуатації оператор може перехопити ручне керування (перемикання в режим `Position Hold` або `Loiter` через стик передавача RC) для обльоту раптової перешкоди.

Коли оператор знову активує режим `Auto` (продовження місії), секвенсер не спрямовує апарат прямо на цільову точку під гострим кутом, оскільки це порушить розраховані галси фотограмметрії. Натомість автопілот розраховує ортогональну проєкцію поточної фізичної позиції на вихідний відрізок W_{k-1} W_k і відновлює рух коридором від проєкції до точки W_k.

---

## Протокол транзакційного завантаження місії

Радіоканал між наземною станцією керування (GCS) та безпілотним апаратом у польових умовах характеризується високим рівнем втрати пакетів (від 5% до 35% при роботі на далеких відстанях або в умовах радіозавад) та значними коливаннями затримок (Round-Trip Time від 50 мс до 1500 мс).

Передача місії «потоком» (коли станція просто відправляє всі точки поспіль без підтвердження) неприпустима: випадання навіть одного кадру спотворить послідовність маршруту. Для гарантування 100% цілісності в MAVLink реалізовано pull-орієнтований транзакційний кінцевий автомат.

![Транзакційний протокол завантаження місії над радіоканалом](/root/sys/sys-dron/missions-waypoints/img/mission-upload-protocol-fsm.svg)
*Часова діаграма взаємодії GCS та автопілота: ініціалізація лічильником MISSION_COUNT, запити точок від автопілота, відновлення після втрати пакета через таймаут та фінальний комміт MISSION_ACK.*

### Фази транзакції завантаження місії

1. **Ініціалізація (`MISSION_COUNT`):**
   GCS відправляє кадр `MISSION_COUNT`, у якому вказує загальну кількість елементів N та цільовий тип місії `mission_type`. Отримавши цей пакет, автопілот переводить кінцевий автомат у стан `UPLOADING`, блокує будь-які зміни поточної робочої місії, очищає тимчасовий буфер у RAM і запускає сторожовий таймер транзакції (Watchdog Timeout T_trans = 1500 мс).

2. **Покроковий запит точок (`MISSION_REQUEST_INT`):**
   Автопілот є ведучим (master) у процесі передачі: саме він генерує запит `MISSION_REQUEST_INT` для першого елемента з індексом `seq = 0`. Станція GCS у відповідь зобов'язана відправити пакет `MISSION_ITEM_INT` для запитаного індексу.

3. **Валідація та запис у тіньовий буфер:**
   Автопілот отримує `MISSION_ITEM_INT`, перевіряє рівність індексу очікуваному (`item.seq == expected_seq`), валідує координати та команди на допустимість діапазонів і записує точку у проміжний буфер. Після цього автопілот надсилає запит на наступний елемент `seq = 1`.

4. **Обробка втрат пакетів та таймаутів:**
   Якщо запит `MISSION_REQUEST_INT` або відповідь `MISSION_ITEM_INT` губляться в радіоефірі, станція і автопілот не отримують очікуваного кадру. Автопілот, не отримавши точку протягом 1500 мс, повторно відправляє той самий запит `MISSION_REQUEST_INT(seq)`. Лічильник спроб (Retry Counter) дозволяє до 5 повторів. Якщо після 5 спроб зв'язок не відновився, транзакція скасовується, тимчасовий буфер скидається, а попередня збережена місія залишається діючою.

5. **Фінальне підтвердження (`MISSION_ACK`):**
   Після успішного отримання останньої точки N - 1 автопілот проводить повний розрахунок контрольної суми буфера, зберігає дані в енергонезалежну пам'ять і відправляє станції фінальний пакет `MISSION_ACK` зі статусом `MAV_MISSION_ACCEPTED` (код `0`). Лише отримавши цей `ACK`, наземна станція вважає завантаження завершеним.

Якщо на будь-якому етапі надходить некоректна точка (наприклад, NaN у висоті або невідома команда), автопілот негайно припиняє процес і відправляє `MISSION_ACK` з відповідним кодом помилки (`MAV_MISSION_INVALID_PARAM`, `MAV_MISSION_UNSUPPORTED`).

---

## Зберігання місії в енергонезалежній пам'яті

Сучасні польотні контролери базуються на мікроконтролерах сімейств STM32F4, STM32F7 та STM32H7, що взаємодіють з різними типами енергонезалежних накопичувачів:

- **Внутрішня Flash-пам'ять MCU:** Має сектори великого розміру (від 16 КБ до 128 КБ на STM32F4). Операція стирання сектора блокує шину Flash на 20–50 мікросекунд, що може викликати зрив переривань у критичних контурах стабілізації (на частотах 400–1000 Гц), якщо не налаштовано апаратне стирання в окремому банку.
- **Зовнішня SPI / QSPI NOR Flash:** Наприклад, Winbond W25Q128. Дозволяє посекторне стирання блоками по 4 КБ та сторінковий запис по 256 байтів. Ресурс становить близько 100 000 циклів перезапису.
- **Сегнетоелектрична пам'ять FRAM (Ferroelectric RAM):** Наприклад, Cypress FM25V02. Забезпечує байтовий довільний доступ без необхідності попереднього стирання, має нульову затримку запису та ресурс 10¹⁴ циклів. Це ідеальний носій для критичних польотних параметрів та місій.

![Організація енергонезалежної пам'яті: Dual-Slot транзакційне сховище](/root/sys/sys-dron/missions-waypoints/img/flash-fram-storage-layout.svg)
*Архітектура дводіапазонної пам'яті NVRAM: сектор атомарного покажчика активного слота та два дзеркальні слоти із заголовками й масивами точок.*

### Архітектура подвійного слота (Dual-Slot Architecture)

Для забезпечення абсолютної стійкості до раптового вимкнення живлення пам'ять розбивається на два фізичні слоти — Слот A та Слот B, а також сектор покажчика активного слота:

```text
Структура Flash-пам'яті місій:
[Сектор Покажчика: 4 КБ] -> [Слот A: 60 КБ (Заголовок + Точки)] -> [Слот B: 60 КБ (Заголовок + Точки)]
```

- **Заголовок слота (Storage Header, 32 байти):**
  - `magic` (`uint32_t`) — магічне число `0x4D495353` (`'MISS'`);
  - `version` (`uint16_t`) — версія схеми даних;
  - `count` (`uint16_t`) — кількість збережених точок N;
  - `current_seq` (`uint16_t`) — збережений індекс активної точки на момент останнього збереження;
  - `crc16` (`uint16_t`) — контрольна сума всього масиву точок за стандартом CRC-16-CCITT;
  - `reserved` (20 байтів) — вирівнювання до 32 байтів.

- **Масив інструкцій:**
  Кожен елемент упаковується в структуру `mission_item_storage_t` (38 байтів). Для місії з 500 точок необхідний обсяг пам'яті складає 32 + (500 · 38) = 19 032 байти.

### Атомарне перемикання слотів

Під час запису нової місії драйвер виконує такі кроки:

1. Визначає неактивний (тіньовий) слот. Якщо активним є Слот A, запис спрямовується в Слот B.
2. Стирає сектори Слота B.
3. Послідовно записує всі точки нової місії та обчислює сумарний CRC-16.
4. Записує заголовок Слота B з обчисленим CRC-16.
5. Зчитує записані дані зі Слота B і перевіряє контрольну суму в пам'яті.
6. **Атомарний крок:** Стирає сектор покажчика та записує один байт нового активного індексу (`0x02` для Слота B).

Якщо живлення зникне на кроках 1–5, у секторі покажчика залишиться значення `0x01`. При наступному запуску автопілот відкриє непошкоджений Слот A, повністю проігнорувавши недописаний Слот B. Повний код драйвера сховища наведено в [проєкті транзакційного драйвера пам'яті](root:sys-dron/missions-waypoints/proj-mission-flash-storage.md).

---

## Повний модуль менеджера місій на C та C++

Нижче наведено виробничу реалізацію менеджера місій, який містить кінцевий автомат транзакційного протоколу MAVLink, буферизацію, перевірку таймаутів та зміну поточної навігаційної цілі.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MISSION_MAX_ITEMS           500u
#define MISSION_TIMEOUT_MS          1500u
#define MISSION_MAX_RETRIES         5u

typedef enum {
    MISSION_STATE_IDLE = 0,
    MISSION_STATE_UPLOADING,
    MISSION_STATE_DOWNLOADING,
    MISSION_STATE_ACTIVE,
    MISSION_STATE_PAUSED
} mission_fsm_state_t;

typedef struct __attribute__((packed)) {
    float param1;
    float param2;
    float param3;
    float param4;
    int32_t x;
    int32_t y;
    float z;
    uint16_t seq;
    uint16_t command;
    uint8_t frame;
    uint8_t current;
    uint8_t autocontinue;
    uint8_t mission_type;
} mission_item_t;

typedef struct {
    mission_fsm_state_t state;
    mission_item_t active_items[MISSION_MAX_ITEMS];
    mission_item_t staging_items[MISSION_MAX_ITEMS];
    uint16_t active_count;
    uint16_t staging_count;
    uint16_t transfer_seq;
    uint16_t current_active_seq;
    uint32_t last_transfer_time_ms;
    uint8_t retry_count;
    uint8_t partner_sysid;
    uint8_t partner_compid;
} mission_manager_t;

// Зовнішні функції надсилання MAVLink повідомлень
extern void mavlink_send_mission_request_int(uint8_t sysid, uint8_t compid, uint16_t seq);
extern void mavlink_send_mission_ack(uint8_t sysid, uint8_t compid, uint8_t result_type);
extern void mavlink_send_mission_current(uint16_t current_seq);
extern void mavlink_send_mission_item_reached(uint16_t reached_seq);

void mission_manager_init(mission_manager_t *mgr) {
    memset(mgr, 0, sizeof(mission_manager_t));
    mgr->state = MISSION_STATE_IDLE;
    mgr->active_count = 0;
    mgr->current_active_seq = 0;
}

// Обробка вхідного кадру MISSION_COUNT від GCS
void mission_manager_on_count(mission_manager_t *mgr, uint8_t sysid, uint8_t compid, uint16_t count, uint32_t now_ms) {
    if (count > MISSION_MAX_ITEMS) {
        mavlink_send_mission_ack(sysid, compid, 4); // MAV_MISSION_NO_SPACE
        return;
    }

    if (count == 0) {
        // Повне очищення місії
        mgr->active_count = 0;
        mgr->current_active_seq = 0;
        mgr->state = MISSION_STATE_IDLE;
        mavlink_send_mission_ack(sysid, compid, 0); // MAV_MISSION_ACCEPTED
        return;
    }

    mgr->state = MISSION_STATE_UPLOADING;
    mgr->staging_count = count;
    mgr->transfer_seq = 0;
    mgr->retry_count = 0;
    mgr->partner_sysid = sysid;
    mgr->partner_compid = compid;
    mgr->last_transfer_time_ms = now_ms;

    // Запитуємо перший елемент seq = 0
    mavlink_send_mission_request_int(sysid, compid, 0);
}

// Обробка вхідного дескриптора точки MISSION_ITEM_INT
void mission_manager_on_item(mission_manager_t *mgr, const mission_item_t *item, uint32_t now_ms) {
    if (mgr->state != MISSION_STATE_UPLOADING) {
        return;
    }

    if (item->seq != mgr->transfer_seq) {
        // Порушення черговості — повторюємо запит актуального індексу
        mavlink_send_mission_request_int(mgr->partner_sysid, mgr->partner_compid, mgr->transfer_seq);
        return;
    }

    // Зберігаємо точку в буфері
    mgr->staging_items[mgr->transfer_seq] = *item;
    mgr->transfer_seq++;
    mgr->retry_count = 0;
    mgr->last_transfer_time_ms = now_ms;

    if (mgr->transfer_seq < mgr->staging_count) {
        // Запитуємо наступний елемент
        mavlink_send_mission_request_int(mgr->partner_sysid, mgr->partner_compid, mgr->transfer_seq);
    } else {
        // Усі точки отримано — атомарна фіксація
        memcpy(mgr->active_items, mgr->staging_items, mgr->staging_count * sizeof(mission_item_t));
        mgr->active_count = mgr->staging_count;
        mgr->current_active_seq = (mgr->active_count > 1) ? 1 : 0;
        mgr->state = MISSION_STATE_IDLE;

        mavlink_send_mission_ack(mgr->partner_sysid, mgr->partner_compid, 0); // MAV_MISSION_ACCEPTED
        mavlink_send_mission_current(mgr->current_active_seq);
    }
}

// Періодичний сторожовий таймер транзакцій (виклик з частотою 10-50 Гц)
void mission_manager_tick(mission_manager_t *mgr, uint32_t now_ms) {
    if (mgr->state == MISSION_STATE_UPLOADING) {
        if ((now_ms - mgr->last_transfer_time_ms) >= MISSION_TIMEOUT_MS) {
            if (mgr->retry_count < MISSION_MAX_RETRIES) {
                mgr->retry_count++;
                mgr->last_transfer_time_ms = now_ms;
                mavlink_send_mission_request_int(mgr->partner_sysid, mgr->partner_compid, mgr->transfer_seq);
            } else {
                // Вичерпано ліміт спроб — скасування транзакції
                mgr->state = MISSION_STATE_IDLE;
                mavlink_send_mission_ack(mgr->partner_sysid, mgr->partner_compid, 15); // MAV_MISSION_OPERATION_CANCELLED
            }
        }
    }
}

// Перемикання на наступну точку після завершення поточної
bool mission_manager_advance(mission_manager_t *mgr) {
    if (mgr->active_count == 0 || mgr->current_active_seq >= mgr->active_count - 1) {
        return false;
    }

    mavlink_send_mission_item_reached(mgr->current_active_seq);
    mgr->current_active_seq++;
    mavlink_send_mission_current(mgr->current_active_seq);
    return true;
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <expected>
#include <optional>
#include <algorithm>

#pragma pack(push, 1)
struct MissionItem {
    float param1{0.0f};
    float param2{0.0f};
    float param3{0.0f};
    float param4{0.0f};
    int32_t x{0};
    int32_t y{0};
    float z{0.0f};
    uint16_t seq{0};
    uint16_t command{16};
    uint8_t frame{3};
    uint8_t current{0};
    uint8_t autocontinue{1};
    uint8_t mission_type{0};
};
#pragma pack(pop)

enum class MissionState : uint8_t {
    Idle,
    Uploading,
    Downloading,
    Active,
    Paused
};

enum class MissionAckResult : uint8_t {
    Accepted = 0,
    Error = 1,
    UnsupportedFrame = 2,
    Unsupported = 3,
    NoSpace = 4,
    Invalid = 5,
    InvalidSequence = 13,
    Cancelled = 15
};

class IMavlinkMissionMessenger {
public:
    virtual ~IMavlinkMissionMessenger() = default;
    virtual void send_request_int(uint8_t sysid, uint8_t compid, uint16_t seq) = 0;
    virtual void send_ack(uint8_t sysid, uint8_t compid, MissionAckResult result) = 0;
    virtual void send_current(uint16_t current_seq) = 0;
    virtual void send_item_reached(uint16_t reached_seq) = 0;
};

class MissionManager {
public:
    static constexpr size_t MAX_ITEMS = 500;
    static constexpr uint32_t TIMEOUT_MS = 1500;
    static constexpr uint8_t MAX_RETRIES = 5;

    explicit MissionManager(IMavlinkMissionMessenger& messenger)
        : m_messenger(messenger) {}

    void on_mission_count(uint8_t sysid, uint8_t compid, uint16_t count, uint32_t now_ms) noexcept {
        if (count > MAX_ITEMS) {
            m_messenger.send_ack(sysid, compid, MissionAckResult::NoSpace);
            return;
        }

        if (count == 0) {
            m_active_count = 0;
            m_current_active_seq = 0;
            m_state = MissionState::Idle;
            m_messenger.send_ack(sysid, compid, MissionAckResult::Accepted);
            return;
        }

        m_state = MissionState::Uploading;
        m_staging_count = count;
        m_transfer_seq = 0;
        m_retry_count = 0;
        m_partner_sysid = sysid;
        m_partner_compid = compid;
        m_last_transfer_time_ms = now_ms;

        m_messenger.send_request_int(sysid, compid, 0);
    }

    void on_mission_item(const MissionItem& item, uint32_t now_ms) noexcept {
        if (m_state != MissionState::Uploading) {
            return;
        }

        if (item.seq != m_transfer_seq) {
            m_messenger.send_request_int(m_partner_sysid, m_partner_compid, m_transfer_seq);
            return;
        }

        m_staging_buffer[m_transfer_seq] = item;
        m_transfer_seq++;
        m_retry_count = 0;
        m_last_transfer_time_ms = now_ms;

        if (m_transfer_seq < m_staging_count) {
            m_messenger.send_request_int(m_partner_sysid, m_partner_compid, m_transfer_seq);
        } else {
            // Атомарна фіксація місії
            std::copy_n(m_staging_buffer.begin(), m_staging_count, m_active_buffer.begin());
            m_active_count = m_staging_count;
            m_current_active_seq = (m_active_count > 1) ? 1 : 0;
            m_state = MissionState::Idle;

            m_messenger.send_ack(m_partner_sysid, m_partner_compid, MissionAckResult::Accepted);
            m_messenger.send_current(m_current_active_seq);
        }
    }

    void tick(uint32_t now_ms) noexcept {
        if (m_state != MissionState::Uploading) {
            return;
        }

        if ((now_ms - m_last_transfer_time_ms) >= TIMEOUT_MS) {
            if (m_retry_count < MAX_RETRIES) {
                m_retry_count++;
                m_last_transfer_time_ms = now_ms;
                m_messenger.send_request_int(m_partner_sysid, m_partner_compid, m_transfer_seq);
            } else {
                m_state = MissionState::Idle;
                m_messenger.send_ack(m_partner_sysid, m_partner_compid, MissionAckResult::Cancelled);
            }
        }
    }

    [[nodiscard]] bool advance_waypoint() noexcept {
        if (m_active_count == 0 || m_current_active_seq >= m_active_count - 1) {
            return false;
        }

        m_messenger.send_item_reached(m_current_active_seq);
        m_current_active_seq++;
        m_messenger.send_current(m_current_active_seq);
        return true;
    }

    [[nodiscard]] std::optional<MissionItem> current_item() const noexcept {
        if (m_active_count == 0 || m_current_active_seq >= m_active_count) {
            return std::nullopt;
        }
        return m_active_buffer[m_current_active_seq];
    }

    [[nodiscard]] uint16_t active_count() const noexcept { return m_active_count; }
    [[nodiscard]] uint16_t current_seq() const noexcept { return m_current_active_seq; }
    [[nodiscard]] MissionState state() const noexcept { return m_state; }

private:
    IMavlinkMissionMessenger& m_messenger;
    MissionState m_state{MissionState::Idle};
    std::array<MissionItem, MAX_ITEMS> m_active_buffer{};
    std::array<MissionItem, MAX_ITEMS> m_staging_buffer{};
    uint16_t m_active_count{0};
    uint16_t m_staging_count{0};
    uint16_t m_transfer_seq{0};
    uint16_t m_current_active_seq{0};
    uint32_t m_last_transfer_time_ms{0};
    uint8_t m_retry_count{0};
    uint8_t m_partner_sysid{0};
    uint8_t m_partner_compid{0};
};
```
:::
