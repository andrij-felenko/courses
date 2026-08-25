# Аналіз модуля «drony» — «Дрони й автономність» (guide/embedded)

## 1. Поточний стан

Секція `drony` — остання (14-та) у курсі, 11 тем, усі — власні статті курсу (жодного ref-кроку):

| # | slug | назва | версії |
|---|------|-------|--------|
| 1 | mjpeg-vs-h264 | MJPEG vs H.264 | basic+detailed done |
| 2 | where-to-compute | Де рахувати | basic+detailed done |
| 3 | output-mixing | Узгодження сигналів керування | basic+detailed done |
| 4 | model-zoo | Зоопарк моделей детекції | basic done |
| 5 | on-device-benchmarking | Бенчмаркінг на пристрої | basic done |
| 6 | model-export | Експорт і розгортання моделей ML | basic done |
| 7 | training-data-pipeline | Підготовка навчальних даних | basic done |
| 8 | servo-sizing | Вибір сервопривода | basic done |
| 9 | esc-bldc-driver | Регулятор обертів (ESC) | basic done |
| 10 | isp-pipeline | ISP-пайплайн | basic done |
| 11 | image-stabilization | Стабілізація зображення | basic done |

Модуль насправді містить ТРИ переплутані нитки: (а) привод дрона (servo-sizing, esc-bldc-driver, output-mixing), (б) камера/відео (isp-pipeline, image-stabilization, mjpeg-vs-h264), (в) бортовий ML (where-to-compute, model-zoo, benchmarking, export, training-data). А четверта нитка — власне АВТОНОМНІСТЬ, винесена в назву модуля, — у модулі відсутня: вона розкидана по mk (autonomous-system, mission-planning, mavlink-commands, mission-planner-qgc) і zvyazok (mavlink-from-ground, pymavlink, fpv-video-systems).

## 2. Головний діагноз

Модуль «Дрони й автономність» не містить ні дрона, ні автономності: нема жодного кроку про те, ЯК дрон літає (тяга, гвинт, реактивний момент, рами) і з чого складається (мотор BLDC, батарея), а автономність (autonomous-system, mission-planning) живе в секції «Мікроконтролер». Порядок усередині зламаний у кількох місцях — перша ж тема (кодеки) стискає кадри, походження яких пояснюється десятою темою (ISP); ML-конвеєр іде задом наперед (бенчмаркінг → експорт → дані). Опорні book-атоми (мотори, сенсор зображення, JPEG, нейромережі) існують у книгах, але заховані в інлайн-попапи замість кроків.

## 3. Порушення порядку (конкретно)

Усередині модуля:

