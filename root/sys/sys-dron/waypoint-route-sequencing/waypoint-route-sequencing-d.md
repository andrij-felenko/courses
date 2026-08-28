# Навігація за маршрутними точками

<preknowlist>
- [Елементи місії й команди](root:sys-dron/mission-items) — як задаються параметри точок у MAVLink: координати, радіус, час зависання, кут курсу.
- [Протокол місій MAVLink](root:sys-dron/mavlink-mission-protocol) — завантаження, підтвердження та перемикання активної точки через протокол зв'язку.
- [Відхилення від лінії шляху (cross-track)](root:sys-dron/vidkhylennia-vid-linii-shliakhu-cross-track) — розрахунок бокового зміщення та утримання коридору між двома точками.
- [Навігація pure pursuit](root:sys-dron/pure-pursuit-navigation) — ведення апарата по кривій за точкою випередження на маршруті.
- [Модель плану](root:sys-dron/plan-model) — структура плану польоту: місії, геозони та точки збору.
</preknowlist>

Якщо автопілот просто видаватиме тягу двигунів у бік координат кінцевого пункту, політ перетвориться на серію невдалих маневрів: апарат проскакуватиме точки на великій швидкості, зупинятиметься до нуля на кожному плавному вигині, розгойдуватиметься від вітру або вийде на нескінченне кружляння навколо пропущеної цілі. Автономне виконання місії вимагає окремого навігаційного прошарку — **секвенсера маршрутних точок** (англ. *waypoint route sequencer*, від лат. *sequi* — іти слідом). Цей модуль перетворює статичний масив польотних завдань на неперервний потік просторових цілей (setpoints) для регуляторів швидкості, положення та курсу, контролюючи точні геодезичні критерії завершення кожного відрізка.

Секвенсер є містком між стратегічним рівнем (глобальним планом польоту, отриманим від наземної станції керування) та тактичним рівнем (контурами відстеження ліній шляху та стабілізації просторової орієнтації). Він не керує моторами безпосередньо, але саме він вирішує, яка просторова точка є актуальною в поточний момент часу, коли вважати сегмент виконаним, як плавно спрямувати ніс апарата чи підвіс камери та за якою траєкторією переходити між сусідніми галсами.

## Анатомія місії: послідовність шляхових точок

План польоту в пам'яті автопілота зберігається як упорядкований масив структур-дескрипторів. Кожна шляхова точка (англ. *waypoint*) містить просторові координати цілі, кінематичні обмеження прольоту та накази для корисного навантаження.

У загальному вигляді навігаційний стан точки описується вектором:

```text
W[i] = [lat, lon, alt, v_cruise, R_acc, t_hold, yaw_target, action_id, flags]
```

Компоненти цього вектора визначають поведінку апарата на сегменті:

1. `lat, lon` — географічна широта й довгота у системі WGS-84 (десяткові градуси, що масштабуються до цілих чисел `10⁻⁷` градуса для уникнення втрати точності дробових чисел одинарної точності).
2. `alt` — висота цілі у метрах. Залежно від системи відліку (frame), вона може бути абсолютною над середнім рівнем моря (AMSL), відносною до точки зльоту (Relative Home) або над рівнем рельєфу (Terrain AGL).
3. `v_cruise` — бажана швидкість руху вздовж сегмента (м/с). Якщо поле не задане (або дорівнює нулю чи `NaN`), автопілот використовує системну круїзну швидкість із глобальних параметрів.
4. `R_acc` — радіус кулі або циліндра досягнення точки (Acceptance Radius) у метрах.
5. `t_hold` — час обов'язкової затримки (зависання/очікування) у точці після її досягнення (секунди).
6. `yaw_target` — бажаний кут рискання апарата (градуси чи радіани) або спеціальний прапорець автоматичного розрахунку курсу (`NaN` або `YAW_MODE_ALONG_TRACK`).
7. `action_id` — команда для виконання корисним навантаженням (спуск затвора камери, скидання вантажу через сервопривід, увімкнення реле, запуск вимірювального сканера).
8. `flags` — бітова маска конфігурації: прапорець плавного прольоту без зупинки (Fly-Through), автопродовження до наступного елемента (`autocontinue`), блокування зміни висоти до досягнення горизонтальних координат.

Навігаційний модуль працює з трьома індексами масиву:

- `seq_prev` — індекс точки початку поточного відрізка `W[k-1]`;
- `seq_curr` — індекс поточної цільової точки `W[k]`;
- `seq_next` — індекс наступної точки `W[k+1]`, потрібний для попереднього планування радіуса повороту та згладжування швидкості.

### Системи відліку висоти та перетворення координат

Висота в автопілотах є багатозначним поняттям, і помилка у виборі системи відліку призводить до зіткнення з пагорбами або польоту на неприпустимо низькому ешелоні. MAVLink та бортові прошивки підтримують три основні системи відліку висоти:

1. `MAV_FRAME_GLOBAL` — абсолютна висота AMSL (Above Mean Sea Level) відносно гравітаційного геоїда Землі (моделі WGS-84 / EGM96). Це значення видають барометричні висотоміри з поправкою тиску QNH та геодезичні GNSS-приймачі.
2. `MAV_FRAME_GLOBAL_RELATIVE_ALT` — висота над точкою армування (Home Position). Приймається за нуль у мить зльоту дрона. Найпопулярніший режим для місій на рівнинній місцевості.
3. `MAV_FRAME_GLOBAL_TERRAIN_ALT` — висота AGL (Above Ground Level) над поверхнею землі. Автопілот бере цифрову карту висот рельєфу (SRTM або DEM-тайли, завантажені на SD-карту або трансльовані зі станції керування) або дані далекоміра (радарного чи лідарного) і постійно додає висоту рельєфу `h_terrain(lat, lon)` до заданої відносної висоти:

```text
alt_target_msl = h_terrain(lat, lon) + alt_agl
```

Перш ніж виконувати векторні обчислення навігації, глобальні геодезичні координати (WGS-84) переводять у локальну декартову систему координат NED (North-East-Down), початок відліку якої фіксується в точці старту апарата (Home Position). Для відстаней у межах десятків кілометрів застосовують проєкцію еквідистантної циліндричної моделі (Equirectangular Approximation):

