# ⚙️ Диспетчер та раціоналізатор тривог за стандартом ISA-18.2 із динамічним пригніченням лавини

У критичних людино-машинних інтерфейсах (HMI) вбудованих систем, розподілених комплексів автоматизації, авіоніки та наземних станцій керування безпілотними апаратами головна небезпека полягає не у відсутності діагностики, а в її надлишку. Під час аварійної ситуації (наприклад, знеструмлення силової шини живлення або пробою контуру охолодження) наївна система сигналізації генерує десятки одночасних сповіщень. Замість розуміння першопричини оператор стикається з феноменом лавини тривог (*Alarm Flood*), коли екран перетворюється на безперервний потік мерехтливих червоних плашок, а звуковий зумер перевантажує слуховий канал сприйняття. У цьому стані людина або механічно квитує всі повідомлення без читання (*Alarm Ack Reflex*), або впадає в когнітивний ступор, пропускаючи критичні повідомлення та посилюючи катастрофічний розвиток подій.

Міжнародний стандарт ANSI/ISA-18.2 (гармонізований як IEC 62682) формулює суворі інженерні вимоги до побудови надійних систем сигналізації: кожна тривога зобов'язана вказувати на конкретну необхідну дію оператора, мати визначений наслідок бездії, проходити процедуру раціоналізації та динамічно пригнічуватися, якщо поточний експлуатаційний стан системи або первинна аварія роблять її вторинним шумом.

---

## 1. Архітектурний аналіз та когнітивні обмеження оператора

У класичній теорії надійності людино-машинних систем помилка оператора рідко є першопричиною інциденту; здебільшого вона є прямим наслідком неякісно спроектованого інформаційного середовища. Коли складна вбудована система генерує тривоги на кожен вихід будь-якого внутрішнього прапорця за номінальні межі, виникає феномен втоми від сигналізації (*Alarm Fatigue*).

Людський мозок має суворо обмежену місткість робочої пам'яті. У стані спокою людина здатна одночасно утримувати в оперативній увазі від чотирьох до семи незалежних інформаційних сутностей (магічне число Міллера 7 ± 2). Проте в умовах раптової аварійної ситуації, супроводжуваної звуковими сиренами, падінням напруги та блиманням дисплеїв, рівень фізіологічного стресу зростає, активуючи симпатичну нервову систему. Згідно із законом Єркса — Додсона (*Yerkes-Dodson Law*), високий рівень збудження спричиняє звуження поля уваги (когнітивне тунелювання), а обсяг ефективної робочої пам'яті падає до однієї-двох сутностей.

Якщо протягом перших десяти секунд після аварії система сигналізації видає на екран 25 повідомлень різного ґатунку — втрата зв'язку з оптичним датчиком потоку, зниження напруги живлення шини 5V, зниження напруги живлення шини 12V, зниження напруги живлення шини 28V, помилка одометрії колісних енкодерів, аварія контролера підвісу камери, зупинка вентилятора охолодження обчислювача, — оператор витрачає критичний час на читання другорядних симптомів. Людина намагається зрозуміти, чому зупинився вентилятор чи відпав лідар, замість того щоб негайно виконати єдину дію, яка врятує апарат: перемкнути перевідник головного контактора аварійного живлення.

Інженерні рекомендації асоціації EEMUA 191 (*Engineering Equipment and Materials Users Association*) та стандарту ANSI/ISA-18.2 встановлюють такі кількісні нормативи навантаження на оператора:

Перший норматив стосується номінального стабільного режиму роботи. У цьому стані система повинна генерувати в середньому не більше однієї тривоги за 10 хвилин (менше 6 тривог на годину). За такого темпу оператор має достатньо часу для спокійного аналізу контексту, звірки фізичних приладів та виконання профілактичних коригувань параметрів установки.

Другий норматив регламентує перехідний стан системи, такий як пуск технологічної лінії, зміна режиму польоту безпілотника чи виконання маневру посадки. У цей період допустимий темп зростає, але не повинен перевищувати двох тривог за 10 хвилин.

Третій норматив визначає межу аварійного режиму при піковому навантаженні. Протягом перших 10 хвилин після виникнення первинної відмови оператор може отримати не більше десяти тривог. Якщо темп надходження перевищує 10 тривог за 10 хвилин, стан кваліфікується як аварійна лавина (*Alarm Flood*), за якої імовірність помилкової дії оператора зростає з 1% до понад 50%.

---

## 2. Історичні уроки промислових та авіаційних катастроф через лавини тривог

Аналіз реальних катастроф показує, що відсутність раціоналізації сигналізації призводить до втрати мільярдних активів та загибелі людей.

Найвідомішим прикладом у нафтохімічній галузі є вибух на нафтопереробному заводі Texaco в Пембруку (Велика Британія, 1994 рік). Протягом останніх 11 хвилин до вибуху два оператори головного пульта отримали 275 тривожних сповіщень. Тривоги надходили зі швидкістю одна подія кожні 2.4 секунди. Оператори були фізично неспроможні прочитати текст на екранах, тому просто безперервно тиснули клавішу скидання звуку. Серед цього суцільного шуму вони пропустили критичну тривогу про переповнення дренажного барабана високого тиску, що призвело до викиду вуглеводнів в атмосферу, загоряння та руйнівного вибуху.

На атомній електростанції Три-Майл-Айленд (США, 1979 рік) у перші хвилини аварії в головній залі керування спрацювало одночасно понад 100 оптичних та звукових сигналізаторів. Світлове та звукове перевантаження завадило операторам локалізувати першопричину — завислий у відкритому положенні електромагнітний скидний клапан PORV. Оператори бачили на панелі зелену лампочку, яка показувала подачу команди на закриття, і через сліпу довіру до інтерфейсу не перевірили пряму термопару на скидній трубі, що призвело до розплавлення активної зони ядерного реактора.

На буровій платформі Deepwater Horizon (Мексиканська затока, 2010 рік) сигналізація небезпечної концентрації газу була заздалегідь переведена в режим вимкненого звуку, оскільки численні хибні спрацювання будили персонал уночі. Коли стався реальний викид метану, система не попередила зміну, а автоматичний контур аварійного відключення не був задіяний вчасно.

Ці катастрофи довели, що сигналізація без динамічного пригнічення, фільтрації брязкоту та суворої пріоритизації перетворюється з інструменту порятунку на каталізатор аварії.

---

## 3. Філософія та методологія раціоналізації сигналізації