1. **`output-mixing` (#3) стоїть перед `servo-sizing` (#8) і `esc-bldc-driver` (#9)**, хоча розкладає команди контролера саме на серво та ESC; стаття сама пише «уся конкретика серво… розібрана окремо» і інлайн-посилається на electronics/hobby-servo та electronics/esc — тобто виконавці мають бути пройдені ДО мікшера.
2. **`mjpeg-vs-h264` (#1) відкриває модуль**, хоча стискає відеокадри, походження яких (сенсор → RAW → ISP) курс пояснює лише в `isp-pipeline` (#10). Камери/сенсора зображення до цього місця в курсі нема взагалі.
3. **`where-to-compute` (#2) починається словами «Коли модель навчено й стиснуто…»**, але про моделі, навчання й експорт курс розповідає пізніше: `model-zoo` (#4), `model-export` (#6), `training-data-pipeline` (#7). Крок має стояти в КІНЦІ ML-конвеєра.
4. **`on-device-benchmarking` (#5) стоїть перед `model-export` (#6)** — бенчмаркати на пристрої можна лише вже експортовану/розгорнуту модель.
5. **`training-data-pipeline` (#7) стоїть після `model-export` (#6)** — у реальному конвеєрі дані передують навчанню, а навчання — експорту.
6. **`esc-bldc-driver` вимагає розуміння BLDC-мотора, якого в курсі нема взагалі** (принцип електромотора ніде не пояснено; у книзі є electronics/bldc-motor і electronics/brushed-dc-motor — обидва done).
7. **`servo-sizing` вимагає моменту сили (math-hinge-moment)** — механіки в курсі нема взагалі (osnovy — суто електрика). У книзі physics є атом `torque` (pending).
8. **`model-zoo` вимагає нейромереж/CNN/детекції**, яких у курсі до цього місця нема (mk/edge-inference у §7 торкається інференсу побіжно й сам страждає від того самого пропуску). Атоми algorithms/what-is-ml, neuron-layer, cnn, nn-detectors — усі done в книзі.

Крос-секційні (видно з повного маніфесту):

9. **zvyazok/video-streaming-protocols і zvyazok/fpv-video-systems (§13) спираються на кодеки**, які курс вводить лише в drony/mjpeg-vs-h264 (§14). Лікується переносом обох тем у відеорозділ drony (після кодеків).
10. **mk/edge-inference (§7) вимагає основ ML** (train-vs-inference, квантування), яких до §7 у курсі нема, — зона відповідальності аналітика mk, але фіксую.
11. **`isp-pipeline` написана під поточний порядок**: інтро посилається на mjpeg-vs-h264 і where-to-compute як на «Ми вже знаємо…». Після перестановки (ISP перед кодеками) інтро потребує правки → статус recheck.

## 4. Пропоновані розділи (усі 11 поточних тем збережено, move_in і нові — на місцях)

### Розділ 1. Як дрон літає: фізика платформи (8 кроків)
Мотивація: перший розділ «дронового» модуля має нарешті показати сам дрон. Механіки в курсі нема — розділ будується на pending-атомах physics/mechanics, які, судячи з назв (thrust-vs-weight, frame-configurations…), закладалися саме під цей курс.
1. **new:newtons-laws** — ДОДАТИ: сила, маса, прискорення; в physics-книзі атома нема, а «тяга проти ваги» без нього — стіна.
2. **ref:physics/torque** — ДОДАТИ: момент сили (потрібен reaction-torque і servo-sizing). [pending]
3. **ref:physics/thrust-vs-weight** — ДОДАТИ: тяга проти ваги. [pending]
4. **ref:physics/propeller-geometry** — ДОДАТИ: гвинт. [pending]
5. **ref:physics/reaction-torque** — ДОДАТИ: реактивний момент → чому гвинти крутяться в різні боки. [pending]
6. **ref:physics/frame-configurations** — ДОДАТИ: рами й конфігурації (квадро/гекса, X/+). [pending]
7. **ref:physics/fixed-wing-lift** — ДОДАТИ: літак/крило — друга платформа. [pending]
8. **ref:physics/vtol-transition** — ДОДАТИ: VTOL-гібриди. [pending]

### Розділ 2. Привод: мотори, ESC, серво й живлення (8 кроків)
1. **ref:electronics/brushed-dc-motor** — ДОДАТИ: принцип електромотора (курс досі жодного разу його не пояснив). [done]
2. **ref:electronics/bldc-motor** — ДОДАТИ: BLDC — мотор дрона. [done]
3. **own:esc-bldc-driver** (був #9) — тепер має під собою BLDC.
4. **new:drone-power-system** — ДОДАТИ: живлення дрона — LiPo, C-рейтинг, розподіл (PDB), просадка під тягою; zhyvlennia дала хімії й BMS, а дронової специфіки ніде нема.
5. **ref:electronics/hobby-servo** — ДОДАТИ: хобі-серво (output-mixing і servo-sizing на нього посилаються). [done]
6. **own:servo-sizing** (був #8).
7. **own:output-mixing** (був #3) — мікшер ПІСЛЯ обох виконавців; PID/attitude вже пройдені в keruvannia (§12).
8. **ref:physics/breguet-range-endurance** — ДОДАТИ: скільки летить — час польоту й дальність (закриває розділ; energy-density уже була в komponenty). [pending]

### Розділ 3. Камера на борту: від фотона до кадру (7 кроків)
1. **ref:electronics/image-sensor** — ДОДАТИ: сенсор зображення. [done]
2. **ref:electronics/cmos-matrix** — ДОДАТИ: CMOS-матриця (isp-pipeline на неї посилається). [done]
3. **ref:electronics/rolling-shutter** — ДОДАТИ: рядкова заслінка — джерело «желе», критично для стабілізації. [done]
4. **ref:algorithms/image-as-data** — ДОДАТИ: зображення як дані (пікселі, RGB) — новачок цього ще не бачив. [done]
5. **ref:algorithms/bayer-demosaic** — ДОДАТИ: демозаїка — серце ISP. [done]
6. **own:isp-pipeline** (був #10) — тепер спирається на пройдене; інтро переписати (recheck): зараз воно посилається на кодеки як «пройдені».
7. **own:image-stabilization** (був #11) — IMU з davachi (§10) уже пройдено.

### Розділ 4. Відео: стиснути й передати (7 кроків)
1. **ref:algorithms/why-compress** — ДОДАТИ: навіщо стискати. [done]
2. **ref:algorithms/jpeg-intra** — ДОДАТИ: JPEG — просторовий двигун. [done]
3. **ref:algorithms/inter-frame** — ДОДАТИ: міжкадрове стиснення — часовий двигун. [done]
4. **own:mjpeg-vs-h264** (був #1) — порівняння тепер стоїть на обох двигунах.
5. **ref:algorithms/quality-bitrate** — ДОДАТИ: якість і бітрейт — місток до радіоканалу. [done]
6. **own:video-streaming-protocols** — MOVE_IN із zvyazok: протоколи стрімінгу вимагають кодеків, у §13 вони висіли до кодеків.
7. **own:fpv-video-systems** — MOVE_IN із zvyazok: аналог vs DJI O3/HDZero — синтез камера+кодек+радіо (радіо з §13 уже пройдено).

### Розділ 5. Нейромережі й детекція (7 кроків)
1. **ref:algorithms/what-is-ml** — ДОДАТИ. [done]
2. **ref:algorithms/train-vs-inference** — ДОДАТИ: навчання в хмарі / інференс на борту — вісь усього розділу. [done]
3. **ref:algorithms/neuron-layer** — ДОДАТИ. [done]
4. **ref:algorithms/cnn** — ДОДАТИ: згорткові мережі — як мережа «бачить» кадр. [done]
5. **ref:algorithms/nn-detectors** — ДОДАТИ: що видає детектор (рамки, впевненість, NMS). [done]
6. **ref:algorithms/tracking** — ДОДАТИ: трекінг (where-to-compute його вживає). [done]
7. **own:model-zoo** (був #4) — вибір моделі тепер має ґрунт.

### Розділ 6. ML-конвеєр: від даних до борту (5 кроків)
1. **own:training-data-pipeline** (був #7) — дані йдуть першими.
2. **own:model-export** (був #6) — експорт після навчання.
3. **own:on-device-benchmarking** (був #5) — міряти можна лише розгорнуте.
4. **ref:algorithms/compute-cost** — ДОДАТИ: вартість обчислень у ватах і грамах — місток до рішення «де рахувати». [done]
5. **own:where-to-compute** (був #2) — фінальне рішення конвеєра, як і каже його власне інтро.

### Розділ 7. Автономний політ (8 кроків)
Це і є «автономність» із назви модуля — зараз вона в чужих секціях. MAVLink-транспорт (mavlink-from-ground, pymavlink) лишається в zvyazok (§13) — він про канал, і за порядком уже пройдений.
1. **own:autonomous-system** — MOVE_IN із mk: архітектура sense–decide–act, failsafe — це не «мікроконтролер», це дрон.
2. **ref:algorithms/sense-decide-act-loop** — ДОДАТИ: offboard-контур companion→FC (пряме продовження where-to-compute). [pending]
3. **own:mavlink-commands** — MOVE_IN із mk: команди апарату (arm/takeoff/goto); пакет MAVLink уже в zvyazok.
4. **own:mission-planning** — MOVE_IN із mk: вейпойнти й місії.
5. **own:mission-planner-qgc** — MOVE_IN із mk: наземні станції — інструмент до щойно пройдених місій.
6. **own:slam-navigation** — MOVE_IN із keruvannia: SLAM — автономна навігація без GPS, а не «керування й сигнали»; Калман/EKF і стереозір уже пройдені (§10, §12).
7. **new:obstacle-avoidance** — ДОДАТИ: уникання перешкод (стереозір/лідар/детектор → маневр); у книгах нема (в algorithms лише dijkstra/missions-waypoints pending) — а без нього «автономний дрон» неповний.
8. **ref:algorithms/geofence-algorithm** — ДОДАТИ: геозона — програмний запобіжник автономії. [pending]

**Перевірка повноти:** усі 11 поточних тем розкладено (4.4, 6.5, 2.7, 5.7, 6.3, 6.2, 6.1, 2.6, 2.3, 3.6, 3.7). move_out — порожній: жодна тема модуля не чужа.

## 5. move_in (7 тем)

| тема | звідки | чому |
|------|--------|------|
| autonomous-system | mk | серце модуля «автономність»; у «Мікроконтролері» — чужорідна |
| mavlink-commands | mk | команди апарату — це автономія, не архітектура МК; транспорт MAVLink лишився в zvyazok |
| mission-planning | mk | місії/вейпойнти — автономія |
| mission-planner-qgc | mk | GCS — інструмент місій, іде відразу за mission-planning |
| slam-navigation | keruvannia | автономна навігація, а не обробка сигналів; потребує стереозору (davachi) і EKF (keruvannia) — обидва вже пройдені |
| video-streaming-protocols | zvyazok | вимагає кодеків, які вводяться лише тут; у §13 стояла ДО кодеків — злам порядку |
| fpv-video-systems | zvyazok | синтез камера+кодек+радіолінк; без mjpeg-vs-h264 порівняння «аналог vs цифра» висить у повітрі |

## 6. Прогалини (missing)

Для новачка (нуль фізики/електроніки/програмування):
- **new:newtons-laws** — сила/маса/прискорення: механіки нема ні в курсі, ні в physics-книзі, а розділ 1 нею дихає.
- **ref:physics/torque** — момент сили (servo-sizing, reaction-torque).
- **ref:physics/thrust-vs-weight, propeller-geometry, reaction-torque, frame-configurations** — фізика польоту (усі є pending-атомами physics/mechanics).
- **ref:electronics/brushed-dc-motor → bldc-motor** — принцип електромотора перед ESC.
- **ref:electronics/hobby-servo** — серво перед servo-sizing/output-mixing.
- **ref:electronics/image-sensor, cmos-matrix, rolling-shutter** — камера перед ISP.
- **ref:algorithms/image-as-data, bayer-demosaic** — пікселі й демозаїка перед ISP.
- **ref:algorithms/why-compress, jpeg-intra, inter-frame, quality-bitrate** — двигуни стиснення перед кодеками.
- **ref:algorithms/what-is-ml, train-vs-inference, neuron-layer, cnn, nn-detectors, tracking** — основи нейромереж перед model-zoo.
- **ref:algorithms/compute-cost** — перед where-to-compute.

Для повного покриття теми модуля:
- **new:drone-power-system** — LiPo/C-рейтинг/PDB/просадки: дронового живлення нема ніде (zhyvlennia — загальне).
- **ref:physics/fixed-wing-lift, vtol-transition** — платформи поза мультикоптером.
- **ref:physics/breguet-range-endurance** — час польоту й дальність.
- **ref:algorithms/sense-decide-act-loop** — offboard-контур.
- **new:obstacle-avoidance** — уникання перешкод (у книгах відсутнє).
- **ref:algorithms/geofence-algorithm** — геозона.

## 7. Органічність ref/own

- Зараз модуль — **0 ref-кроків з 11**, при тому що власні статті густо інлайн-посилаються на book-атоми (jpeg-intra, inter-frame, cmos-matrix, bayer-demosaic, hobby-servo, esc, tinyml, nn-detectors, tracking…). Для решти курсу нормою є ref-кроки (osnovy — суцільні refs). Отже опорний матеріал у цьому модулі захований у попапи — новачок, який їх не відкриває, іде крізь стіну незнаного. Пропозиція вище піднімає ключові атоми в кроки.
- Зворотний бік: розділи 1 і 5 виходять «стрічками ref-ів» (7–6 поспіль). Це стиль osnovy, прийнятно для guide, але розділи мають нести нитку назвою і, в ідеалі, отримати короткі власні статті-містки або власну оглядову статтю на початку розділу 1 («Анатомія дрона») — рішення лишаю редактору.
- Дублювання own vs book-атом: own `esc-bldc-driver` (курс) і book `electronics/esc` — виправдано (курсова стаття кумулятивна, DSHOT/інтеграція), book-атом лишається інлайном; те саме про `servo-sizing` vs `electronics/hobby-servo`.
- `isp-pipeline` після перестановки потребує правки інтро (посилається на mjpeg-vs-h264/where-to-compute як пройдені) → статус recheck.

## 8. Модуль як ціле

- **Назва** «Дрони й автономність» стає влучною лише ПІСЛЯ move_in автономних тем; без них це «відео і ML на дроні».
- **Розмір**: після реорганізації ~50 кроків у 7 розділах — це найбільший модуль курсу. Розумний варіант — розбити на ДВА модулі: «Дрон: платформа, привод, камера й відео» (розділи 1–4) і «Бортовий зір і автономність» (розділи 5–7). Розріз між 4 і 5 природний (закінчується залізо+відеотракт, починається ML).
- **Місце в курсі**: останнє — правильне: capstone, що збирає фізику (§1), живлення (§6), МК (§7), давачі (§10), керування (§12) і радіо (§13).
- **Ризик черги письма**: майже всі physics/mechanics-refи розділу 1 — pending у книзі; модуль стає головним замовником на дописання physics/mechanics (атоми там явно закладалися під цей курс).