```text
x_ned = (lat − lat_0) · (π / 180) · R_earth
y_ned = (lon − lon_0) · (π / 180) · R_earth · cos(lat_0 · π / 180)
z_ned = −(alt − alt_0)
```

де `R_earth ≈ 6 371 000 м` — середній радіус Землі. Знак мінус для `z_ned` відповідає авіаційному стандарту NED, де вісь Down спрямована до центру Землі.

> 🔧 **Навіщо це.** Декартова система координат NED позбавляє контури керування від важких тригонометричних функцій на кожному такті 50–400 Гц. Усі відстані, швидкості, скалярні та векторні добутки обчислюються у простих метрах, що критично для бортових мікроконтролерів реального часу без надлишкової обчислювальної потужності.

## Умова проходження точки: куля досягнення проти площини прольоту

Найпростіший спосіб визначити, чи досяг апарат призначеної точки, — перевірити евклідову відстань від поточної позиції `P = [x, y, z]ᵀ` до цілі `W[k] = [x_k, y_k, z_k]ᵀ`.

Для мультикоптерів та наземних роботів перевірка здійснюється за радіусом кулі або циліндра досягнення (Acceptance Radius `R_acc`):

```text
d_horizontal = √((x − x_k)² + (y − y_k)²)
d_vertical   = |z − z_k|

is_inside_acceptance = (d_horizontal ≤ R_acc) AND (d_vertical ≤ R_acc_z)
```

де `R_acc_z` — допустима вертикальна похибка (зазвичай `0.5–2.0 м`).

![Куля досягнення та площина прольоту](/root/sys/sys-dron/waypoint-route-sequencing/img/acceptance-criteria.svg)
*Геометрія критеріїв проходження шляхової точки. Траєкторія 1 потрапляє в кулю досягнення R_acc. Траєкторія 2 зноситься вітром або проходить повз кулю через високу швидкість: перетин ортогональної площини (Passing Plane) своєчасно перемикає ціль на наступну точку W_k+1, запобігаючи нескінченному кружлянню.*

### Пастка пропущеної точки (Missed Waypoint Loiter Trap)

Покладання виключно на умову `d_horizontal ≤ R_acc` є фундаментальною інженерною помилкою, здатною призвести до аварії. Розгляньмо, що відбувається, коли літак, крило або швидкісний дрон летить зі швидкістю `v = 20 м/с` при бічному вітрі `8 м/с`, а радіус досягнення налаштовано як `R_acc = 5 м`:

1. Через бічний знос або затримку контуру стабілізації апарат проходить повз точку `W[k]` на відстані `6.5 м` (тобто `d > R_acc`).
2. Оскільки умова `d ≤ R_acc` не виконана, секвенсер вважає точку недосягнутою і продовжує видавати команду на рух до `W[k]`.
3. Апарат уже пролетів точку вперед. Контур навігації формує команду максимального розвороту назад.
4. Фізичний мінімальний радіус розвороту апарата на цій швидкості становить `R_min = v² / (g · tan(φ_max)) ≈ 35 м` (за кута крену `φ = 30°`).
5. Здійснюючи віраж радіусом `35 м`, літак фізично не може потрапити в коло радіусом `5 м`, розташоване в центрі його кола обертання.
6. Апарат виходить на нескінченну орбітальну траєкторію довкола точки, спалює все пальне чи заряд акумулятора і падає через аварійне виснаження живлення.

### Детектор перетину площини прольоту (Passing Plane Detection)

Для подолання цієї вразливості автопілоти використовують комбінований критерій: точку визнають пройденою, якщо апарат увійшов у сферу `R_acc` **АБО** перетнув ортогональну площину прольоту (Passing Plane).

Площина прольоту проходить через цільову точку `W[k]` перпендикулярно до вектора сегмента наближення `u_in = (W[k] − W[k-1]) / ||W[k] − W[k-1]||`.

Вектор положення апарата відносно цілі:

```text
d_target = P − W[k]
```

Скалярний добуток вектора зміщення на одиничний вектор відрізка дає знак проходження площини:

```text
s_pass = d_target · u_in = (P − W[k]) · u_in
```

Якщо `s_pass < 0`, апарат перебуває на підльоті до точки.
Щойно `s_pass ≥ 0`, апарат перетнув нормальну площину точки `W[k]`.

Щоб площина не спрацьовувала, коли дрон летить паралельним курсом за сотні метрів від траєкторії, перетин площини валідується допустимим коридором бічного відхилення:

```text
is_waypoint_passed = (||P − W[k]|| ≤ R_acc) OR ((d_target · u_in ≥ 0) AND (|e_ct| ≤ R_max_cross))
```

де `e_ct` — лінійна поперечна похибка (Cross-Track Error) відносно сегмента `W[k-1] → W[k]`.

Повний математичний апарат із векторними виведеннями для бісекторної площини на довільних кутах зламу та строгий аналіз дискретних кроків інтегрування наведено у вставці [Геометричне виведення площини прольоту](root:sys-dron/waypoint-route-sequencing/math-passing-plane.md).

## Зупинка в точці проти плавного обльоту

У практичних місіях точки маршруту поділяють на два принципово різні типи за динамікою проходження:

1. **Fly-Over (Stop-at-Waypoint)** — точка обов'язкової зупинки;
2. **Fly-Through (Spline / S-Curve Waypoint)** — точка безперервного транзитного прольоту зі збереженням швидкості.

![Зупинка в точці проти плавного обльоту](/root/sys/sys-dron/waypoint-route-sequencing/img/fly-over-vs-fly-through.svg)
*Порівняння динаміки руху. Ліворуч: режим Fly-Over із повним гальмуванням до v = 0, витримкою часу t_hold та розворотом на місці. Праворуч: режим Fly-Through із постійною круїзною швидкістю та плавним зрізанням кута по дузі радіуса R_corner з контролем бічного прискорення.*

### Режим Fly-Over (Зупинка та дія)

Режим Fly-Over призначений для задач, які вимагають прецизійної фіксації апарата в просторі: точкове скидання вантажу, отримання високоякісного фотокадру без змазування (motion blur), лазерне далекомірне сканування, інспекція конструкцій чи посадка.