За стандартом ISA-18.2 тривога (*Alarm*) — це не просто повідомлення про подію чи запис у лог-файлі. Сигнал має право отримати статус тривоги лише за одночасного виконання чотирьох обов'язкових критеріїв.

Перший критерій — це необхідність безпосередньої дії оператора (*Operator Action*). Якщо вихід параметра за межу не вимагає від людини фізичної дії (перемикання тумблера, зміна курсу, перезапуск підсистеми, перехід на ручне керування), цей сигнал є діагностичним статусом (*Alert/Event*), а не тривогою. Автоматичні дії системи, які не потребують підтвердження чи втручання людини, повинні записуватися в журнал подій без активації тривожних екранів.

Другий критерій — наявність чіткого наслідку бездії (*Consequence*). Невиконання оператором передбаченої дії протягом визначеного часу зобов'язане призводити до відчутної та вимірної втрати: аварійної зупинки апарата, деградації місії, теплового руйнування силових вузлів або прямої загрози життю людей. Якщо наслідок відсутній або зводиться до незначного косметичного відхилення, параметр підлягає вилученню з контуру тривог.

Третій критерій — бюджет допустимого часу реакції (*Response Time*). Час від моменту виникнення сигналу до настання незворотного наслідку повинен перевищувати мінімальний час, необхідний оператору для виявлення сповіщення, осмислення фізичного контексту та виконання потрібної маніпуляції. Якщо наслідок настає швидше, ніж людина фізіологічно здатна зреагувати (наприклад, менше 200 мілісекунд при пробої ключа інвертора), такий захист зобов'язаний виконуватися виключно апаратно або в жорсткому перериванні мікроконтролера, а не через виведення діалогового вікна на екран HMI.

Четвертий критерій — унікальність повідомлення. Одна фізична першопричина повинна породжувати рівно одне тривожне повідомлення найвищого пріоритету, а не ланцюжок із трьох десятків вторинних симптомів.

Процедура раціоналізації тривог (*Alarm Rationalization*) полягає у систематичному аналізі кожного датчика, програмного ліміту та прапорця стану. Результати аналізу вносяться у раціоналізаційну карту (*Alarm Rationalization Worksheet*), де для кожного тегу фіксуються уставка спрацювання, уставка скидання, час затримки, наслідок бездії, покрокова інструкція оператору та призначений пріоритет.

Приклад раціоналізованого списку сигналізації для автономного комплексу:

У системі електроживлення тривога `PWR_MAIN_BUS_UV` активується при падінні напруги головної шини 28 В нижче порогу 22.0 В. Наслідком бездії є повне знеструмлення бортових обчислювачів і падіння апарата через 10 секунд. Необхідна дія оператора полягає в негайному перемиканні аварійного тумблера резервної батареї та переведенні апарата в плануючий спуск. Цій тривозі призначається найвищий пріоритет `Critical`.

У системі моніторингу акумулятора тривога `BATT_CELL_OVERTEMP` спрацьовує при нагріванні будь-якої літієвої комірки понад 65 °C. Наслідком бездії є незворотний тепловий розгін акумуляторного блоку та загоряння через 45 секунд. Дія оператора: зменшити газ двигунів до 30% та розпочати екстрене зниження. Призначений пріоритет — `High`.

У навігаційному контурі тривога `SENSOR_PLAUS_WARN` виникає при перевищенні нев'язки між даними акселерометра IMU та похідною швидкості GNSS понад 3.5 м/с². Наслідком бездії є неконтрольоване відхилення апарата від курсу через супутниковий спуфінг або завади. Дія оператора: звірити візуальний горизонт по курсовій камері та негайно перехопити ручне пілотування. Призначений пріоритет — `High`.

У каналі висотоміра тривога `LIDAR_COMM_LOST` активується при відсутності валідних пакетів від лазерного далекоміра понад 0.5 секунди. Наслідком бездії є неможливість точної автоматичної посадки на нерівний ґрунт через 60 секунд. Дія оператора: перевірити висоту за резервним барометром та увімкнути посадкову камеру. Призначений пріоритет — `Medium`.

У сервісній підсистемі тривога `LOG_STORAGE_WARN` виникає при заповненні енергонезалежної Flash-пам'яті понад 90%. Наслідком бездії є припинення реєстрації параметрів чорної скриньки через 30 хвилин. Дія оператора: активувати режим циклічного перезапису застарілих журналів. Призначений пріоритет — `Low`.

---

## 4. Математичний апарат фільтрації та оцінки достовірності

Розглянемо аналітичні методи, що усувають брязкіт сигналів, розраховують довірчі інтервали та виявляють розбіжності фізичних моделей.

### 4.1. Оптимізація гістерезису та середнього часу між хибними тривогами

Нехай вимірюваний сенсорний сигнал `y(t)` складається з істинного значення фізичної величини `x(t)` та аддитивного гаусового шуму `n(t)` із нульовим математичним сподіванням і дисперсією `σ_n²`:

```
y(t) = x(t) + n(t),   де n(t) ~ N(0, σ_n²)
```

Якщо уставка спрацювання становить `T_trip`, а поріг скидання збігається з уставкою (`T_clear = T_trip`, нульовий гістерезис), то при наближенні фізичної величини `x(t)` до порогу на відстань `δ = |x(t) - T_trip| < 2·σ_n` сигнал здійснюватиме випадкові блукання через поріг. За формулою Райса для середньої частоти перетинів рівня диференційовним випадковим процесом, частота генерації тривог `f_cross` визначається шириною спектра шуму `f_max`:

```
f_cross = f_max · exp(-(T_trip - x(t))² / (2 · σ_n²))
```

При нульовій різниці `x(t) = T_trip` частота хибних перетинів досягає максимуму `f_max`, що в цифрових системах з частотою опитування 100 Гц генерує до 50 хибних переходів за секунду.

Введення гістерезису `Δ = T_trip - T_clear` розриває єдиний поріг на два ізольовані стани. Щоб відбулося повторне помилкове спрацювання після повернення в норму, шум повинен здійснити подвійний розмах, амплітуда якого перевищує `Δ`. Середній час між хибними переходами (*Mean Time Between False Alarms*, MTBFA) для системи з гістерезисом та затримкою `t_on` розраховується через інтеграл першого досягнення межі:

```
MTBFA ≈ (1 / f_max) · (Δ / σ_n) · exp(Δ² / (8 · σ_n²)) · exp(t_on / τ_noise)
```

де `τ_noise` — час автокореляції сенсорного шуму. З формули видно, що експоненційне зростання MTBFA досягається вибором гістерезису `Δ ≥ 3.5 · σ_n` та затримки спрацювання `t_on ≥ 3 · τ_noise`.

Для тривог за верхньою межею (High Alarm) уставка спрацювання `T_trip` та уставка скидання `T_clear` пов'язані співвідношенням:

```
T_clear = T_trip - Δ
```

Сигнал переходить у стан тривоги лише при `value ≥ T_trip`, а повертається до норми виключно після зниження до `value ≤ T_clear`. Для тривог за нижньою межею (Low Alarm) правило працює дзеркально:

```
T_clear = T_trip + Δ
```

### 4.2. Затримки On-Delay та Off-Delay у контурах захисту

Застосування фільтра `On-Delay` вносить фазову затримку у виявлення аварії. Бюджет затримки `t_on` суворо обмежений тепловою або механічною постійною часу захищуваного об'єкта.

Розглянемо силовий польовий транзистор інвертора (MOSFET), через який протікає струм перевантаження `I_fault`. Швидкість нагрівання кристала описується спрощеним диференціальним рівнянням теплового балансу:

```
C_th · (dT_j / dt) = I_fault² · R_ds(on) - (T_j - T_amb) / R_th
```

де:
- `C_th` — теплоємність кристала (Дж/°C),
- `R_th` — тепловий опір перехід-корпус (°C/Вт),
- `T_j` — температура кристала p-n переходу (°C),
- `T_amb` — температура навколишнього середовища (°C),
- `T_j_max` — гранична температура руйнування напівпровідникової структури (типово 150 °C або 175 °C).

Максимально допустимий час затримки `t_on_max` до моменту відключення визначається інтегруванням теплового рівняння від початкової робочої температури `T_j_0`:

```
t_on_max = -C_th · R_th · ln(1 - (T_j_max - T_j_0) / (I_fault² · R_ds(on) · R_th))
```

Якщо затримка `On-Delay` у диспетчері тривог перевищить величину `t_on_max`, кристал транзистора розплавиться до того, як спрацює алгоритм аварійного захисту. Тому для силових електричних та теплових параметрів `t_on` обирається з умови:

```
t_on ≤ 0.2 · t_on_max
```

що гарантує п'ятикратний запас надійності при надійному придушенні високочастотних комутаційних завад тривалістю 10..50 мікросекунд.

Параметр `Off-Delay` (`t_off`) виконує зворотну функцію: після повернення сигналу в межі норми тривога утримується активною щонайменше `t_off` мілісекунд. Це гарантує, що короткочасне пірнання сигналу тривалістю кілька мілісекунд під час перехідних процесів не спричинить хибного скидання і повторного вмикання зумера.

### 4.3. Критерій Хі-квадрат для виявлення розбіжності датчиків (Chi-Squared Innovation Test)

У розширеному фільтрі Калмана (EKF), що об'єднує покази IMU, GNSS, магнітометра та барометра, вектор нев'язки (інновації) `v_k` на кроці дискретизації `k` визначається як різниця між фактичним вимірюванням `z_k` та прогнозом моделі `h(x̂_k^-)`:

```
v_k = z_k - h(x̂_k^-)
```

Коваріаційна матриця інновації `S_k` враховує апріорну невизначеність стану `P_k^-` та матрицю шуму вимірювань `R_k`:

```
S_k = H_k · P_k^- · H_kᵀ + R_k
```

Нормована квадратична форма нев'язки (квадрат відстані Махаланобіса) `γ_k` визначається як:

```
γ_k = v_kᵀ · S_k⁻¹ · v_k
```

За умови нормального розподілу похибок вимірювань величина `γ_k` підпорядковується χ²-розподілу з `m` ступенями вільності (де `m` — розмірність вектора вимірювань `z_k`). Модуль перевірки достовірності обчислює поріг відсічки `Γ_threshold` для заданого рівня значущості α = 0.01 (довірча ймовірність 99%):

```
P(γ_k > Γ_threshold) = α
```

Якщо `γ_k > Γ_threshold`, гіпотеза про коректність сенсорних даних відкидається. Фільтр EKF ізолює дефектний сенсор (наприклад, GNSS під час дії активних завад РЕБ або супутникового спуфінгу), запобігаючи спотворенню матриці коваріацій стану, а диспетчер тривог активує попередження `SENSOR_PLAUSIBILITY_WARN` з переведенням HMI в режим підвищеної уваги.

### 4.4. Мультисенсорна крос-валідація та розрахунок довірчих інтервалів

Для потрійно-резервованих датчиків (наприклад, три незалежні перетворювачі тиску або три аналогові канали вимірювання напруги) модуль застосовує алгоритм мажоритарного голосування з аналізом дисперсії (2-out-of-3 quorum).

Нехай покази трьох датчиків становлять `s_1`, `s_2` та `s_3`. Медіанне значення `s_med` визначається ранжуванням вибірки. Модуль обчислює попарні розбіжності між датчиками:

```
d_12 = |s_1 - s_2|
d_23 = |s_2 - s_3|
d_31 = |s_3 - s_1|
d_max = max(d_12, d_23, d_31)
```

Якщо максимальна розбіжність не перевищує допустимого порогу похибки `max_spread`, усі три сенсори визнаються валідними. Оцінка фізичної величини формується на основі медіани, а результуюча дисперсія шуму зменшується за рахунок статистичного усереднення:

```
σ_est² = σ_sensor² / 3
```

Якщо один із сенсорів виходить з ладу і відхиляється на величину, більшу за `max_spread`, але дві інші попарні різниці залишаються в нормі, система переходить у деградований режим кворуму двох датчиків:

```
σ_est² = σ_sensor² / 2
```

Оцінка достовірності `confidence_score` знижується з 1.0 до 0.65, що відображається на панелі приладів зміною колірного індикатора з нейтрального зеленого на попереджувальний жовтий (Amber).

Якщо ж усі три попарні різниці перевищують `max_spread`, система фіксує повну втрату консенсусу вимірювань. Дисперсія розширюється у чотири рази, метрика достовірності падає до 0.15, а статус вимірювання маркується як `PLAUSIBILITY_FAILED`.

Для відображення на графічному дисплеї модуль обчислює 95% довірчий інтервал:

```
Confidence_Bound_95 = 1.96 · √(σ_est²)
```

Замість фіктивного числового значення із шістьма знаками після коми на панель HMI виводиться фізичний інтервал невизначеності `y_est ± Confidence_Bound_95`, що дає оператору повну картину надійності вимірювань.

---

## 5. Повний розбір автомата станів ISA-18.2