Динамічний профіль Fly-Over складається з чотирьох послідовних фаз:

1. **Гальмування (Deceleration):** За наближення до точки на гальмівну відстань `d_brake = v² / (2 · a_max)` профіль швидкості знижується за S-подібною кривою з обмеженням ривка (jerk-limited braking), зводячи швидкість у точці `W[k]` строго до нуля.
2. **Захоплення положення (Position Hold):** Після зупинки в межах радіуса `R_acc` запускається таймер витримки `t_hold`.
3. **Виконання дії (Payload Action):** Секвенсер надсилає команду на спрацьування корисного навантаження (імпульс на затвор камери, команда по шині CAN чи PWM-сигнал сервоприводу).
4. **Розворот на місці та розгін:** Апарат повертає корпус у напрямку наступного сегмента `W[k] → W[k+1]` і починає плавне прискорення з темпом `a_accel`.

Ціна такого режиму — підвищене енергоспоживання (витрати енергії на постійні гальмування й розгони) та суттєве збільшення загального часу місії.

### Траєкторії з обмеженням ривка (Jerk-Limited S-Curves)

У сучасних автопілотах (PX4, ArduPilot) профіль гальмування та розгону будується не за простою трапецією (де прискорення змінюється східчасто), а за 7-фазною S-кривою, де обмежено похідну прискорення — ривок `j(t) = da/dt`:

```text
j(t) ≤ j_max
a(t) = ∫ j(t) dt ≤ a_max
v(t) = ∫ a(t) dt ≤ v_cruise
s(t) = ∫ v(t) dt
```

Східчаста зміна прискорення у звичайних трапецеїдальних регуляторах створює миттєвий нескінченний ривок `j = ∞`. Це викликає різкі сплески струму в силових регуляторах обертів (ESC), паразитні вібрації рами дрона, зрив потоку на кінцях пропелерів і тремтіння підвісу камери. Обмеження ривка `j_max` гарантує плавне наростання струмів і високу якість відеозйомки навіть при різких змінах польотного завдання.

### Режим Fly-Through (Плавний обліт за сплайном)

Для задач картографування площ галсами (Survey), патрулювання периметра чи транзитного перельоту зупинятися на кожному проміжному зламі маршруту неефективно. Режим Fly-Through забезпечує проходження поворотів на незмінній круїзній швидкості за рахунок завчасного зрізання кутів (Corner Cutting).

Точка переходу розраховується геометрично. Нехай кут між відрізками становить `θ`. Радіус дуги розвороту `R_corner` обирається з обмеження максимального допустимого бічного прискорення `a_lat_max` (для коптерів це відповідає обмеженню кута крену `tan(φ_max) = a_lat / g`):

```text
R_corner = v_cruise² / a_lat_max
```

Відстань початку маневру до точки зламу `W[k]`:

```text
d_transition = R_corner · tan(θ / 2)
```

Коли відстань до точки `W[k]` стає меншою або рівною `d_transition`, секвенсер автоматично перемикає активний цільовий сегмент на `W[k] → W[k+1]`. Поточна ціль для контуру слідування генерується за кубічним ермітовим сплайном (Cubic Hermite Spline) або кривою Безьє, зшиваючи позицію, вектор швидкості та вектор прискорення на стику двох відрізків без розривів.

## Керування кутом рискання (Yaw Coordination)

На відміну від літаків, де напрямок носа жорстко пов'язаний із вектором повітряної швидкості через аеродинаміку кіля та кут ковзання, мультикоптер володіє повною кінематичною розв'язкою між вектором лінійної швидкості `V = [v_x, v_y, v_z]` та кутом рискання `ψ` (Yaw). Дрон може летіти на північ зі швидкістю 15 м/с, маючи ніс, повернутий на схід, захід чи південь.

Секвенсер маршруту підтримує три основні режими координації курсу:

![Три режими узгодження курсу](/root/sys/sys-dron/waypoint-route-sequencing/img/yaw-modes.svg)
*Режими узгодження курсу: 1) Фіксований курс для кругових сенсорів. 2) Курс за вектором маршруту для мінімізації аеродинамічного опору. 3) Неперервне наведення на фіксовану точку інтересу (ROI) під час польоту складним контуром.*

### 1. Фіксований курс (Fixed Heading)

Кут рискання задається параметром `param4` конкретної шляхової точки і залишається незмінним протягом усього сегмента польоту:

```text
ψ_cmd(t) = ψ_fixed = const
```

Цей режим необхідний під час роботи з лідарами кругового огляду 360°, магнітометричної зйомки (де обертання корпусу вносить фазові спотворення у вимірювання власного магнітного поля) або під час польотів в умовах вузьких інспекційних коридорів поблизу ліній електропередач.

### 2. Курс за напрямком маршруту (Facing Next Waypoint / Along Track)

Ніс апарата автоматично розгортається вздовж вектора поточного або наступного сегмента:

```text
Δx = x[k] − x(t)
Δy = y[k] − y(t)

ψ_cmd(t) = atan2(Δy, Δx)
```

Для запобігання різким стрибкам курсу, якщо точка знаходиться майже вертикально над апаратом або на відстані менше 1 метра, обчислення `atan2` блокується, і дрон зберігає попередній курс.

Цей режим забезпечує:
- Мінімальний лобовий аеродинамічний опір конструкції;
- Правильний огляд курсової FPV-камери пілота;
- Захист сенсорів переднього огляду (Stereo Vision, далекоміри оптичного потоку) від сліпих зон під час маневрування.

### 3. Наведення на точку інтересу (Region of Interest / ROI)

Команда `MAV_CMD_DO_SET_ROI` задає фіксовану або динамічну координату в просторі `T_roi = [x_roi, y_roi, z_roi]ᵀ`. Під час руху за будь-якою складною ламаною траєкторією секвенсер неперервно оновлює цільовий кут рискання корпусу дрона (або 3-осьового гіростабілізованого підвісу камери):

```text
Δx_roi = x_roi − x(t)
Δy_roi = y_roi − y(t)
Δz_roi = z_roi − z(t)

ψ_cmd(t) = atan2(Δy_roi, Δx_roi)
```