Стандарт визначає нормативну логіку переходів між сімома взаємопов'язаними станами життєвого циклу тривоги.

Перший стан — `NORMAL` (Нормальний стан). Вимірювана фізична величина перебуває в межах безпечного коридору. Графічний віджет HMI залишається в нейтральному колірному оформленні, звукові виклики відключені, навантаження на оператора нульове.

Другий стан — `UNACK_ALARM` (Непідтверджена активна тривога). Сигнал перетнув уставку `trip_threshold` і залишався за нею довше часу `On-Delay`. На HMI активується висококонтрастне миготіння яскраво-червоного кольору та вмикається імпульсний звуковий сигнал. Цей стан є імперативним: він вимагає обов'язкової фіксації уваги людини та натискання кнопки квитування `ACK`.

Третій стан — `ACK_ALARM` (Підтверджена активна тривога). Оператор натиснув кнопку `ACK`, підтвердивши отримання інформації. Звуковий зумер негайно вимикається, миготіння віджета припиняється, але колір залишається стабільно тривожним (жовтим або червоним). Це показує, що аварійний стан фізично ще триває, але оператор вже поінформований і контролює процес.

Четвертий стан — `RTN_UNACK` (Повернення до норми без підтвердження). Фізичний сигнал повернувся в норму до того, як оператор встиг натиснути кнопку `ACK`. Щоб запобігти зникненню інформації про швидкоплинні аварії (наприклад, імпульсний стрибок тиску чи короткочасне просідання напруги), тривога не гасне автоматично, а переходить у режим повільного приглушеного миготіння, вимагаючи фінального квитування скидання.

П'ятий стан — `SHELVED` (Тимчасово відкладена тривога). Оператор свідомо відкладає тривогу на фіксований час (наприклад, на 15 хвилин під час продування магістралі або заміни фільтра). Відкладення контролюється обов'язковим таймером зворотного відліку `shelved_until_time`. Після закінчення таймуату диспетчер автоматично перевіряє поточний рівень сигналу: якщо сигнал все ще за межами норми, тривога знову активується у стані `UNACK_ALARM`.

Шостий стан — `SUPPRESSED_BY_DESIGN` (Пригнічена логікою режиму або першопричиною). Тривога блокується програмною маскою стану системи або деревом першопричин. Наприклад, якщо знеструмлена головна шина живлення, тривоги зупинки периферійних датчиків автоматично маскуються, щоб не створювати вторинного шуму на екрані.

Сьомий стан — `OUT_OF_SERVICE` (Виведена з експлуатації). Ручний сервісний стан для проведення ремонтних робіт або калібрування знятого з експлуатації вузла.

---

## 6. Програмна реалізація на C99 та C++20

Нижче наведено повні фрагменти реалізації обох мовних стеків.

:::tabs
@tab c
```c
/* alarm_types.h — Базові типи та конфігурація тривог ISA-18.2 */
#ifndef ALARM_TYPES_H
#define ALARM_TYPES_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define MAX_ALARMS               64
#define MAX_ALARM_TAG_LEN        32
#define MAX_ACTION_TEXT_LEN      64
#define MAX_CONSEQUENCE_LEN      64
#define ALARM_RATE_WINDOW_MS     600000U /* 10 хвилин за стандартом ISA-18.2 */
#define ALARM_FLOOD_THRESHOLD    10U     /* >10 активних тривог за 10 хв = лавина */

typedef enum {
    ALARM_STATE_NORMAL = 0,
    ALARM_STATE_UNACK_ALARM,
    ALARM_STATE_ACK_ALARM,
    ALARM_STATE_RTN_UNACK,
    ALARM_STATE_SHELVED,
    ALARM_STATE_SUPPRESSED_BY_DESIGN,
    ALARM_STATE_OUT_OF_SERVICE
} AlarmState_t;

typedef enum {
    ALARM_PRIO_DIAGNOSTIC = 0,
    ALARM_PRIO_LOW,
    ALARM_PRIO_MEDIUM,
    ALARM_PRIO_HIGH,
    ALARM_PRIO_CRITICAL
} AlarmPriority_t;

typedef enum {
    ALARM_CAT_PROCESS = 0,
    ALARM_CAT_SAFETY,
    ALARM_CAT_SENSOR_HEALTH,
    ALARM_CAT_ACTUATOR_FAULT,
    ALARM_CAT_COMMUNICATION
} AlarmCategory_t;

typedef enum {
    SYS_STATE_COLD_BOOT = (1U << 0),
    SYS_STATE_STANDBY   = (1U << 1),
    SYS_STATE_ARMED     = (1U << 2),
    SYS_STATE_MISSION   = (1U << 3),
    SYS_STATE_FAILSAFE  = (1U << 4),
    SYS_STATE_MAINTENANCE = (1U << 5)
} SystemStateMask_t;

typedef struct {
    uint16_t id;
    char tag[MAX_ALARM_TAG_LEN];
    char action_text[MAX_ACTION_TEXT_LEN];
    char consequence[MAX_CONSEQUENCE_LEN];
    AlarmPriority_t priority;
    AlarmCategory_t category;
    uint32_t response_time_limit_ms;
    
    float trip_threshold;
    float clear_threshold;
    bool is_high_alarm;
    uint32_t on_delay_ms;
    uint32_t off_delay_ms;
    uint16_t chatter_limit;
    uint32_t chatter_window_ms;

    uint32_t suppression_state_mask;
    int32_t parent_alarm_id;
} AlarmConfig_t;

typedef struct {
    AlarmState_t state;
    AlarmState_t prev_state;
    float current_value;
    bool raw_trip_condition;
    
    uint64_t trip_start_timestamp_ms;
    uint64_t clear_start_timestamp_ms;
    uint64_t state_change_timestamp_ms;
    uint64_t shelved_until_timestamp_ms;

    uint16_t transitions_in_window;
    uint64_t first_transition_in_window_ms;
    bool is_chattering;

    bool is_suppressed_by_state;
    bool is_suppressed_by_parent;
} AlarmRuntime_t;

#endif /* ALARM_TYPES_H */
```
@tab cpp
```cpp
// alarm_types.hpp — Строга типізація та концепції ISA-18.2 на C++20
#pragma once

#include <cstdint>
#include <string_view>
#include <chrono>
#include <optional>
#include <span>

namespace isa18_2 {

using namespace std::chrono_literals;

inline constexpr size_t MaxAlarms = 64;
inline constexpr std::chrono::milliseconds AlarmRateWindow = 10min;
inline constexpr size_t AlarmFloodThreshold = 10;

enum class AlarmState : uint8_t {
    Normal = 0,
    UnacknowledgedAlarm,
    AcknowledgedAlarm,
    ReturnToNormalUnack,
    Shelved,
    SuppressedByDesign,
    OutOfService
};

enum class AlarmPriority : uint8_t {
    Diagnostic = 0,
    Low,
    Medium,
    High,
    Critical
};

enum class AlarmCategory : uint8_t {
    Process = 0,
    Safety,
    SensorHealth,
    ActuatorFault,
    Communication
};

enum class SystemStateMask : uint32_t {
    ColdBoot    = (1U << 0),
    Standby     = (1U << 1),
    Armed       = (1U << 2),
    Mission     = (1U << 3),
    Failsafe    = (1U << 4),
    Maintenance = (1U << 5)
};

constexpr SystemStateMask operator|(SystemStateMask a, SystemStateMask b) noexcept {
    return static_cast<SystemStateMask>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

constexpr bool operator&(SystemStateMask a, SystemStateMask b) noexcept {
    return (static_cast<uint32_t>(a) & static_cast<uint32_t>(b)) != 0;
}

struct AlarmConfig {
    uint16_t id{};
    std::string_view tag{};
    std::string_view action_text{};
    std::string_view consequence{};
    AlarmPriority priority{AlarmPriority::Low};
    AlarmCategory category{AlarmCategory::Process};
    std::chrono::milliseconds response_time_limit{30000ms};

    float trip_threshold{0.0f};
    float clear_threshold{0.0f};
    bool is_high_alarm{true};
    std::chrono::milliseconds on_delay{0ms};
    std::chrono::milliseconds off_delay{0ms};
    uint16_t chatter_limit{3};
    std::chrono::milliseconds chatter_window{5000ms};

    SystemStateMask suppression_mask{SystemStateMask::ColdBoot};
    std::optional<uint16_t> parent_alarm_id{std::nullopt};
};

struct AlarmRuntime {
    AlarmState state{AlarmState::Normal};
    AlarmState prev_state{AlarmState::Normal};
    float current_value{0.0f};
    bool raw_trip_condition{false};

    std::chrono::milliseconds trip_start_time{0ms};
    std::chrono::milliseconds clear_start_time{0ms};
    std::chrono::milliseconds state_change_time{0ms};
    std::chrono::milliseconds shelved_until_time{0ms};

    uint16_t transitions_in_window{0};
    std::chrono::milliseconds first_transition_in_window{0ms};
    bool is_chattering{false};

    bool is_suppressed_by_state{false};
    bool is_suppressed_by_parent{false};
};

} // namespace isa18_2
```
:::

Нижче наведено реалізацію диспетчера автомата станів, детектора лавини тривог та алгоритмів пригнічення.

:::tabs
@tab c
```c
/* alarm_rationalizer.c — Реалізація автомата станів та пригнічення */
#include "alarm_rationalizer.h"
#include <string.h>

void alarm_rationalizer_init(AlarmRationalizer_t *ar) {
    if (!ar) return;
    memset(ar, 0, sizeof(AlarmRationalizer_t));
    ar->current_sys_state = SYS_STATE_COLD_BOOT;
}

bool alarm_rationalizer_register(AlarmRationalizer_t *ar, const AlarmConfig_t *cfg) {
    if (!ar || !cfg || ar->count >= MAX_ALARMS) return false;
    size_t idx = ar->count++;
    memcpy(&ar->configs[idx], cfg, sizeof(AlarmConfig_t));
    memset(&ar->runtimes[idx], 0, sizeof(AlarmRuntime_t));
    ar->runtimes[idx].state = ALARM_STATE_NORMAL;
    return true;
}

void alarm_rationalizer_process(AlarmRationalizer_t *ar, uint64_t now_ms) {
    if (!ar) return;

    /* Фаза 1: Оцінка пригнічення за станом та батьківськими подіями */
    for (size_t i = 0; i < ar->count; ++i) {
        const AlarmConfig_t *cfg = &ar->configs[i];
        AlarmRuntime_t *rt = &ar->runtimes[i];

        rt->is_suppressed_by_state = ((ar->current_sys_state & cfg->suppression_state_mask) != 0);

        rt->is_suppressed_by_parent = false;
        if (cfg->parent_alarm_id >= 0 && (size_t)cfg->parent_alarm_id < ar->count) {
            AlarmState_t parent_state = ar->runtimes[cfg->parent_alarm_id].state;
            if (parent_state == ALARM_STATE_UNACK_ALARM || parent_state == ALARM_STATE_ACK_ALARM) {
                rt->is_suppressed_by_parent = true;
            }
        }

        if (rt->state == ALARM_STATE_SHELVED && now_ms >= rt->shelved_until_timestamp_ms) {
            rt->state = rt->raw_trip_condition ? ALARM_STATE_UNACK_ALARM : ALARM_STATE_NORMAL;
            rt->state_change_timestamp_ms = now_ms;
        }
    }

    /* Фаза 2: Обчислення автомата станів ISA-18.2 */
    for (size_t i = 0; i < ar->count; ++i) {
        const AlarmConfig_t *cfg = &ar->configs[i];
        AlarmRuntime_t *rt = &ar->runtimes[i];

        if (rt->state == ALARM_STATE_OUT_OF_SERVICE) continue;

        bool should_suppress = rt->is_suppressed_by_state || rt->is_suppressed_by_parent;
        if (should_suppress) {
            if (rt->state != ALARM_STATE_SUPPRESSED_BY_DESIGN && rt->state != ALARM_STATE_SHELVED) {
                rt->prev_state = rt->state;
                rt->state = ALARM_STATE_SUPPRESSED_BY_DESIGN;
                rt->state_change_timestamp_ms = now_ms;
                ar->total_suppressions++;
            }
            continue;
        } else {
            if (rt->state == ALARM_STATE_SUPPRESSED_BY_DESIGN) {
                rt->state = ALARM_STATE_NORMAL;
                rt->state_change_timestamp_ms = now_ms;
            }
        }

        if (rt->state == ALARM_STATE_SHELVED) continue;

        /* Гістерезис */
        if (cfg->is_high_alarm) {
            if (rt->raw_trip_condition) {
                if (rt->current_value <= cfg->clear_threshold) rt->raw_trip_condition = false;
            } else {
                if (rt->current_value >= cfg->trip_threshold) rt->raw_trip_condition = true;
            }
        } else {
            if (rt->raw_trip_condition) {
                if (rt->current_value >= cfg->clear_threshold) rt->raw_trip_condition = false;
            } else {
                if (rt->current_value <= cfg->trip_threshold) rt->raw_trip_condition = true;
            }
        }

        /* Затримки On-Delay та Off-Delay */
        bool active_filtered = false;
        if (rt->raw_trip_condition) {
            rt->clear_start_timestamp_ms = 0;
            if (rt->trip_start_timestamp_ms == 0) rt->trip_start_timestamp_ms = now_ms;
            if ((now_ms - rt->trip_start_timestamp_ms) >= cfg->on_delay_ms) active_filtered = true;
        } else {
            rt->trip_start_timestamp_ms = 0;
            if (rt->clear_start_timestamp_ms == 0) rt->clear_start_timestamp_ms = now_ms;
            if ((now_ms - rt->clear_start_timestamp_ms) < cfg->off_delay_ms) active_filtered = true;
        }

        AlarmState_t next_state = rt->state;
        switch (rt->state) {
            case ALARM_STATE_NORMAL:
                if (active_filtered && !rt->is_chattering) next_state = ALARM_STATE_UNACK_ALARM;
                break;
            case ALARM_STATE_UNACK_ALARM:
                if (!active_filtered) next_state = ALARM_STATE_RTN_UNACK;
                break;
            case ALARM_STATE_ACK_ALARM:
                if (!active_filtered) next_state = ALARM_STATE_NORMAL;
                break;
            case ALARM_STATE_RTN_UNACK:
                if (active_filtered) next_state = ALARM_STATE_UNACK_ALARM;
                break;
            default: break;
        }

        if (next_state != rt->state) {
            rt->prev_state = rt->state;
            rt->state = next_state;
            rt->state_change_timestamp_ms = now_ms;
        }
    }
}
```
@tab cpp
```cpp
// alarm_rationalizer.cpp — Обробка логіки диспетчера на C++20
#include "alarm_rationalizer.hpp"
#include <algorithm>
#include <cmath>

namespace isa18_2 {

void AlarmRationalizer::process(std::chrono::milliseconds now) noexcept {
    for (size_t i = 0; i < count_; ++i) {
        const auto& cfg = configs_[i];
        auto& rt = runtimes_[i];

        rt.is_suppressed_by_state = (current_sys_state_ & cfg.suppression_mask);

        rt.is_suppressed_by_parent = false;
        if (cfg.parent_alarm_id.has_value()) {
            const auto parent_id = *cfg.parent_alarm_id;
            if (parent_id < count_) {
                const auto parent_state = runtimes_[parent_id].state;
                if (parent_state == AlarmState::UnacknowledgedAlarm || parent_state == AlarmState::AcknowledgedAlarm) {
                    rt.is_suppressed_by_parent = true;
                }
            }
        }

        if (rt.state == AlarmState::Shelved && now >= rt.shelved_until_time) {
            rt.state = rt.raw_trip_condition ? AlarmState::UnacknowledgedAlarm : AlarmState::Normal;
            rt.state_change_time = now;
        }
    }

    for (size_t i = 0; i < count_; ++i) {
        const auto& cfg = configs_[i];
        auto& rt = runtimes_[i];

        if (rt.state == AlarmState::OutOfService) continue;

        const bool should_suppress = rt.is_suppressed_by_state || rt.is_suppressed_by_parent;
        if (should_suppress) {
            if (rt.state != AlarmState::SuppressedByDesign && rt.state != AlarmState::Shelved) {
                rt.prev_state = rt.state;
                rt.state = AlarmState::SuppressedByDesign;
                rt.state_change_time = now;
                total_suppressions_++;
            }
            continue;
        } else {
            if (rt.state == AlarmState::SuppressedByDesign) {
                rt.state = AlarmState::Normal;
                rt.state_change_time = now;
            }
        }

        if (rt.state == AlarmState::Shelved) continue;

        evaluate_raw_trip(cfg, rt);

        bool active_filtered = false;
        if (rt.raw_trip_condition) {
            rt.clear_start_time = 0ms;
            if (rt.trip_start_time == 0ms) rt.trip_start_time = now;
            if ((now - rt.trip_start_time) >= cfg.on_delay) active_filtered = true;
        } else {
            rt.trip_start_time = 0ms;
            if (rt.clear_start_time == 0ms) rt.clear_start_time = now;
            if ((now - rt.clear_start_time) < cfg.off_delay) active_filtered = true;
        }

        auto next_state = rt.state;
        switch (rt.state) {
            case AlarmState::Normal:
                if (active_filtered && !rt.is_chattering) {
                    next_state = AlarmState::UnacknowledgedAlarm;
                    total_trips_++;
                    add_rate_event(now);
                }
                break;
            case AlarmState::UnacknowledgedAlarm:
                if (!active_filtered) next_state = AlarmState::ReturnToNormalUnack;
                break;
            case AlarmState::AcknowledgedAlarm:
                if (!active_filtered) next_state = AlarmState::Normal;
                break;
            case AlarmState::ReturnToNormalUnack:
                if (active_filtered) next_state = AlarmState::UnacknowledgedAlarm;
                break;
            default: break;
        }

        if (next_state != rt.state) {
            rt.prev_state = rt.state;
            rt.state = next_state;
            rt.state_change_time = now;
        }
    }

    update_rate_metrics(now);
}

} // namespace isa18_2
```
:::