Для підвісу камери додатково обчислюється кут тангажу (Pitch):

```text
d_ground = √(Δx_roi² + Δy_roi²)
θ_gimbal(t) = atan2(Δz_roi, d_ground)
```

Швидкість повороту за рисканням лімітується параметром максимальної кутової швидкості `ω_yaw_max` (наприклад, `45°/с` для плавного відеокадру):

```text
e_yaw = wrap_pi(ψ_cmd − ψ_curr)
ψ_rate_cmd = clamp(k_p_yaw · e_yaw, −ω_yaw_max, +ω_yaw_max)
```

де `wrap_pi(α)` зводить кутову похибку до діапазону `[−π, +π]`.

## Вертикальне профілювання та обробка висоти (3D Waypoint Sequencing)

У тривимірному просторі зміна висоти між точками `W[k-1]` та `W[k]` може відбуватися за двома різними стратегіями:

1. **Одночасне просторове наведення (3D Vector Steer):** Апарат одночасно змінює горизонтальні координати й висоту, рухаючись строго похилим тривимірним вектором:

```text
v_xy = v_cruise · cos(γ)
v_z  = v_cruise · sin(γ)
```

де `γ = arctan((z[k] − z[k-1]) / L_xy)` — кут нахилу траєкторії. Цей режим є основним для зйомок та картографування.

2. **Ступінчастий підйом (Climb-First Waypoints):** Застосовується під час польотів у гірській місцевості або при виході з лісових просік. Якщо прапорець `NAV_ALT_HOLD` або параметр `param1` вимагає спочатку набрати безпечну висоту, секвенсер блокує горизонтальний рух (`v_xy = 0`), доки висота не досягне `|z(t) − z[k]| ≤ R_acc_z`, і лише після цього дозволяє рух до цілі. Це гарантує, що апарат не вріжеться у верхівки дерев під час набору висоти на старті галса.

## Взаємодія секвенсера з контурами стеження за лінією

Секвенсер не веде дрон по лінії самостійно: його завдання — своєчасно перемикати активний відрізок `W[k-1] → W[k]` і передавати параметри сегмента в контур бічного наведення.

В автопілотах використовують два основні сімейства алгоритмів стеження:

1. **Нелінійне наведення L1 / NPFG (Nonlinear Path Following Guidance):** Контур обирає віртуальну точку наведення на відрізку маршруту на відстані випередження `L_1 = 2 · ζ · v / ω_n` (де `ζ` — коефіцієнт демпфування, `ω_n` — власна частота) і формує бажане бічне прискорення `a_cmd = 2 · (v² / L_1) · sin(η)`, де `η` — кут між вектором швидкості дрона та вектором на точку наведення.
2. **Алгоритм прямої видимості з інтегратором (ILOS / Pure Pursuit):** Розраховує кут випередження `χ_los = χ_path + arctan(−e_ct / Δ + σ_int)`, де `e_ct` — бічне відхилення, `Δ` — відстань погляду вперед, а `σ_int` — інтегратор зносу вітром.

Щоб запобігти високочастотному брязкоту перемикання (Switching Chatter), коли алгоритм перестрибує між сусідніми сегментами, відстань випередження `L_1` та радіус кулі `R_acc` узгоджують за правилом:

```text
L_1 ≥ 1.5 · R_acc
```

Це гарантує, що контур наведення плавно «підхоплює» наступний відрізок ще до того, як апарат досягне фізичної точки зламу.

## Архітектура автомата станів секвенсера

Керування місією реалізується як кінцевий автомат (Finite State Machine, FSM), який виконується з фіксованою частотою навігаційного циклу (зазвичай `50 Гц`).

![Автомат станів секвенсера місії](/root/sys/sys-dron/waypoint-route-sequencing/img/sequencer-fsm.svg)
*Діаграма станів навігаційного секвенсера: обробка навігаційного наближення, таймерів очікування, команд корисного навантаження та перемикання індексів.*

Автомат підтримує шість базових станів:

1. `ST_IDLE` — місія не активна або стоїть на паузі. Регулятори виконують команди ручного керування чи утримання позиції.
2. `ST_NAVIGATING` — активний рух до точки `W[k]`. Контур навігації генерує цілі швидкості та курсу. Щотакту перевіряється комбінована умова досягнення точки (Acceptance Sphere + Passing Plane).
3. `ST_LOITER_HOLD` — апарат досяг координат точки `W[k]`. Швидкість скинуто до нуля, запущено зворотний відлік таймера `t_hold`.
4. `ST_EXEC_ACTION` — таймер `t_hold` вичерпано. Виконується наказ корисного навантаження (спуск затвора камери, скидання вантажу).
5. `ST_ADVANCE_WP` — інкремент індексу `seq_curr++`. Оновлення векторів сегментів `u_in`, `u_out`, завантаження нових обмежень швидкості. Якщо активна точка була останньою (`seq_curr >= N`), автомат ініціює завершення місії.
6. `ST_MISSION_DONE` — виконання плану завершено. Секвенсер передає керування модулю повернення додому (RTL) або автопосадці (Land).

## Телеметрія та протокольний обмін MAVLink

Під час автономного польоту секвенсер маршруту постійно повідомляє наземній станції керування (QGroundControl чи Mission Planner) про стан виконання місії:

- `MISSION_CURRENT` (повідомлення #42) — транслює індекс поточної активної точки `seq`. Станція підсвічує активний галс жовтим кольором.
- `NAV_CONTROLLER_OUTPUT` (повідомлення #62) — передає розрахунковий кут курсу на ціль `nav_bearing`, кут бажаного курсу `target_bearing`, дистанцію до активної точки `wp_dist` (метри) та миттєву бічну похибку відхилення від лінії `xtrack_error` (метри).
- `POSITION_TARGET_LOCAL_NED` (повідомлення #85) — транслює миттєві просторові цілі (позиція, швидкість, прискорення, рискання), які секвенсер видає внутрішньому контуру регуляторів.

## Реалізація модуля секвенсера на C та C++

Нижче наведено повний промисловий модуль секвенсера маршрутних точок. Він містить конвертацію геодезичних координат у NED, перевірку кулі та площини прольоту, розрахунок цілей курсу (Fixed, Track, ROI), обробку затримок та перемикання станів.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define M_PI_F 3.14159265358979323846f
#define DEG_TO_RAD_F (M_PI_F / 180.0f)
#define RAD_TO_DEG_F (180.0f / M_PI_F)
#define CONSTANTS_RADIUS_OF_EARTH 6371000.0f

typedef enum {
    YAW_MODE_ALONG_TRACK = 0,
    YAW_MODE_FIXED       = 1,
    YAW_MODE_ROI         = 2
} yaw_mode_t;

typedef enum {
    SEQ_STATE_IDLE         = 0,
    SEQ_STATE_NAVIGATING   = 1,
    SEQ_STATE_LOITER_HOLD  = 2,
    SEQ_STATE_EXEC_ACTION  = 3,
    SEQ_STATE_ADVANCE_WP   = 4,
    SEQ_STATE_MISSION_DONE = 5
} seq_state_t;

typedef struct {
    double lat;          // Градуси WGS-84
    double lon;          // Градуси WGS-84
    float alt;           // Метри (відносна висота)
    float v_cruise;      // м/с
    float r_acc;         // Радіус кулі досягнення (м)
    float t_hold;        // Час затримки в точці (с)
    float yaw_param;     // Цільовий кут рискання (рад)
    yaw_mode_t yaw_mode; // Режим узгодження курсу
    uint16_t action_id;  // Ідентифікатор команди (наприклад 100 = фотознімок)
    bool fly_through;    // true = плавний обліт, false = зупинка
} waypoint_t;

typedef struct {
    float x; // North (м)
    float y; // East (м)
    float z; // Down (м)
} vec3_t;

typedef struct {
    vec3_t pos;          // Поточна позиція в NED
    vec3_t vel;          // Поточна швидкість в NED
    float yaw;           // Поточний кут рискання (рад)
} vehicle_state_t;

typedef struct {
    vec3_t pos_target;   // Цільова позиція (м)
    vec3_t vel_target;   // Бажаний вектор швидкості (м/с)
    float yaw_target;    // Бажаний кут рискання (рад)
    bool trigger_action; // Сигнал виконання дії
} nav_setpoint_t;

typedef struct {
    const waypoint_t *waypoints;
    size_t count;
    size_t current_index;
    size_t prev_index;

    double home_lat;
    double home_lon;
    float home_alt;

    seq_state_t state;
    float hold_timer;
    vec3_t roi_pos;
    bool roi_active;

    vec3_t curr_wp_ned;
    vec3_t prev_wp_ned;
    vec3_t segment_unit_in;
} mission_sequencer_t;

static float wrap_pi(float angle) {
    while (angle > M_PI_F)  angle -= 2.0f * M_PI_F;
    while (angle < -M_PI_F) angle += 2.0f * M_PI_F;
    return angle;
}

static vec3_t geo_to_ned(double lat, double lon, float alt,
                         double home_lat, double home_lon, float home_alt) {
    double d_lat = (lat - home_lat) * DEG_TO_RAD_F;
    double d_lon = (lon - home_lon) * DEG_TO_RAD_F;
    double lat_rad = home_lat * DEG_TO_RAD_F;

    vec3_t ned;
    ned.x = (float)(d_lat * CONSTANTS_RADIUS_OF_EARTH);
    ned.y = (float)(d_lon * CONSTANTS_RADIUS_OF_EARTH * cos(lat_rad));
    ned.z = -(alt - home_alt);
    return ned;
}

static float vec3_dist_2d(vec3_t a, vec3_t b) {
    float dx = a.x - b.x;
    float dy = a.y - b.y;
    return sqrtf(dx * dx + dy * dy);
}

static float vec3_dot(vec3_t a, vec3_t b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

void sequencer_init(mission_sequencer_t *seq, const waypoint_t *wps, size_t count,
                    double home_lat, double home_lon, float home_alt) {
    seq->waypoints = wps;
    seq->count = count;
    seq->current_index = 0;
    seq->prev_index = 0;
    seq->home_lat = home_lat;
    seq->home_lon = home_lon;
    seq->home_alt = home_alt;
    seq->state = (count > 0) ? SEQ_STATE_NAVIGATING : SEQ_STATE_IDLE;
    seq->hold_timer = 0.0f;
    seq->roi_active = false;

    if (count > 0) {
        seq->prev_wp_ned = geo_to_ned(home_lat, home_lon, home_alt, home_lat, home_lon, home_alt);
        seq->curr_wp_ned = geo_to_ned(wps[0].lat, wps[0].lon, wps[0].alt, home_lat, home_lon, home_alt);
        
        vec3_t seg_in = {
            seq->curr_wp_ned.x - seq->prev_wp_ned.x,
            seq->curr_wp_ned.y - seq->prev_wp_ned.y,
            seq->curr_wp_ned.z - seq->prev_wp_ned.z
        };
        float len = sqrtf(vec3_dot(seg_in, seg_in));
        if (len > 0.001f) {
            seq->segment_unit_in.x = seg_in.x / len;
            seq->segment_unit_in.y = seg_in.y / len;
            seq->segment_unit_in.z = seg_in.z / len;
        } else {
            seq->segment_unit_in = (vec3_t){1.0f, 0.0f, 0.0f};
        }
    }
}

void sequencer_set_roi(mission_sequencer_t *seq, double lat, double lon, float alt) {
    seq->roi_pos = geo_to_ned(lat, lon, alt, seq->home_lat, seq->home_lon, seq->home_alt);
    seq->roi_active = true;
}

void sequencer_clear_roi(mission_sequencer_t *seq) {
    seq->roi_active = false;
}

static bool check_waypoint_reached(const mission_sequencer_t *seq, const vehicle_state_t *veh, const waypoint_t *wp) {
    float dist_xy = vec3_dist_2d(veh->pos, seq->curr_wp_ned);
    float dist_z = fabsf(veh->pos.z - seq->curr_wp_ned.z);

    // 1. Умова входу в кулю досягнення
    if (dist_xy <= wp->r_acc && dist_z <= (wp->r_acc * 1.5f)) {
        return true;
    }

    // 2. Умова перетину нормальної площини прольоту (Passing Plane)
    vec3_t d_target = {
        veh->pos.x - seq->curr_wp_ned.x,
        veh->pos.y - seq->curr_wp_ned.y,
        veh->pos.z - seq->curr_wp_ned.z
    };
    float s_pass = vec3_dot(d_target, seq->segment_unit_in);

    // Дозволяємо перетин площини, якщо бічне зміщення не перевищує 3-кратний радіус кулі
    if (s_pass >= 0.0f && dist_xy <= (wp->r_acc * 3.0f)) {
        return true;
    }

    return false;
}

nav_setpoint_t sequencer_tick(mission_sequencer_t *seq, const vehicle_state_t *veh, float dt) {
    nav_setpoint_t sp = {0};
    sp.pos_target = seq->curr_wp_ned;
    sp.trigger_action = false;

    if (seq->state == SEQ_STATE_IDLE || seq->state == SEQ_STATE_MISSION_DONE) {
        sp.vel_target = (vec3_t){0.0f, 0.0f, 0.0f};
        sp.yaw_target = veh->yaw;
        return sp;
    }

    const waypoint_t *curr_wp = &seq->waypoints[seq->current_index];

    switch (seq->state) {
    case SEQ_STATE_NAVIGATING: {
        bool reached = check_waypoint_reached(seq, veh, curr_wp);

        if (reached) {
            if (curr_wp->fly_through && curr_wp->t_hold <= 0.001f) {
                // Плавний обліт без зупинки: одразу перемикаємо на наступну точку
                seq->state = SEQ_STATE_ADVANCE_WP;
            } else {
                // Зупинка в точці: скидаємо швидкість і запускаємо таймер
                seq->state = SEQ_STATE_LOITER_HOLD;
                seq->hold_timer = curr_wp->t_hold;
            }
        } else {
            // Напрям швидкості вздовж лінії до цілі
            vec3_t dir = {
                seq->curr_wp_ned.x - veh->pos.x,
                seq->curr_wp_ned.y - veh->pos.y,
                seq->curr_wp_ned.z - veh->pos.z
            };
            float dist = sqrtf(vec3_dot(dir, dir));
            if (dist > 0.001f) {
                sp.vel_target.x = (dir.x / dist) * curr_wp->v_cruise;
                sp.vel_target.y = (dir.y / dist) * curr_wp->v_cruise;
                sp.vel_target.z = (dir.z / dist) * curr_wp->v_cruise;
            }
        }
        break;
    }

    case SEQ_STATE_LOITER_HOLD: {
        sp.vel_target = (vec3_t){0.0f, 0.0f, 0.0f};
        seq->hold_timer -= dt;
        if (seq->hold_timer <= 0.0f) {
            seq->state = (curr_wp->action_id != 0) ? SEQ_STATE_EXEC_ACTION : SEQ_STATE_ADVANCE_WP;
        }
        break;
    }

    case SEQ_STATE_EXEC_ACTION: {
        sp.vel_target = (vec3_t){0.0f, 0.0f, 0.0f};
        sp.trigger_action = true;
        // Після генерації імпульсу дії переходимо до наступної точки
        seq->state = SEQ_STATE_ADVANCE_WP;
        break;
    }

    case SEQ_STATE_ADVANCE_WP: {
        seq->prev_index = seq->current_index;
        seq->current_index++;

        if (seq->current_index >= seq->count) {
            seq->state = SEQ_STATE_MISSION_DONE;
            sp.vel_target = (vec3_t){0.0f, 0.0f, 0.0f};
        } else {
            seq->prev_wp_ned = seq->curr_wp_ned;
            const waypoint_t *next_wp = &seq->waypoints[seq->current_index];
            seq->curr_wp_ned = geo_to_ned(next_wp->lat, next_wp->lon, next_wp->alt,
                                          seq->home_lat, seq->home_lon, seq->home_alt);

            vec3_t seg = {
                seq->curr_wp_ned.x - seq->prev_wp_ned.x,
                seq->curr_wp_ned.y - seq->prev_wp_ned.y,
                seq->curr_wp_ned.z - seq->prev_wp_ned.z
            };
            float len = sqrtf(vec3_dot(seg, seg));
            if (len > 0.001f) {
                seq->segment_unit_in.x = seg.x / len;
                seq->segment_unit_in.y = seg.y / len;
                seq->segment_unit_in.z = seg.z / len;
            }
            seq->state = SEQ_STATE_NAVIGATING;
        }
        break;
    }

    default:
        break;
    }

    // Розрахунок цільового кута рискання (Yaw Coordination)
    if (seq->roi_active) {
        float dx = seq->roi_pos.x - veh->pos.x;
        float dy = seq->roi_pos.y - veh->pos.y;
        sp.yaw_target = atan2f(dy, dx);
    } else {
        switch (curr_wp->yaw_mode) {
        case YAW_MODE_FIXED:
            sp.yaw_target = curr_wp->yaw_param;
            break;
        case YAW_MODE_ROI:
            sp.yaw_target = atan2f(seq->roi_pos.y - veh->pos.y, seq->roi_pos.x - veh->pos.x);
            break;
        case YAW_MODE_ALONG_TRACK:
        default: {
            float dx = seq->curr_wp_ned.x - veh->pos.x;
            float dy = seq->curr_wp_ned.y - veh->pos.y;
            if (sqrtf(dx * dx + dy * dy) > 0.5f) {
                sp.yaw_target = atan2f(dy, dx);
            } else {
                sp.yaw_target = veh->yaw;
            }
            break;
        }
        }
    }

    return sp;
}
```
```cpp
#include <cmath>
#include <cstdint>
#include <numbers>
#include <optional>
#include <span>
#include <vector>

namespace navigation {

constexpr float EarthRadiusMeters = 6371000.0f;

enum class YawMode : uint8_t {
    AlongTrack = 0,
    Fixed      = 1,
    Roi        = 2
};

enum class SequencerState : uint8_t {
    Idle,
    Navigating,
    LoiterHold,
    ExecuteAction,
    AdvanceWaypoint,
    MissionDone
};

struct Waypoint {
    double latitudeDeg;
    double longitudeDeg;
    float altitudeM;
    float cruiseSpeedMs{5.0f};
    float acceptanceRadiusM{2.0f};
    float holdTimeSec{0.0f};
    float yawTargetRad{0.0f};
    YawMode yawMode{YawMode::AlongTrack};
    uint16_t actionId{0};
    bool flyThrough{true};
};

struct Vector3D {
    float x{0.0f}; // North (м)
    float y{0.0f}; // East (м)
    float z{0.0f}; // Down (м)

    [[nodiscard]] constexpr float dot(const Vector3D& other) const noexcept {
        return x * other.x + y * other.y + z * other.z;
    }

    [[nodiscard]] float length() const noexcept {
        return std::sqrt(dot(*this));
    }

    [[nodiscard]] float distance2D(const Vector3D& other) const noexcept {
        const float dx = x - other.x;
        const float dy = y - other.y;
        return std::sqrt(dx * dx + dy * dy);
    }

    [[nodiscard]] Vector3D normalized() const noexcept {
        const float len = length();
        return len > 0.001f ? Vector3D{x / len, y / len, z / len} : Vector3D{1.0f, 0.0f, 0.0f};
    }
};

struct VehicleState {
    Vector3D position;
    Vector3D velocity;
    float yawRad{0.0f};
};

struct NavigationSetpoint {
    Vector3D targetPosition;
    Vector3D targetVelocity;
    float targetYawRad{0.0f};
    bool triggerAction{false};
};

class MissionSequencer {
public:
    MissionSequencer(std::span<const Waypoint> missionPlan,
                     double homeLatDeg, double homeLonDeg, float homeAltM)
        : m_plan(missionPlan),
          m_homeLat(homeLatDeg),
          m_homeLon(homeLonDeg),
          m_homeAlt(homeAltM),
          m_state(missionPlan.empty() ? SequencerState::Idle : SequencerState::Navigating) {
        if (!m_plan.empty()) {
            m_prevWpNed = geoToNed(m_homeLat, m_homeLon, m_homeAlt);
            m_currWpNed = geoToNed(m_plan[0].latitudeDeg, m_plan[0].longitudeDeg, m_plan[0].altitudeM);
            m_segmentUnitIn = (m_currWpNed.distance2D(m_prevWpNed) > 0.001f)
                                  ? Vector3D{m_currWpNed.x - m_prevWpNed.x,
                                             m_currWpNed.y - m_prevWpNed.y,
                                             m_currWpNed.z - m_prevWpNed.z}.normalized()
                                  : Vector3D{1.0f, 0.0f, 0.0f};
        }
    }

    void setRegionOfInterest(double latDeg, double lonDeg, float altM) noexcept {
        m_roiNed = geoToNed(latDeg, lonDeg, altM);
    }

    void clearRegionOfInterest() noexcept {
        m_roiNed.reset();
    }

    [[nodiscard]] SequencerState currentState() const noexcept { return m_state; }
    [[nodiscard]] size_t currentWaypointIndex() const noexcept { return m_currentIndex; }

    NavigationSetpoint update(const VehicleState& vehicle, float dtSec) {
        NavigationSetpoint setpoint{};
        setpoint.targetPosition = m_currWpNed;

        if (m_state == SequencerState::Idle || m_state == SequencerState::MissionDone) {
            setpoint.targetVelocity = Vector3D{0.0f, 0.0f, 0.0f};
            setpoint.targetYawRad = vehicle.yawRad;
            return setpoint;
        }

        const auto& currentWp = m_plan[m_currentIndex];

        switch (m_state) {
        case SequencerState::Navigating: {
            if (isWaypointReached(vehicle, currentWp)) {
                if (currentWp.flyThrough && currentWp.holdTimeSec <= 0.001f) {
                    m_state = SequencerState::AdvanceWaypoint;
                } else {
                    m_state = SequencerState::LoiterHold;
                    m_holdTimer = currentWp.holdTimeSec;
                }
            } else {
                const Vector3D toTarget{
                    m_currWpNed.x - vehicle.position.x,
                    m_currWpNed.y - vehicle.position.y,
                    m_currWpNed.z - vehicle.position.z
                };
                const float dist = toTarget.length();
                if (dist > 0.001f) {
                    const float speed = currentWp.cruiseSpeedMs;
                    setpoint.targetVelocity = Vector3D{
                        (toTarget.x / dist) * speed,
                        (toTarget.y / dist) * speed,
                        (toTarget.z / dist) * speed
                    };
                }
            }
            break;
        }

        case SequencerState::LoiterHold: {
            setpoint.targetVelocity = Vector3D{0.0f, 0.0f, 0.0f};
            m_holdTimer -= dtSec;
            if (m_holdTimer <= 0.0f) {
                m_state = (currentWp.actionId != 0) ? SequencerState::ExecuteAction
                                                    : SequencerState::AdvanceWaypoint;
            }
            break;
        }

        case SequencerState::ExecuteAction: {
            setpoint.targetVelocity = Vector3D{0.0f, 0.0f, 0.0f};
            setpoint.triggerAction = true;
            m_state = SequencerState::AdvanceWaypoint;
            break;
        }

        case SequencerState::AdvanceWaypoint: {
            m_currentIndex++;
            if (m_currentIndex >= m_plan.size()) {
                m_state = SequencerState::MissionDone;
                setpoint.targetVelocity = Vector3D{0.0f, 0.0f, 0.0f};
            } else {
                m_prevWpNed = m_currWpNed;
                const auto& nextWp = m_plan[m_currentIndex];
                m_currWpNed = geoToNed(nextWp.latitudeDeg, nextWp.longitudeDeg, nextWp.altitudeM);

                const Vector3D seg{
                    m_currWpNed.x - m_prevWpNed.x,
                    m_currWpNed.y - m_prevWpNed.y,
                    m_currWpNed.z - m_prevWpNed.z
                };
                m_segmentUnitIn = seg.normalized();
                m_state = SequencerState::Navigating;
            }
            break;
        }

        default:
            break;
        }

        setpoint.targetYawRad = computeTargetYaw(vehicle, currentWp);
        return setpoint;
    }

private:
    [[nodiscard]] Vector3D geoToNed(double latDeg, double lonDeg, float altM) const noexcept {
        constexpr double DegToRad = std::numbers::pi / 180.0;
        const double dLat = (latDeg - m_homeLat) * DegToRad;
        const double dLon = (lonDeg - m_homeLon) * DegToRad;
        const double latRad = m_homeLat * DegToRad;

        return Vector3D{
            static_cast<float>(dLat * EarthRadiusMeters),
            static_cast<float>(dLon * EarthRadiusMeters * std::cos(latRad)),
            -(altM - m_homeAlt)
        };
    }

    [[nodiscard]] bool isWaypointReached(const VehicleState& veh, const Waypoint& wp) const noexcept {
        const float distXY = veh.position.distance2D(m_currWpNed);
        const float distZ = std::abs(veh.position.z - m_currWpNed.z);

        // 1. Перевірка сфери досягнення
        if (distXY <= wp.acceptanceRadiusM && distZ <= (wp.acceptanceRadiusM * 1.5f)) {
            return true;
        }

        // 2. Перевірка площини прольоту (Passing Plane)
        const Vector3D dTarget{
            veh.position.x - m_currWpNed.x,
            veh.position.y - m_currWpNed.y,
            veh.position.z - m_currWpNed.z
        };
        const float sPass = dTarget.dot(m_segmentUnitIn);

        return (sPass >= 0.0f) && (distXY <= (wp.acceptanceRadiusM * 3.0f));
    }

    [[nodiscard]] float computeTargetYaw(const VehicleState& veh, const Waypoint& wp) const noexcept {
        if (m_roiNed.has_value()) {
            const float dx = m_roiNed->x - veh.position.x;
            const float dy = m_roiNed->y - veh.position.y;
            return std::atan2(dy, dx);
        }

        switch (wp.yawMode) {
        case YawMode::Fixed:
            return wp.yawTargetRad;
        case YawMode::Roi:
            if (m_roiNed.has_value()) {
                return std::atan2(m_roiNed->y - veh.position.y, m_roiNed->x - veh.position.x);
            }
            [[fallthrough]];
        case YawMode::AlongTrack:
        default: {
            const float dx = m_currWpNed.x - veh.position.x;
            const float dy = m_currWpNed.y - veh.position.y;
            return (std::sqrt(dx * dx + dy * dy) > 0.5f) ? std::atan2(dy, dx) : veh.yawRad;
        }
        }
    }

    std::span<const Waypoint> m_plan;
    double m_homeLat{0.0};
    double m_homeLon{0.0};
    float m_homeAlt{0.0f};

    size_t m_currentIndex{0};
    SequencerState m_state{SequencerState::Idle};
    float m_holdTimer{0.0f};

    Vector3D m_currWpNed{};
    Vector3D m_prevWpNed{};
    Vector3D m_segmentUnitIn{1.0f, 0.0f, 0.0f};
    std::optional<Vector3D> m_roiNed{std::nullopt};
};

} // namespace navigation
```
:::

## Крайові випадки та виробничі пастки

Під час експлуатації автономних комплексів розробники стикаються з набором критичних граничних умов, які вимагають окремого захисту в коді секвенсера:

### 1. Модифікація плану на льоту (Dynamic Mission Update)
Оператор станції може передати команду `MAV_CMD_DO_SET_MISSION_CURRENT` або завантажити новий план просто посеред виконання відрізка. Якщо секвенсер зберігає старі локальні вектори сегмента, перехід на нову точку спричинить стрибок цільового прискорення. Правильне опрацювання вимагає повного скидання попередньої точки на поточну позицію апарата: `prev_wp_ned = vehicle_pos` та миттєвого перерахунку нормалей.

### 2. Зациклення через цикли переходів (`MAV_CMD_DO_JUMP`)
Команда переходу дозволяє організувати циклічний прохід групи точок `k` разів. Секвенсер зобов'язаний тримати локальний лічильник ітерацій для кожного джампа в масиві. Якщо лічильник не декрементується або відсутній захист від нульової кількості повторів, прошивка зависає в нескінченному переході без можливості дійти до команди посадки.

### 3. Стрибок оцінки стану EKF (Position Jump)
За раптового перемикання супутникових сузір'їв або відновлення сигналу GPS після глушіння фільтр Калмана (EKF) може змістити поточну оцінку координат `P` на десятки метрів за один такт. Якщо в цей момент дрон був на підльоті до точки, стрибок може штучно перекинути його за площину прольоту `s_pass > 0`, спричинивши помилкове передчасне зарахування точки. Для захисту запроваджують фільтрацію інновацій або перевірку неперервності швидкості.

### 4. Пріоритет геозон (Geofence Breach)
Якщо траєкторія між точками `W[k-1]` та `W[k]` внаслідок зносу вітром перетинає межу циліндричної чи полігональної забороненої зони, модуль безпеки Geofence зобов'язаний негайно перехопити керування у секвенсера місії, перевівши дрон у режим зависання (Hold/Brake) або повернення (RTL), заблокувавши подальший перехід по масиву точок.

### 5. Сингулярність прямовисного прольоту над ROI
Коли дрон у режимі наведення на точку інтересу пролітає безпосередньо над самою точкою `T_roi`, горизонтальна відстань `d_ground = √(Δx² + Δy²)` прямує до нуля. Розрахунок кута рискання `atan2(Δy, Δx)` стає чисельно нестійким, а підвіс камери намагається миттєво розвернутися на 180° при переході через точку надиру (Nadir Point). Секвенсер захищає систему, заморожуючи курс за умови `d_ground < 2.0 м` та плавно переходячи на утримання останнього валідного кута.

### 6. Відновлення місії після переривання (Mission Resume)
Якщо місія була перервана оператором у ручному режимі (наприклад, для обльоту раптової перешкоди) або спрацював короткочасний Failsafe, повернення до місії не повинно вести дрон на початок уже виконаного багатометрового відрізка. Алгоритм відновлення проєктує поточне положення дрона ортогонально на активний відрізок `W[k-1] → W[k]` і підключає наведення з найближчої точки прямої, зберігаючи цілісність плану без зайвих перельотів.