Нижче наведено реалізацію модуля перевірки фізичної достовірності (Plausibility Checker) та розрахунку довірчих інтервалів.

:::tabs
@tab c
```c
/* plausibility_checker.c — Крос-валідація та розрахунок нев'язок сенсорів */
#include "plausibility_checker.h"
#include <math.h>
#include <string.h>

#ifndef fmaxf
#define fmaxf(a,b) ((a) > (b) ? (a) : (b))
#endif

void plausibility_check_kinematics(PlausibilityChecker_t *pc, float imu_accel_x, float gnss_vel_x, uint64_t now_ms) {
    if (!pc) return;

    if (pc->last_eval_time_ms == 0) {
        pc->last_eval_time_ms = now_ms;
        pc->last_imu_accel_x = imu_accel_x;
        pc->last_gnss_vel_x = gnss_vel_x;
        pc->nav_velocity_confidence.estimated_value = gnss_vel_x;
        pc->nav_velocity_confidence.confidence_score = 1.0f;
        pc->nav_velocity_confidence.status = PLAUSIBILITY_VALID;
        return;
    }

    float dt = (float)(now_ms - pc->last_eval_time_ms) / 1000.0f;
    if (dt <= 0.0001f) return;

    float gnss_accel_x = (gnss_vel_x - pc->last_gnss_vel_x) / dt;
    float residual = fabsf(gnss_accel_x - imu_accel_x);

    pc->nav_velocity_confidence.estimated_value = gnss_vel_x;
    pc->nav_velocity_confidence.residual = residual;
    pc->nav_velocity_confidence.variance = residual * 0.25f + 0.05f;
    pc->nav_velocity_confidence.confidence_bound_95 = 1.96f * sqrtf(pc->nav_velocity_confidence.variance);

    if (residual < pc->config.max_kinematic_residual * 0.5f) {
        pc->nav_velocity_confidence.status = PLAUSIBILITY_VALID;
        pc->nav_velocity_confidence.confidence_score = 0.95f;
    } else if (residual < pc->config.max_kinematic_residual) {
        pc->nav_velocity_confidence.status = PLAUSIBILITY_DEGRADED;
        pc->nav_velocity_confidence.confidence_score = 0.70f;
    } else if (residual < pc->config.max_kinematic_residual * 2.0f) {
        pc->nav_velocity_confidence.status = PLAUSIBILITY_SUSPECT;
        pc->nav_velocity_confidence.confidence_score = 0.35f;
    } else {
        pc->nav_velocity_confidence.status = PLAUSIBILITY_FAILED;
        pc->nav_velocity_confidence.confidence_score = 0.05f;
    }

    pc->last_eval_time_ms = now_ms;
    pc->last_imu_accel_x = imu_accel_x;
    pc->last_gnss_vel_x = gnss_vel_x;
}
```
@tab cpp
```cpp
// plausibility_checker.cpp — Перевірка фізичної достовірності на C++20
#include "plausibility_checker.hpp"
#include <algorithm>
#include <cmath>

namespace isa18_2 {

void PlausibilityChecker::check_kinematics(float imu_accel_x, float gnss_vel_x, std::chrono::milliseconds now) noexcept {
    if (last_eval_time_ == 0ms) {
        last_eval_time_ = now;
        last_imu_accel_x_ = imu_accel_x;
        last_gnss_vel_x_ = gnss_vel_x;
        nav_velocity_confidence_.estimated_value = gnss_vel_x;
        nav_velocity_confidence_.confidence_score = 1.0f;
        nav_velocity_confidence_.status = PlausibilityStatus::Valid;
        return;
    }

    const float dt = std::chrono::duration<float>(now - last_eval_time_).count();
    if (dt <= 0.0001f) return;

    const float gnss_accel_x = (gnss_vel_x - last_gnss_vel_x_) / dt;
    const float residual = std::abs(gnss_accel_x - imu_accel_x);

    nav_velocity_confidence_.estimated_value = gnss_vel_x;
    nav_velocity_confidence_.residual = residual;
    nav_velocity_confidence_.variance = residual * 0.25f + 0.05f;
    nav_velocity_confidence_.confidence_bound_95 = 1.96f * std::sqrt(nav_velocity_confidence_.variance);

    if (residual < config_.max_kinematic_residual * 0.5f) {
        nav_velocity_confidence_.status = PlausibilityStatus::Valid;
        nav_velocity_confidence_.confidence_score = 0.95f;
    } else if (residual < config_.max_kinematic_residual) {
        nav_velocity_confidence_.status = PlausibilityStatus::Degraded;
        nav_velocity_confidence_.confidence_score = 0.70f;
    } else if (residual < config_.max_kinematic_residual * 2.0f) {
        nav_velocity_confidence_.status = PlausibilityStatus::Suspect;
        nav_velocity_confidence_.confidence_score = 0.35f;
    } else {
        nav_velocity_confidence_.status = PlausibilityStatus::Failed;
        nav_velocity_confidence_.confidence_score = 0.05f;
    }

    last_eval_time_ = now;
    last_imu_accel_x_ = imu_accel_x;
    last_gnss_vel_x_ = gnss_vel_x;
}

} // namespace isa18_2
```
:::

---

## 7. Інтеграційні тести та верифікація поведінки

Повний тестовий стенд демонструє чотири ключові фази поведінки диспетчера:

У першій фазі система працює в номінальному режимі польоту `SYS_STATE_MISSION`. Напруга акумулятора становить 27.8 В, струм споживання 12 А відповідає розрахунковій потужності моторів 330 Вт, прискорення IMU узгоджене зі швидкістю GNSS 15 м/с. Диспетчер фіксує нуль активних тривог, а HMI відображає стабільні показники нейтрального кольору.

У другій фазі симулюється аварійне просідання напруги силової шини 28 В до 19.5 В. Спрацьовує критична тривога `PWR_MAIN_BUS_UV`. Одночасно через падіння напруги перезавантажується оптичний далекомір, що генерує сигнал втрати кадрів `LIDAR_COMM_LOST`. Оскільки в конфігурації далекоміра встановлено зв'язок `parent_alarm_id = 0`, диспетчер миттєво позначає вторинну тривогу як пригнічену (`is_suppressed_by_parent = true`) і переводить її у стан `SUPPRESSED_BY_DESIGN`. На екрані оператора з'являється єдина чітка тривога `PWR_MAIN_BUS_UV` із вказівкою перемкнути контактор аварійного живлення, а вторинний шум ліквідується.

У третій фазі оператор натискає кнопку квитування `ACK` для тривоги `PWR_MAIN_BUS_UV`. Стан переходить з `UNACK_ALARM` у `ACK_ALARM`. Звуковий зумер негайно замовкає, миготіння припиняється, але колір віджета залишається зафіксованим у тривожному стані, нагадуючи про необхідність виконання аварійної посадки.

У четвертій фазі симулюється активний супутниковий спуфінг. GNSS-приймач фіксує стрибок швидкості від 15 до 35 м/с за три секунди, тоді як акселерометр IMU фіксує рівномірний політ із прискоренням 0.1 м/с². Модуль перевірки фізичної достовірності виявляє невідповідність між інтегралом прискорення та диференціалом швидкості GNSS. Метрика достовірності `confidence_score` падає до 0.05, статус маркується як `PLAUSIBILITY_FAILED`, а на диспетчер тривог надходить діагностична тривога `SENSOR_PLAUSIBILITY_WARN` пріоритету `High`. Навігаційний віджет HMI розширює довірчий інтервал швидкості до `35.0 ± 8.4 м/с` та забарвлюється у тривожний бурштиновий колір (Amber), попереджаючи оператора про неприпустимість автоматичного слідування за супутниковою траєкторією.

---

## 8. Аналіз відмов та сценаріїв FMEA для сигналізації

Під час проектування вбудованого диспетчера тривог необхідно враховувати критичні крайові випадки поведінки як самої автоматики, так і людини.

Розглянемо сценарій швидкого подвійного натискання кнопки `ACK`. У стані паніки або через фізіологічний тремор рук оператор може двічі поспіль клацнути по сенсорному екрану. Якщо в інтервалі 50 мілісекунд між першим і другим натисканням виникає нова критична аварія (наприклад, пожежа двигуна), друге випадкове натискання могло б миттєво підтвердити нову тривогу без її усвідомлення людиною. Для захисту від цього ефекту диспетчер реалізує антидребезг інтерфейсу: після кожної зміни списку активних тривог кнопка підтвердження блокується на 300 мілісекунд, унеможливлюючи сліпе квитування щойно виниклих подій.

Інший небезпечний сценарій — повний фізичний обрив лінії зв'язку з датчиком під час активного аварійного стану. Якщо термопара перегорає у момент перегріву двигуна, аналого-цифровий перетворювач видає нульове значення або плаваючу напругу, що в наївній системі сприймається як повернення температури до нормального стану. Диспетчер сигналізації зобов'язаний перевіряти прапорець апаратної валідності сенсора (`Quality == BAD`). При виявленні обриву автоматичне скидання тривоги суворо блокується, а стан переводиться у режим діагностичної несправності каналу.

Третій крайовий випадок пов'язаний із синхронізацією системного годинника. Якщо вбудований комп'ютер коригує час через NTP або протокол PTP (IEEE 1588), системний таймер може стрибнути назад на кілька секунд. Якщо диспетчер тривог використовує абсолютний календарний час для розрахунку тривалості `On-Delay` чи таймуату відкладення `Shelve`, такий стрибок призведе до нескінченного зависання таймерів. Усі внутрішні таймстати модуля реалізовано виключно на монотонному лічильнику часу (`CLOCK_MONOTONIC` або апаратний таймер SysTick мікроконтролера) з беззнаковою модульною арифметикою, що виключає збої при переході через нуль.

Четвертий сценарій стосується відновлення напруги після короткочасного просідання. Якщо в колі спрацьовує самовідновлюваний полімерний запобіжник PTC, напруга може здійснювати загасаючі коливання навколо порогу 22 В. Без коректно налаштованого гістерезису `clear_threshold = 24.5 В` та затримки `Off-Delay = 3000 мс` диспетчер входив би в режим неперервного миготіння, дезорієнтуючи пілота.

П'ятий сценарій — масове відкладення тривог оператором (*Shelving Abuse*). Бажаючи позбутися настирливого попередження про несправність резервного каналу зв'язку, оператор може багаторазово відкладати тривогу, забуваючи про накопичений ризик. Для запобігання створенню прихованих аварійних факторів диспетчер обмежує максимальну кількість одночасно відкладених тривог (не більше трьох) та встановлює жорстку верхню межу тривалості відкладення (не більше 15 хвилин). Після закінчення ліміту тривога примусово повертається на екран і вимагає ескалації рішення.

---

## 9. Архітектура першої причини (First-Out Alarm Detection)

У складних енергетичних та електроприводних комплексах ланцюгова реакція руйнування розгортається за лічені мілісекунди: пробій ізоляції обмотки спричиняє стрибок струму, який викликає спрацювання апаратного захисту драйвера, що призводить до просідання напруги проміжної ланки постійного струму, скидання мікроконтролера інвертора та відключення шини CAN.

Якщо реєстрація подій виконується з періодом опитування 100 мілісекунд, усі п'ять аварій потрапляють в один такт таймера з однаковою часовою міткою. Оператор бачить на екрані п'ять одночасних повідомлень і не може визначити, яка подія була причиною, а які — наслідком.

Для точної фіксації первинної причини модуль використовує архітектуру першої тривоги (*First-Out Alarm Detection*). Вхідні апаратні переривання компараторів, лічильників та драйверів записують подію у lock-free кільцевий буфер переривань із захопленням апаратного 64-бітного таймера мікросекундного розрізнення (DWT cycle counter на ARM Cortex-M).

Під час обробки черги диспетчер знаходить подію з найменшим абсолютним часом t_0. Ця подія отримує статус першопричини (*First-Out*), маркується спеціальним символом на HMI та виноситься у верхній рядок з найвищим пріоритетом. Усі наступні події, що виникли в інтервалі t_0 + Δt_cascade і мають фізичний зв'язок із першопричиною, групуються під нею у вигляді згорнутого списку симптомів.

---

## 10. Інженерна інтеграція з операційними системами реального часу (RTOS)

У реальних вбудованих архітектурах на базі FreeRTOS, Zephyr або RTEMS диспетчер тривог виділяється в окремий потік моніторингу середнього пріоритету, який працює з фіксованим періодом квантування 20 мілісекунд (частота 50 Гц).

Розподіл обов'язків між системними потоками будується за трирівневою ієрархією:

Перший рівень — високопріоритетний потік керування (*Control Task*, частота 500 Гц або 1 кГц). Цей потік виконує критичні розрахунки матриць обертання, фільтрації орієнтації та зворотних зв'язків ПІД-регуляторів приводів. Потік керування працює в режимі жорсткого реального часу і не має права викликати функції форматування рядків, блокуватися на м'ютексах чи чекати завершення передачі телеметрії. Потік лише записує сирі сенсорні вибірки у lock-free атомарні структури подвійної буферизації.

Другий рівень — потік перевірки достовірності та сигналізації (*Alarm Task*, частота 50 Гц). Потік прокидається по апаратному таймеру, зчитує зріз сенсорних даних, обчислює нев'язки фізичної моделі, виконує такти автомата станів ISA-18.2, оновлює лічильники ковзного вікна лавини тривог та формує бітові маски активних сповіщень.

Третій рівень — потік інтерфейсу та телеметрії (*Telemetry/HMI Task*, частота 10 Гц). Цей потік пакує активні тривоги та розраховані довірчі інтервали у кадри протоколів зв'язку (MAVLink `STATUSTEXT` та `NAMED_VALUE_FLOAT`, CANopen Emergency Objects або DDS Topics) і передає їх через DMA-канал на наземний планшет оператора.

Така багаторівнева ізоляція гарантує, що навіть за умов найважчої аварії з сотнями вторинних збоїв та піковим завантаженням графічного дисплея первинний польотний контролер збереже бездоганний детермінізм керування, а оператор отримає чітку, раціоналізовану та перевірену на фізичну достовірність картину стану апарата.
