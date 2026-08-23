# Том 8. Читання світу

Читач приходить сюди з томів 1–7. Він уміє зібрати схему, прочитати даташит, залити
прошивку, під'єднати чип по I²C, підняти лінк, порахувати живлення й утримати апарат у
просторі. Одного він не вміє: **зробити з фізичного явища число, якому можна вірити, і
довезти це число туди, де його чекають.**

Це й є том. Не каталог давачів — ремесло вимірювання: тракт, похибка, калібрування,
модальність за модальністю, і нарешті потік, у який усе це складається.

## Межа тому

| | том 7 «Положення в просторі» | **том 8 «Читання світу»** |
|---|---|---|
| що міряє | **себе**: нахил, курс, швидкість, координату, оберти | **світ навколо**: тепло, світло, повітря, об'єкт, поле, струм у чужому навантаженні, звук, кадр |
| типовий давач | IMU, магнітометр, барометр-альтиметр, GNSS, енкодер | термопара, фотодіод, NDIR, ToF, ТС, мікрофон, матриця |
| результат | оцінка стану апарата | вимірювання про середовище |

Дві межі, які я проводжу свідомо й обґрунтовую в Частині 5:

- **власне споживання — том 6, чуже навантаження — том 8.** «Виміряти споживання»,
  «Логер споживання», «Аудит струму спокою» лишаються в томі 6: це вимірювання себе.
  Розетка, що міряє чайник, — мій розділ 9.
- **вимірювання поля — том 8, виживання в полі — том 9.** RSSI, детектор поля, скан
  ефіру, лічильник Гейгера тут; глушіння, РЕБ, боротьба із завадою — том 9.

## Легенда міток

| мітка | значення |
|---|---|
| `наявна` | тема вже є в курсі (`flat-embedded.md`) |
| `+ref <шлях>` | стаття **написана** й лежить у резерві (`pool-embedded.md`) |
| `+ref(pend) <шлях>` | у резерві з позначкою `[pending]`: **адресу заведено в маніфесті, статтю ще не написано.** Вести `ref` сюди можна й треба; вигадувати НОВУ тему на те саме — не можна |
| `кандидат` | з `newtopics-embedded.md` |
| `НОВА` / `ВЛАСНА` | вироки за `vol-rules.md` |

Шляхи в три сегменти без назви книги (`sensors/motion/hc-sr04`, `boards/mcu/esp32-cam`,
`connect/ir/vs1838b-ir-rx`) — це **каталог**: конкретні модулі, які читач тримає в руках.
Розкладку звірено з **оновленим резервом (3676 статей, із них 903 `[pending]`)**, у якому
каталог уже присутній.

---

# Частина 1. Розділи

Тринадцять розділів, **156 кроків** (10–15 на розділ — у межах правила).
Порядок: спершу ремесло, спільне для всіх давачів (1–3), далі модальності від
найповільнішої до найшвидшої (4–9), далі дисципліна потоку (10), і нарешті два важкі
потоки — звук і кадр (11–13).

**1. Вимірювальний тракт** — 13 кроків.
Як фізична величина стає числом: перетворювач, збудження, підсилення, опора,
дискретизація, шумова підлога, і скільки біт із цього справжні.
*Спирається на:* ОП і фільтри (том 2), АЦП і DMA (том 4).

**2. Похибка й калібрування** — 11 кроків.
Чому число бреше і що з цим робити: точність проти роздільності, бюджет похибки, дві
точки, крива, компенсація температури, повірка за еталоном, коефіцієнти у флеші.
*Спирається на:* розділ 1, NVS і Flash (том 3).

**3. Виносний давач** — 11 кроків.
Давач за тридцять метрів від плати: спад, наводка, різні землі, 4–20 мА, чотири дроти,
розв'язка, захист входу — і як шукати обрив у кабелі.
*Спирається на:* розділи 1–2, диференційні лінії й RS-485 (том 5).

**4. Тепло** — 11 кроків.
Термістор, RTD, термопара, цифровий давач, безконтактна ІЧ-термометрія — і головне:
самонагрів, теплова інерція й місце встановлення, через які давач міряє не те.
*Спирається на:* розділи 1–3.

**5. Світло** — 10 кроків.
Фотодіод і трансімпеданс, освітленість у люксах, спектральна чутливість, УФ, колір,
модульований ІЧ, засвітка й динамічний діапазон.
*Спирається на:* розділи 1–2; далі живить розділи 7, 12, 13.

**6. Повітря** — 12 кроків.
Вологість, тиск, CO₂, летка органіка, чадний газ, пил: три різні фізики в одному корпусі,
крос-чутливість, прогрів, дрейф базової лінії й ціна калібрування.
*Спирається на:* розділи 1–2, 4 (усі ці давачі температурозалежні).

**7. Присутність і відстань** — 12 кроків.
Одна задача — «що там попереду і як далеко» — і п'ять фізик на вибір: ІЧ-бар'єр, PIR,
ультразвук, лазерний ToF, радар. Поле зору, хибні спрацювання, відбивність, багатопроменевість.
*Спирається на:* розділи 1, 5 (оптика й фотоприймач), 4 (піроелектрика).

**8. Поля й випромінювання** — 10 кроків.
Те, чого не видно: магнітне поле й Холл, напруженість ЕМ-поля, ефір як вимірюваний
об'єкт, RSSI як число, блискавка, іонізуюче тло.
*Спирається на:* розділи 1–3; радіо й антени (том 5).

**9. Вимірювання електромережі** — 13 кроків.
230 В без смерті й без брехні: розв'язка, шунт/ТС/Холл, справжній RMS, активна й
реактивна потужність, cos φ, гармоніки, перехід через нуль, кіловат-година.
*Спирається на:* розділи 1–3, 8 (Холл); мережа й безпека (том 2).
**Це та діра, з якої курс починається: обіцянка «розумної розетки» досі не виконана.**

**10. Потік вимірювань** — 14 кроків.
Десять давачів, кожен зі своїм періодом: розклад опитування, спільна шкала часу,
згладжування й ціна затримки, поріг із гістерезисом, подія замість потоку, агрегація,
правдоподібність, поведінка без каналу, бюджет трафіку.
*Спирається на:* усі попередні розділи; таймери й DMA (том 4), канал (том 5).

**11. Звук** — 15 кроків (стеля розділу).
Мікрофон, тракт, дискретизація, рівень у децибелах, спектр, вікно й витік, спектрограма,
тон, подія, запис, кодек — і той самий спектр по вібрації машини.
*Спирається на:* розділи 1, 10; I²S і DMA (том 4).

**12. Камера** — 12 кроків.
Від фотона до кадру в пам'яті: об'єктив і експозиція, матриця, заслінка, інтерфейс,
демозаїка, ISP, баланс білого, формат пікселя — і чому кадр не влазить у мікроконтролер.
*Спирається на:* розділи 1, 5, 10.

**13. Кадр як дані** — 12 кроків.
Кадр як вимірювання, а не картинка: гістограма, згортка, межа, поріг, різниця кадрів,
мітка, глибина зі стереопари — і скільки коштує винести відео назовні.
*Спирається на:* розділ 12; далі живить том 12 (машинне навчання).

---

# Частина 2. Розкладка

## 1. Вимірювальний тракт (13)

1. Що таке давач · `наявна`
2. Класи перетворювачів · `+ref electronics/sensors/transducer-classes`
3. Характеристики давача · `наявна` · + `+ref(pend) electronics/sensors/transfer-function-sensor`
4. П'єзо й оптичні перетворювачі · `+ref electronics/sensors/piezo-optical-semiconductor`
5. Узгодження давача з входом · `+ref electronics/sensors/sensor-input-matching`
   · + `+ref electronics/analog/transimpedance-amplifier` · `+ref electronics/analog/charge-amplifier`
6. Кондиціонування сигналу · `наявна` (міст, підсилення, зміщення)
   · спирається на «Міст Вітстона» й «Інструментальний підсилювач» із томів 1–2
7. Опора вимірювання · `+ref electronics/analog/voltage-reference-sources`
   · `+ref electronics/analog/ratiometric-measurement` · `+ref(pend) electronics/metrology/adc-vref-noise`
8. Зчитування сигналу · `наявна` · + `+ref electronics/digital/adc-sample-hold`
9. Найквіст і аліасинг · `наявна` + Проєктування антиаліасингового фільтра · `наявна`
   · `+ref electronics/analog/anti-aliasing-filter`
10. Скільки біт справжні · `+ref electronics/analog/adc-quantization` · `+ref electronics/analog/quantization-noise`
    · `+ref electronics/digital/sampling-quantization` · `+ref(pend) electronics/metrology/sar-adc-internals`
11. Шумова підлога тракту · `наявна` (Тепловий шум, Дробовий шум)
    · `+ref physics/condensed-matter-physics/flicker-noise` · `+ref electronics/analog/kT-over-C-noise`
    · `+ref electronics/analog/signal-noise-ratio` · `+ref electronics/analog/dynamic-range`
12. Дрейф нуля й боротьба з ним · `+ref electronics/analog/offset-voltage`
    · `+ref electronics/analog/auto-zero-opamp` · `+ref electronics/analog/chopper-amplifier`
13. **ВЛАСНА** «Тракт одного давача: від термістора до °C на екрані» — наскрізна: дільник,
    опора, АЦП, oversampling, лінеаризація, вивід. Далі цей самий тракт калібрують у
    розділі 2 і виносять на 30 м у розділі 3.

## 2. Похибка й калібрування (11)

1. Похибки вимірювань · `наявна`
2. Точність, роздільність, повторюваність · `+ref(pend) electronics/metrology/measurement-uncertainty` (ISO GUM)
3. Бюджет похибки · `+ref math/numerical-analysis/error-budget` · `+ref physics/mechanics/uncertainty-budget`
4. Дрейф і гістерезис · `наявна` · + `+ref(pend) electronics/metrology/adc-temperature-drift`
5. Виграш від усереднення · `+ref math/statistics/averaging` · `+ref math/statistics/averaging-gain`
6. Процедура калібрування давача · `наявна` · + `+ref electronics/metrology/calibration`
7. Дві точки, багато точок, крива · `+ref(pend) electronics/metrology/multipoint-calibration`
   · `+ref math/statistics/least-squares`
8. Калібрування АЦП зовнішньою опорою · `наявна`
9. Простежуваність і повірка за еталоном · `+ref(pend) electronics/metrology/traceability`
10. Проєктування під найгірший екземпляр · `+ref(pend) electronics/metrology/worst-case-analysis`
    · `+ref electronics/components/guarantee-levels` · `+ref electronics/components/arrhenius-lifetime` (старіння)
11. **ВЛАСНА** «Коефіцієнти в пристрої: де їх узяти, де зберігати, коли перевіряти» —
    зшиває калібрувальну криву, NVS із тому 3, заводські OTP-коефіцієнти чужого чипа й
    процедуру на виробництві (том 15 потім спирається).

## 3. Виносний давач (11)

1. Чому давач на дроті бреше · `+ref communications/buses/single-ended-line-limits`
   · `наявні` Ємнісна наводка, Індуктивна наводка
2. Синфазна завада й диференційний вхід · `+ref electronics/analog/common-mode-noise`
   · `+ref electronics/analog/cmrr` · `+ref electronics/analog/differential-signaling`
3. Земляні петлі · `наявна` · + `+ref electronics/analog/ground-loop`
4. Екранування · `наявна` · + `+ref electronics/pcb/shielded-cable` · `+ref electronics/pcb/twisted-pair`
   · `+ref electronics/pcb/ferrite-clamp` · `+ref physics/condensed-matter-physics/magnetic-shielding`
5. Струмова петля 4–20 мА · `+ref electronics/analog/current-loop-4-20ma`
   · `+ref communications/interfaces/current-loop`
6. Чотири дроти замість двох · `+ref electronics/analog/kelvin-connection`
   · `+ref physics/electromagnetism/4wire-resistance` · `+ref physics/condensed-matter-physics/four-probe-measurement`
7. Гальванічна розв'язка вимірювання · `+ref electronics/digital/digital-isolator`
   · `+ref(pend) electronics/optoelectronics/isolation-amplifier`
8. Захист входу · `+ref electronics/analog/input-protection-analog` · `+ref electronics/components/tvs-diode`
   · `+ref electronics/components/varistor` · `+ref electronics/analog/guard-ring`
9. Давач як вузол шини · `+ref communications/protocols/modbus` · `+ref communications/interfaces/rs422-rs485`
   (RS-485 уводить том 5 — тут його вживають)
10. Пошук обриву в кабелі · `+ref communications/radio-engineering/tdr`
11. **ВЛАСНА** «Давач за тридцять метрів» — наскрізна: той самий тракт із розділу 1
    виносять у поле; що ламається на кожному метрі й у якому порядку це лагодять.

## 4. Тепло (11)

1. NTC-термістор · `наявна` · + `+ref sensors/temp-gas/ky-013-thermistor`
2. Лінеаризація термістора · `+ref(pend) electronics/metrology/steinhart-hart`
   · `+ref(pend) electronics/sensors/ptc-thermistor`
3. RTD: платина замість оксиду · `+ref(pend) electronics/sensors/rtd-sensor` (тут «окупається» розділ 3)
4. Термопара · `+ref(pend) electronics/sensors/thermocouple`
5. **НОВА** «Ефект Зеєбека» → `book/physics/condensed-matter-physics`
   (у корпусі є лише вставка `hist-seebeck.md` у «Що таке давач» і спіновий Зеєбек — самого ефекту немає)
6. **НОВА** «Холодний спай і його компенсація» → `book/electronics/sensors`
7. Цифровий давач температури · `+ref sensors/temp-gas/ds18b20` · `+ref sensors/temp-gas/ky-028-temp`
8. Тепло, що доходить до давача · `+ref physics/thermal-statistical/heat-transfer`
   · `+ref physics/thermal-statistical/thermal-conductivity` · `+ref physics/thermal-statistical/heat-capacity`
   · `+ref physics/thermal-statistical/thermal-diffusivity` · `+ref physics/thermal-statistical/natural-convection`
   · `+ref electronics/components/thermal-chain`
9. **НОВА** «ІЧ-термометрія й випромінювальна здатність» → `book/electronics/sensors`
   · спирається на `+ref physics/thermal-statistical/blackbody-radiation`
   · `+ref physics/thermodynamics/black-body-radiation`
10. **НОВА** «Тепловізор: матриця мікроболометрів» → `book/electronics/sensors`
    + **НОВА** каталожний модуль (клас MLX90640 / AMG8833) → `catalog/sensors/temp-gas`
11. **ВЛАСНА** «Де ставити термодавач» — самонагрів, теплова інерція, тепловий міст до
    корпуса, вітер; чому три градуси різниці — це не похибка давача, а помилка монтажу.

*(«Тепловий опір і відведення тепла», «Передача тепла», «Тепловий бюджет системи» лишаються
в томах 1–2: там це про власне тепло плати, а не про вимірювання чужого.)*

## 5. Світло (10)

1. Фотодавачі · `+ref electronics/sensors/photo-sensors` · `+ref sensors/light-sound/ky-018-photoresistor`
2. Фізика фотоприймача · `+ref(pend) electronics/optoelectronics/photodetector-physics`
   · `+ref(pend) electronics/optoelectronics/pin-photodiode` · `+ref physics/optics/quantum-efficiency`
3. Фотострум у напругу · (трансімпеданс уведено в розділі 1) · `+ref(pend) electronics/optoelectronics/dark-current`
4. **НОВА** «Люмен, люкс, кандела: фотометрія проти радіометрії» → `book/physics/optics`
   (у корпусі немає жодної фотометричної одиниці; є лише `lambert-cosine-law`)
5. **НОВА** «Давач освітленості (ALS)» → `book/electronics/sensors`
   · `+ref physics/optics/lambert-cosine-law` · `+ref physics/optics/photon-budget-optical`
6. Колір як вимірювання · `+ref(pend) electronics/sensors/color-sensor`
   · `+ref physics/optics/colorimetry-basics` · `+ref physics/optics/color-spaces` · `+ref physics/optics/color-gamut`
7. УФ-індекс · `+ref(pend) electronics/sensors/uv-light-sensor`
   · `+ref physics/optics/am15-solar-spectrum` · `+ref physics/optics/solar-irradiance-model`
8. Модульований ІЧ: як не осліпнути від сонця · `+ref(pend) electronics/sensors/ir-communication`
   · `+ref connect/ir/vs1838b-ir-rx` · `+ref connect/ir/ky-022-ir-rx` · `+ref connect/ir/ky-005-ir-tx`
9. Лавинний режим і лічба фотонів · `+ref(pend) electronics/optoelectronics/avalanche-photodiode`
   (готує SPAD у розділі 7)
10. Полум'я, дим і чому це оптика · `+ref sensors/light-sound/ky-026-flame`
    · `+ref physics/optics/rayleigh-scattering`

## 6. Повітря (12)

1. Давачі оточення · `+ref electronics/sensors/environment-sensors`
2. Вологість: ємність, що змінюється · `+ref(pend) electronics/sensors/capacitive-humidity-sensor`
   · `+ref physics/thermal-statistical/humidity-measurement` · `+ref physics/thermodynamics/relative-humidity`
   · `+ref sensors/environment/dht11` · `+ref sensors/environment/gy-21`
3. Точка роси й конденсат у приладі · `+ref physics/thermal-statistical/dew-point`
4. Тиск як давач · `+ref(pend) electronics/sensors/mems-pressure-sensor` · `+ref physics/mechanics/pressure`
   · `+ref physics/mechanics/atmospheric-pressure` · `+ref physics/thermal-statistical/standard-atmosphere`
   · `+ref sensors/environment/gy-bmp280` · `+ref sensors/environment/gy-63`
   *(барометр-альтиметр — том 7; тут тиск — погода й потік)*
5. Швидкість потоку · `+ref(pend) electronics/sensors/pitot-tube` · `+ref physics/mechanics/dynamic-pressure`
6. CO₂ по-справжньому: NDIR · `+ref(pend) electronics/sensors/ndir-co2` · `+ref(pend) electronics/sensors/ndir-sensor`
7. Напівпровідниковий давач газу й що таке eCO₂ · `+ref(pend) electronics/sensors/mox-gas-sensor`
   · `+ref(pend) electronics/sensors/electronic-nose` · `+ref sensors/series/mq-family` · `+ref sensors/temp-gas/mq-gas`
8. Електрохімічна комірка: CO, O₂ · `+ref(pend) electronics/sensors/electrochemical-cell`
9. Пил PM2.5 · `+ref(pend) electronics/sensors/dust-aerosol-sensor`
   + **НОВА** «Розсіяння Мі» → `book/physics/optics` (є Релей, самого механізму для пилу немає)
10. Крос-чутливість і температурна поправка · `+ref(pend) electronics/sensors/cross-sensitivity-compensation`
11. **НОВА** «Індекс якості повітря» → `book/electronics/sensors` (з ppm у число для людини)
12. **ВЛАСНА** «Газовий давач у виробі: прогрів, базова лінія, ABC, вік» — зшиває розділ 2
    (калібрування), розділ 4 (температура) і реальність MOX/NDIR, де «калібрування» —
    це не разова дія, а політика на роки.

## 7. Присутність і відстань (12)

1. Безконтактна відстань · `наявна`
2. **кандидат** «Оптика: лінза, фокусна відстань, поле зору» (1 джерело; сам кандидат
   просить поставити це перед «Безконтактною відстанню») → **НОВА** → `book/physics/optics`
   · `+ref physics/optics/snells-law` · `+ref physics/optics/refractive-index`
3. Відбиття IR і оптичний бар'єр · `+ref electronics/sensors/reflection-absorption`
   · `+ref sensors/optical/ir-obstacle` · `+ref sensors/light-sound/ky-010-interrupter`
4. PIR: рух як зміна тепла · `+ref(pend) electronics/sensors/pir-sensor`
   · `+ref physics/electromagnetism/pyroelectric-effect` · `+ref physics/optics/fresnel-lens`
   · `+ref sensors/motion/hc-sr501`
5. Ультразвук · `+ref electronics/sensors/ultrasonic-rangefinder` · `+ref electronics/sensors/tof-ultrasonic`
   · `+ref physics/oscillations-waves/speed-of-sound` · `+ref physics/oscillations-waves/beam-pattern`
   · `+ref physics/oscillations-waves/sound-attenuation-air` · `+ref physics/electromagnetism/pzt-piezo-ceramics`
   · `+ref sensors/motion/hc-sr04`
6. Лазерний ToF · `+ref electronics/sensors/tof-laser` · `+ref(pend) electronics/sensors/tof-sensor`
   · `+ref(pend) electronics/sensors/vcsel` · `+ref(pend) electronics/sensors/spad-photon-counting`
   · `+ref(pend) electronics/sensors/tdc-time-digital-converter`
   · `+ref sensors/motion/tof250` · `+ref sensors/motion/tof10120`
7. Тріангуляція · `+ref electronics/sensors/triangulation` · `+ref(pend) electronics/sensors/position-sensitive-detector`
8. Радар на 24/60 ГГц · `+ref electronics/radio/fmcw-radar` · `+ref physics/oscillations-waves/doppler-effect`
9. Архітектури LiDAR · `наявна`
10. Близькість без відстані · `+ref electronics/analog/capacitive-sensing` · `+ref electronics/sensors/touch-controller`
    · `+ref(pend) electronics/sensors/inductive-proximity-sensor` · `+ref sensors/light-sound/ttp223-touch`
    · `+ref sensors/motion/ky-021-reed`
11. Похибки відстані · `+ref electronics/sensors/distance-errors` · `+ref(pend) electronics/sensors/multipath-ranging`
    · `+ref(pend) electronics/sensors/ultrasonic-chirp-coding` · Бюджет похибок далекоміра · `наявна`
12. **ВЛАСНА** «Вибір далекоміра під сцену» — чорна тканина, скло, дощ, сонце, кут,
    рухома ціль: одна таблиця рішень замість п'яти окремих правд.

*(Камера як далекомір — розділ 13: до неї читач ще не має матриці.)*

## 8. Поля й випромінювання (10)

1. Електромагнітний спектр як карта давачів · `+ref physics/electromagnetism/em-spectrum`
2. Магнітне поле й Холл · `+ref(pend) electronics/sensors/hall-sensor` · «Ефект Холла» (том 1)
   · `+ref physics/electromagnetism/magnetoresistance` · `+ref sensors/motion/ky-003-hall`
3. Струм без розриву кола · `+ref(pend) electronics/sensors/hall-current-sensor`
   · `+ref electronics/metrology/clamp-meter` (готує розділ 9)
4. Поле Землі й що йому заважає · `+ref physics/electromagnetism/earth-magnetic-field`
   · `+ref physics/condensed-matter-physics/eddy-currents` *(компас — том 7)*
5. Ближня зона: зондування плати · `+ref(pend) electronics/metrology/near-field-probing`
   · `+ref physics/electromagnetism/radiation-zones` · `+ref physics/electromagnetism/poynting-vector`
6. **НОВА** «Вимірювач напруженості поля» → `book/electronics/metrology`
7. RSSI як вимірювання, а не як індикатор · `+ref communications/propagation/rssi-signal-strength`
   · `+ref communications/propagation/link-quality-metrics` · `+ref communications/propagation/db-reference-variants`
8. **НОВА** «Приймач із програмною обробкою (SDR) як прилад» → `book/communications/radio-engineering`
   + **НОВА** каталожний модуль (клас RTL-SDR) → `catalog/instruments`
   · `+ref(pend) electronics/metrology/fft-spectrum` · `+ref communications/propagation/frequency-bands`
9. Гроза за 40 кілометрів · `+ref physics/electromagnetism/atmospheric-electricity`
   · `+ref physics/electromagnetism/lightning` · `+ref sensors/environment/as3935-lightning`
10. Іонізуюче тло · `+ref(pend) electronics/sensors/geiger-muller-counter` · `+ref(pend) electronics/sensors/ionization-chamber`
    · `+ref physics/nuclear-particle/radioactive-decay-law` · `+ref math/statistics/poisson-statistics`
    · `+ref physics/condensed-matter-physics/photomultiplier-tube`

## 9. Вимірювання електромережі (13)

1. Що таке мережа під навантаженням · `+ref physics/electromagnetism/ac-power-grid`
   · `+ref physics/electromagnetism/three-phase-ac`
2. Спершу — як не загинути · `+ref electronics/power-electronics/mains-safety`
   · `+ref physics/electromagnetism/current-safety` · `+ref physics/electromagnetism/protective-grounding`
   · `+ref(pend) electronics/metrology/measurement-safety-cat` (CAT I–IV)
3. Ізоляція вимірювального каналу · `+ref electronics/power-electronics/insulation-classes`
   · `+ref electronics/power-electronics/mains-hipot-test` · `+ref electronics/digital/digital-isolator`
4. Шунт · `наявна` (Струмовимірювальний шунт) · `+ref(pend) electronics/metrology/busbar-shunt`
   · `+ref physics/condensed-matter-physics/manganese-alloys-tcr`
   · `+ref physics/condensed-matter-physics/temperature-coefficient-alloys`
5. Трансформатор струму й котушка Роговського · `+ref(pend) electronics/metrology/current-transformer`
   · `+ref(pend) electronics/metrology/rogowski-coil`
6. Підсилювач вимірювання струму · `наявна` (Монітор струму) · `+ref(pend) electronics/metrology/current-sense-amplifier`
   · `+ref(pend) electronics/metrology/bidirectional-current-sense` · `+ref electronics/power-electronics/motor-current-sense`
7. Справжній RMS проти середньовипрямленого · `наявна` (Діюче значення, том 2)
   · `+ref(pend) electronics/metrology/true-rms` · `+ref electronics/power-electronics/rms-current`
8. Миттєва потужність, активна, реактивна, повна · `+ref physics/electromagnetism/instantaneous-power`
   · `+ref electronics/analog/reactive-power` · `+ref electronics/analog/power-factor`
   · `+ref physics/electromagnetism/three-phase-power`
9. Спотворений струм: гармоніки й THD · `+ref electronics/analog/harmonic-distortion`
   · `+ref electronics/power-electronics/pfc-basics` · `+ref electronics/analog/notch-filter`
10. Синхронізація з мережею · `+ref electronics/power-electronics/zero-cross-switching`
    · `+ref electronics/power-electronics/mains-transients`
11. **НОВА** «Кіловат-година: облік енергії в пристрої» → `book/electronics/metrology`
    · `+ref math/numerical-analysis/energy-units`
12. **НОВА** «Мікросхема-лічильник енергії» (клас ADE7953/CS5490/BL0937) → `book/electronics/metrology`
    + **НОВА** каталожний модуль (клас PZEM-004T) → `catalog/instruments`
    + **НОВА** каталожний модуль струму (клас INA219/ACS712) → `catalog/sensors`
    · `+ref(pend) electronics/sensors/power-monitor`
13. **ВЛАСНА** «Розумна розетка міряє навантаження» — наскрізна: ТС + справжній RMS +
    енергія + межа спрацювання + телеметрія. Це той крок, який закриває обіцянку, дану
    читачеві в томі 1.

## 10. Потік вимірювань (14)

1. Проблема потоку даних · `наявна` · + DMA + АЦП · `наявна`
2. Розклад опитування десяти давачів · `+ref programming/embedded-systems/periodic-scheduling`
   · `+ref algorithms/data-structures/ring-buffer` · `+ref algorithms/data-structures/queue-fifo`
3. Коли саме сталося вимірювання · `+ref communications/synchronization/measurement-time`
   · `+ref communications/synchronization/timestamps` · `+ref communications/synchronization/sampling-jitter`
   · `+ref(pend) algorithms/signal-robotics/sensor-timestamp-sync`
4. Спільна шкала часу · `+ref communications/synchronization/synchronous-multi-sensor-read`
   · `+ref communications/synchronization/clock-offset-drift` · `+ref communications/synchronization/sensor-latency-compensation`
   · **кандидат** «Часові мітки й спільна шкала часу для давачів» (1 джерело; кандидат
   адресує його томові 7 — забираю сюди, бо тут він потрібен усім давачам, а не лише фузії)
5. Дешеве згладжування · `+ref algorithms/signal-robotics/moving-average` · `+ref algorithms/signal-robotics/median-filter`
   · `+ref algorithms/signal-robotics/ema` · `+ref(pend) algorithms/signal-robotics/welford-online`
   · `+ref(pend) algorithms/signal-robotics/trimmed-mean` · `+ref math/statistics/robust-estimators`
6. Ціна згладжування · `+ref algorithms/signal-robotics/smoothing-vs-lag` · Бюджет затримки фільтра · `наявна`
7. Вибір фільтра · `наявна` + КІХ проти БІХ · `наявна` + Специфікація фільтра · `наявна`
8. Поріг, гістерезис, дребезг показань · `наявна` (Схема зчитування CC: АЦП, фільтрація, гістерезис)
   · `+ref programming/client-architecture/debouncing-throttling`
9. Давач збрехав · Виявлення відмови давача · `наявна` · `+ref algorithms/signal-robotics/sensor-insufficiency`
   · `+ref programming/embedded-systems/graceful-degradation` · `+ref programming/representation/sentinel-values`
10. Проріджування без утрати події · `+ref communications/signal-processing/decimation`
    · `+ref(pend) algorithms/signal-robotics/plot-downsampling`
11. Подія замість потоку · агрегація (min/max/avg/квантилі) · `+ref math/statistics/percentiles-quantiles`
12. Формат вимірювання на дроті · `+ref programming/representation/self-describing-format`
    · `+ref programming/representation/iso-8601` · `+ref programming/representation/zero-copy-serialization`
    · `+ref(pend) algorithms/data-compression/cobs-encoding` · `+ref(pend) algorithms/data-compression/crc-algorithm`
    *(транспорт — том 5; тут вирішують, ЩО і в якому вигляді передавати)*
13. **ВЛАСНА** «Від тисячі вибірок на секунду до двадцяти байтів на хвилину» — наскрізна:
    бюджет каналу, дельта, агрегація, звіт за подією, і що з цього видно на другому кінці.
14. **ВЛАСНА** «Канал зник: буфер, дозапис, дозвантаження» — store-and-forward для
    вимірювань. **СПІРНА** з томом 10 (див. Частину 4).

## 11. Звук (15)

1. Мікрофон і динамік · `наявна` (тут — тільки вхідна половина; вихідна в томі 12)
2. MEMS-мікрофон · `наявна` · + електретний тракт · `+ref(pend) electronics/sensors/electret-microphone`
3. Захоплення звуку: від мікрофона до буфера · `наявна` (I²S уводить том 4)
4. PDM і децимація · `+ref(pend) algorithms/signal-robotics/cic-filter`
   · `+ref communications/signal-processing/decimation`
5. Рівень у децибелах · Потужність і децибели · `наявна`
   · `+ref physics/biophysics/weber-fechner` · `+ref communications/propagation/db-reference-variants`
   + **НОВА** «Звуковий тиск і зважування A» → `book/physics/oscillations-waves`
6. Обробка на МК: фільтрація, рівень, AGC · `наявна`
7. Навіщо частота · `наявна` + ШПФ · `наявна` · `+ref physics/oscillations-waves/frequency-spectrum`
8. Вікно, витік і роздільність спектра · **НОВА** «Вікна ШПФ і витік спектра» →
   `book/algorithms/signal-robotics` · `+ref(pend) algorithms/signal-robotics/overlap-add`
9. Виявлення тонів · `наявна` · `+ref(pend) algorithms/signal-robotics/goertzel`
10. Детекція подій у звуці (VAD, пороги, енергія) · `наявна`
    (розпізнавання слів — KWS — том 12)
11. Проєктування КІХ-фільтрів · `наявна` · `+ref algorithms/signal-robotics/fir-filter`
    · `+ref algorithms/signal-robotics/band-filters` · `+ref algorithms/signal-robotics/fixed-point-implementation`
12. Запис звуку: WAV, кільцевий буфер, SD · `наявна` + Стиснення звуку на МК · `наявна`
    · `+ref(pend) algorithms/data-compression/auditory-masking` · `+ref communications/signal-processing/speech-codecs`
    · `+ref communications/signal-processing/media-container`
13. Вібродіагностика · `наявна` — той самий спектр по акселерометру: підшипник, дисбаланс,
    обгинаюча. **СПІРНА** з томом 7 (давач) і томом 12 (аномалії через ML)
14. **НОВА** «Мікрофонний масив: напрям на джерело» → `book/algorithms/signal-robotics`
    (у корпусі немає ні beamforming, ні TDOA)
15. **ВЛАСНА** «Пристрій, що чує подію» — наскрізна: мікрофон → кільцевий буфер → спектр →
    поріг → повідомлення, з бюджетом такту й пам'яті.

## 12. Камера (12)

1. Сенсор зображення · `наявна`
2. **кандидат** «Об'єктив і експозиція: поле зору, діафрагма, витримка, підсилення»
   (2 джерела; кандидат сам адресує це томові 8 після «CMOS-матриці») → **НОВА**
   «Експозиція: діафрагма, витримка, підсилення» → `book/physics/optics`
   *(половину про поле зору вже дав розділ 7 — тут лишається трикутник експозиції)*
   · `+ref physics/optics/optical-aberrations` · `+ref physics/optics/diffraction`
3. CMOS-матриця · `наявна` · `+ref(pend) electronics/optoelectronics/pixel-clock-timing`
4. Рядкова заслінка · `наявна` · `+ref(pend) electronics/optoelectronics/global-shutter`
5. Шум і динамічний діапазон кадру · `+ref electronics/optoelectronics/dynamic-range-noise`
   · `+ref(pend) electronics/optoelectronics/dark-current` · `+ref(pend) electronics/optoelectronics/dual-gain-sensor`
   · `+ref(pend) electronics/optoelectronics/pixel-binning`
6. Підключення камери до МК: DVP, MIPI-CSI, SPI · `наявна`
   · `+ref programming/embedded-systems/double-buffering`
7. Демозаїка · `наявна` · `+ref(pend) algorithms/computer-vision/edge-adaptive-demosaic`
   · `+ref(pend) algorithms/computer-vision/color-filter-array-variants`
8. ISP-пайплайн · `наявна` · `+ref(pend) algorithms/computer-vision/raw-processing-pipeline`
   · `+ref(pend) electronics/optoelectronics/gamma-correction` · `+ref(pend) electronics/optoelectronics/tone-mapping`
9. Баланс білого · `наявна`
10. Формати пікселів і буферів зображення · `наявна`
    · `+ref communications/signal-processing/ycbcr` · `+ref communications/signal-processing/chroma-subsampling`
    · `+ref communications/signal-processing/color-spaces-video` · `+ref communications/signal-processing/resolution-framerate`
11. Модель камери й калібрування · `+ref(pend) algorithms/computer-vision/camera-model`
    · `+ref(pend) algorithms/computer-vision/camera-calibration`
    · **кандидат** «Калібрування камери: pinhole, дисторсія, матриця K» (1 джерело)
12. **ВЛАСНА** «Кадр у 512 кілобайтах» — чому камера не влазить у мікроконтролер: розмір
    кадру × кадри × біти проти RAM і шини; що з цього робить ESP32-CAM
    · `+ref boards/mcu/esp32-cam` · `+ref programming/embedded-systems/video-latency`

## 13. Кадр як дані (12)

1. Зображення як дані · `наявна`
2. Гістограма · `наявна` · `+ref(pend) algorithms/computer-vision/clahe`
3. Згортки й фільтри · `наявна` · `+ref(pend) algorithms/computer-vision/separable-filters`
4. Виділення меж · `наявна` · `+ref(pend) algorithms/computer-vision/marr-hildreth-log`
5. Пороги й морфологія · `наявна` · `+ref(pend) algorithms/computer-vision/otsu-method`
   · `+ref(pend) algorithms/computer-vision/adaptive-thresholding`
6. Різниця кадрів: рух без нейромережі · `+ref(pend) algorithms/computer-vision/background-subtraction`
   · `+ref(pend) algorithms/computer-vision/blob-analysis`
7. Стабілізація зображення · `наявна`
8. Мітка як опора · Фідуційні мітки ArUco та AprilTag · `наявна`
   · `+ref(pend) algorithms/computer-vision/template-matching`
9. Глибина з кадру · Стереозір · `наявна` · `+ref(pend) electronics/sensors/structured-light-3d`
10. Кадр у байти · JPEG · `наявна` + MJPEG vs H.264 · `наявна` + H.264: NAL, SPS/PPS · `наявна`
    · `+ref algorithms/data-compression/why-compress` · `+ref algorithms/data-compression/inter-frame`
    · `+ref algorithms/data-compression/quality-bitrate` · `+ref communications/signal-processing/h264-hardware-codec`
11. Ціна якості · `+ref(pend) algorithms/data-compression/rate-control-algorithms`
    · `+ref(pend) algorithms/data-compression/psnr-ssim` · `+ref communications/signal-processing/generation-loss`
12. **ВЛАСНА** «Скільки коштує відео» — роздільність × кадри × бітрейт проти каналу,
    пам'яті й батареї; коли передавати кадр, коли — одне число з кадру.
    *(Транспорт відео — RTP/RTSP/GStreamer — том 5 і том 11.)*

---

# Частина 3. Не лягло нікуди

Нічого не викинуто мовчки. Адреси:

**→ том 7 «Положення в просторі»** (власний стан): Акселерометр · Гіроскоп · Магнітометр ·
IMU-давач · Шум і дрейф IMU · Розв'язка IMU · Матеріали для кріплення IMU · IMU й барометр ·
Барометр-альтиметр · GNSS · Давачі апарата · Процедура калібрування IMU · Фільтр Калмана ·
Комплементарний фільтр · Поєднання давачів · Оцінка орієнтації · Оптичний потік ·
Детектори кутів · Зіставлення ключових точок · Візуально-інерціальна одометрія.

**→ том 12 «Автоматизація»** (навчання й дія): Виявлення об'єктів · Нейродетектори ·
Зоопарк моделей детекції · Трекінг · KWS · Аномалії вібрацій через ML · TinyML ·
Квантування нейромереж · Інференс на пристрої · Латентність інференсу · Бенчмаркінг на
пристрої · **звукова половина «на вихід»**: Підсилювач класу D · Акустичне оформлення
динаміка · Відтворення: I2S/ЦАП/PDM-виходи · Активне гасіння шуму · Зміна темпу без зміни
висоти тону.

**→ том 5 «Комунікація»**: Телеметрія · Керування й телеметрія · Серіалізація даних ·
Пакування бінарного протоколу · Протоколи відеострімінгу · RTP і RTCP · RTSP і SDP.
*(Мій розділ 10 вирішує, ЩО передавати; як саме — там.)*

**→ том 11 «Дрони»**: FPV-відеосистеми · Конвеєр GStreamer · appsink і appsrc · Апаратне
декодування · Стик із відеоконвеєром · cv::Mat: пам'ять і володіння · Відеопідсистема станції.

**→ том 4 «Периферія МК»**: АЦП · Роздільність АЦП · Типи АЦП · Похибки АЦП · ЦАП ·
Шина I2S · DMA + SPI/I2S · Регістрова карта · Практикум даташитів.
*(Розділи 1–2 їх уживають і поглиблюють, а не переказують.)*

**→ том 6 «Керування живленням»**: Виміряти споживання · Логер споживання · Вимірювання
профілю струму · Аудит струму спокою плати — це вимірювання **себе**.

**→ том 9 «Безпека і перешкоди»**: Лінк під глушінням · Полювання на заваду · Шум і завади
(як боротьба, не як вимірювання).

**→ том 14 «Власні плати»**: Спільна земля · DFM · Тест-джиг · Корпус, IP-захист, роз'єми.

**→ том 4/12 (індикація)**: Класи дисплеїв · Кадр у пам'яті: framebuffer і RGB565 ·
Управління кольором: колірні профілі та гама.

---

# Частина 4. Діри

**Головне про попередній прохід.** Він працював без резерву й доповів **90 нових тем**.
Я перевірив кожну його рубрику — спершу по маніфестах корпусу, потім наново по **оновленому
`pool-embedded.md` (3676 статей, 903 з них `[pending]`, каталог уже всередині)**. Реальність
інша: написане покриває більшість, а частина «дір» узагалі вже **має адресу в маніфесті**
зі статусом `pending` — тему в корпусі визнано, її просто ще не написали. Найгостріше це в
`electronics/metrology`: 34 теми в резерві, з них **31 `pending`** — саме тому попередньому
проходу здалося, що вимірювання в корпусі немає взагалі.

**Після оновлення резерву я звірив усі свої `НОВА` наново — жодна не отримала адреси.**
Повітря, світло й вимірювання електрики виявилися покриті значно краще, ніж доповідалося,
але всі 21 тема, які я називаю новими, у резерві відсутні. Перевірено пошуком по
`pool-embedded.md` — жодного збігу: Зеєбек, холодний спай, емісивність і пірометрія,
мікроболометр, фотометричні одиниці, ALS, розсіяння Мі, індекс якості повітря, лінза й
поле зору, трикутник експозиції, вимірювач напруженості поля, SDR як прилад, кВт·год,
лічильник енергії, звуковий тиск і зважування A, вікна ШПФ, мікрофонний масив, плюс
чотири каталожні картки (тепловізійний модуль, RTL-SDR, PZEM-004T, INA219/ACS712).

| його твердження | що насправді |
|---|---|
| «Повітря — нуль тем із одинадцяти, корпус не має **жодної** теми про вологість, тиск, гази, CO₂, VOC, пил» | **8 написаних** (`humidity-measurement`, `dew-point`, `relative-humidity`, `standard-atmosphere`, `pressure`, `atmospheric-pressure`, `dynamic-pressure`, `environment-sensors`), **7 написаних у каталозі** (DHT11, Si7021, BMP280, BMP180, MS5611, MQ, родина MQ), **10 заведених `pending`** (MOX, NDIR ×2, електрохімія, пил, крос-чутливість, електронний ніс, ємнісна вологість, MEMS-тиск, Піто). Справді нових — **2** |
| «Світло — нуль тем із десяти, немає фотодіода, трансімпедансу, люксів, кольору, УФ, ІЧ» | трансімпеданс **написаний** (`electronics/analog/transimpedance-amplifier`), фотодавачі **написані**, плюс 10 написаних тем оптики й 6 каталожних модулів; PIN-фотодіод, APD, темновий струм, УФ, колір, ІЧ-зв'язок — **заведені `pending`**. Справді нових — **2** |
| «Температура — сам лише термістор» | RTD, термопара, PTC, Стейнгарт–Гарт — **заведені `pending`**; уся теплофізика **написана**. Справді нових — **4 (+1 каталожна)** |
| «Електрика й поле — „Монітор струму“, і все» | **написані**: `power-factor`, `reactive-power`, `harmonic-distortion`, `instantaneous-power`, `ac-power-grid`, `three-phase-power`, `mains-safety`, `insulation-classes`, `zero-cross-switching`, `rms-current`, `digital-isolator`, `clamp-meter`, `energy-units`. **`pending`**: true-RMS, CAT I–IV, ТС, Роговський, підсилювач струму, двонапрямковий, busbar, near-field, FFT-спектр, Гейгер, іонізаційна камера, Холл ×2. Справді нових — **4 (+3 каталожні)** |
| «Відстань — немає жодного давача, з яким читач працюватиме руками» | ультразвук, ToF-звук, ToF-лазер, тріангуляція, ІЧ-відбиття, похибки, ємнісне зондування, **FMCW-радар**, піроелектрика, лінза Френеля — усі **написані**; PIR, ToF-давач, SPAD, VCSEL, TDC, індуктивний — **`pending`**; каталог має 9 модулів. Справді нових давачів — **0** (одна нова тема оптики, і та з кандидатів) |
| «Мікрофонний тракт і спектр — діри по краях» | електретний тракт, PDM-децимація (`cic-filter`), психоакустичне маскування, Гертцель, overlap-add — **усі заведені `[pending]`**; `weber-fechner`, `speech-codecs`, `media-container`, `frequency-spectrum` **написані**; каталог має 3 мікрофонні модулі. Справді нових — **3** (dB SPL і зважування A, вікна ШПФ, мікрофонний масив) |
| «Дрібніші, але кусючі» (14 пунктів) | ратіометрія, бюджет похибки, динамічний діапазон кадру, 4–20 мА, тара на тензодавачі — **написані**; точність проти роздільності (ISO GUM), двоточкове калібрування, повірка, нічна зйомка (dual-gain, dark current), різниця кадрів — **`[pending]`**; «пікселі в міліметри» — це `camera-model`+`homography`, теж `[pending]`. Справді нових — **0** |
| «Вузол із багатьох давачів — майже порожньо» | увесь блок синхронізації (6 тем) і згладжування (6 тем) **написаний**, планувальник і кільцевий буфер **написані**. Справді нових — **0**, потрібні 2 власні статті |
| «Телеметрія числами — нічого» | `decimation`, `debouncing-throttling`, `sentinel-values`, `iso-8601`, `self-describing-format`, `zero-copy-serialization`, `ring-buffer` **написані**; COBS, CRC, проріджування графіка — **`pending`**. Справді нових — **0**, потрібні 2 власні статті |

**Підсумок вироків по тому.**

### `+ref` — узяти написане з резерву (≈120 звернень, ≈95 різних статей)

Найважливіші (решта — у Частині 2): `electronics/analog/current-loop-4-20ma` ·
`electronics/analog/kelvin-connection` · `electronics/analog/power-factor` ·
`electronics/analog/reactive-power` · `electronics/analog/harmonic-distortion` ·
`electronics/analog/transimpedance-amplifier` · `electronics/analog/capacitive-sensing` ·
`electronics/analog/ratiometric-measurement` · `electronics/analog/anti-aliasing-filter` ·
`electronics/digital/digital-isolator` · `electronics/metrology/calibration` ·
`electronics/metrology/clamp-meter` · `electronics/sensors/environment-sensors` ·
`electronics/sensors/photo-sensors` · `electronics/radio/fmcw-radar` ·
`physics/electromagnetism/instantaneous-power` · `physics/electromagnetism/pyroelectric-effect` ·
`physics/electromagnetism/em-spectrum` · `physics/thermal-statistical/humidity-measurement` ·
`physics/optics/quantum-efficiency` · `communications/synchronization/*` (6) ·
`algorithms/signal-robotics/*` (7) · `math/numerical-analysis/error-budget` ·
`math/statistics/least-squares` · `programming/embedded-systems/periodic-scheduling`.

### `+ref(pend)` — адреса є, стаття не написана (**86**)

Це не діри розкладки й не нові теми: у резерві вони стоять із позначкою `[pending]`.
Слуг і назву вже обрано — вести `ref` можна одразу, лишається написати текст.
**Це найбільша окрема категорія тому**: 86 тем проти 21 справді нової.

`electronics/sensors`: thermocouple · rtd-sensor · ptc-thermistor · pir-sensor · tof-sensor ·
spad-photon-counting · vcsel · tdc-time-digital-converter · multipath-ranging ·
ultrasonic-chirp-coding · inductive-proximity-sensor · structured-light-3d ·
position-sensitive-detector · mox-gas-sensor · ndir-co2 · ndir-sensor · electrochemical-cell ·
dust-aerosol-sensor · cross-sensitivity-compensation · electronic-nose ·
capacitive-humidity-sensor · mems-pressure-sensor · pitot-tube · uv-light-sensor ·
color-sensor · ir-communication · hall-sensor · hall-current-sensor · power-monitor ·
geiger-muller-counter · ionization-chamber · electret-microphone · transfer-function-sensor.
`electronics/metrology`: true-rms · measurement-safety-cat · current-transformer ·
rogowski-coil · current-sense-amplifier · bidirectional-current-sense · busbar-shunt ·
multipoint-calibration · steinhart-hart · traceability · measurement-uncertainty ·
worst-case-analysis · adc-temperature-drift · near-field-probing · fft-spectrum ·
sar-adc-internals · adc-vref-noise.
`electronics/optoelectronics`: pin-photodiode · avalanche-photodiode · photodetector-physics ·
dark-current · global-shutter · gamma-correction · tone-mapping · pixel-binning ·
pixel-clock-timing · dual-gain-sensor · isolation-amplifier.
`algorithms/computer-vision`: camera-model · camera-calibration · raw-processing-pipeline ·
edge-adaptive-demosaic · color-filter-array-variants · background-subtraction · otsu-method ·
adaptive-thresholding · blob-analysis · template-matching · separable-filters · clahe ·
marr-hildreth-log.
`algorithms/signal-robotics`: cic-filter · goertzel · overlap-add · welford-online ·
trimmed-mean · plot-downsampling · sensor-timestamp-sync.
`algorithms/data-compression`: auditory-masking · cobs-encoding · crc-algorithm ·
rate-control-algorithms · psnr-ssim.

### `НОВА` — теми немає ніде (**21**: 17 у книги + 4 каталожні картки)

Кожен рядок перевірено пошуком по оновленому резерву (включно з `[pending]`-адресами
й каталогом) — збігів немає.

| тема | куди | розділ |
|---|---|---|
| Ефект Зеєбека | `book/physics/condensed-matter-physics` | 4 |
| Холодний спай і його компенсація | `book/electronics/sensors` | 4 |
| ІЧ-термометрія й випромінювальна здатність | `book/electronics/sensors` | 4 |
| Тепловізор: матриця мікроболометрів | `book/electronics/sensors` | 4 |
| Люмен, люкс, кандела: фотометрія проти радіометрії | `book/physics/optics` | 5 |
| Давач освітленості (ALS) | `book/electronics/sensors` | 5 |
| Розсіяння Мі | `book/physics/optics` | 6 |
| Індекс якості повітря | `book/electronics/sensors` | 6 |
| Лінза, фокусна відстань і поле зору *(кандидат, 1 джерело)* | `book/physics/optics` | 7 |
| Експозиція: діафрагма, витримка, підсилення *(кандидат, 2 джерела)* | `book/physics/optics` | 12 |
| Вимірювач напруженості поля | `book/electronics/metrology` | 8 |
| Приймач із програмною обробкою (SDR) як прилад | `book/communications/radio-engineering` | 8 |
| Кіловат-година: облік енергії в пристрої | `book/electronics/metrology` | 9 |
| Мікросхема-лічильник енергії (ADE7953/CS5490/BL0937) | `book/electronics/metrology` | 9 |
| Звуковий тиск і зважування A | `book/physics/oscillations-waves` | 11 |
| Вікна ШПФ і витік спектра | `book/algorithms/signal-robotics` | 11 |
| Мікрофонний масив: напрям на джерело | `book/algorithms/signal-robotics` | 11 |
| Тепловізійний модуль (MLX90640/AMG8833) | `catalog/sensors/temp-gas` | 4 |
| SDR-приймач (RTL-SDR) | `catalog/instruments` | 8 |
| Лічильник мережі (PZEM-004T) | `catalog/instruments` | 9 |
| Давач струму (INA219/ACS712) | `catalog/sensors` | 9 |

### `ВЛАСНА` — може дати лише курс (**12**)

| стаття | розділ | чому атом цього не може |
|---|---|---|
| Тракт одного давача: від термістора до °C | 1 | зшиває дільник, опору, АЦП, oversampling і лінеаризацію — п'ять чужих атомів в один ланцюг, який далі веде через увесь том |
| Коефіцієнти в пристрої: узяти, зберегти, перевірити | 2 | спирається на NVS із тому 3 і на виробничу процедуру з тому 15 — атом не має права нічого припускати |
| Давач за тридцять метрів | 3 | 4–20 мА, екран, розв'язка, ТДР — це рішення, а не явище |
| Де ставити термодавач | 4 | висновок із теплофізики + монтажу + досвіду, якого немає в жодній окремій темі |
| Газовий давач у виробі: прогрів, базова лінія, вік | 6 | політика калібрування на роки, спирається на розділ 2 |
| Вибір далекоміра під сцену | 7 | порівняння п'яти фізик під одну задачу |
| Розумна розетка міряє навантаження | 9 | закриває обіцянку тому 1, зшиває розв'язку, RMS, енергію й телеметрію |
| Від тисячі вибірок до двадцяти байтів | 10 | бюджет каналу проти інформації — рішення, не факт |
| Канал зник: буфер, дозапис, дозвантаження | 10 | поведінка пристрою, а не властивість даних |
| Пристрій, що чує подію | 11 | наскрізний ланцюг мікрофон → спектр → поріг → повідомлення |
| Кадр у 512 кілобайтах | 12 | арифметика пам'яті й шини для конкретного класу плат |
| Скільки коштує відео | 13 | компроміс «кадр чи число з кадру» |

Десять із них наскрізні (читач доводить ланцюг до працюючого результату), дві оглядові
(«Вибір далекоміра під сцену», «Скільки коштує відео»). Кількість власних статей курсу
нічим не обмежена — і цей том справді потребує стількох: без них він розсипається на
каталог давачів.

---

# Частина 5. Спірне

**СПІРНА 1. Розділ 9 «Вимірювання електромережі» — суперник: том 6 «Керування живленням».**
Аргумент за том 6: усе про ватти й вольти в одному місці. Аргумент за том 8, і я на ньому
наполягаю: том 6 учить **годувати свій пристрій** (батарея, перетворювач, автономність), а
розетка з лічильником **міряє чужий світ** — навантаження, якого пристрій не контролює.
Розділ повністю побудований на ремеслі розділів 1–3 (розв'язка, шунт, RMS, похибка), якого в
томі 6 немає. Межа, яку пропоную закріпити: **власне споживання — том 6, чуже навантаження — том 8.**

**СПІРНА 2. Далекоміри — суперник: том 7 «Положення в просторі».**
Сьогодні «Безконтактна відстань», «Бюджет похибок далекоміра» й «Архітектури LiDAR» стоять
поруч з IMU. Аргумент за том 7: далекомір тримає висоту. Аргумент за том 8: далекомір
відповідає на питання «що переді мною», а не «де я»; і фізика в нього спільна з розділами
5 і 11, а не з інерціальною. Пропоную: **давач і його похибки — том 8; утримання висоти й
обхід перешкод — том 7 і том 13.**

**СПІРНА 3. Класична обробка кадру — суперник: том 12 «Автоматизація».**
Гістограма, згортка, межа, поріг, різниця кадрів — це вимірювання за кадром, те саме, що
термістор, лише двовимірне. Навчені моделі (детектори, трекери, KWS) — том 12. Межа:
**правило, написане людиною, — том 8; правило, вивчене з даних, — том 12.**

**СПІРНА 4. Вібродіагностика — суперники: том 7 (акселерометр) і том 12 (ML-аномалії).**
Беру її в розділ 11, бо це той самий спектр і та сама детекція події, лише датчик інший;
і бо діагностують **чужу машину**, а не власний нахил.

**СПІРНА 5. «Канал зник: буфер і дозавантаження» — суперник: том 10 «Архітектура IoT».**
Тут це поведінка одного вузла з вимірюваннями; там — властивість системи. Якщо том 10
візьме тему повністю, мій розділ 10 обійдеться посиланням.

**СПІРНА 6. Скан ефіру й детектор поля — суперник: том 9 «Безпека і перешкоди».**
Розводжу так: **виміряти поле — том 8, вижити в полі — том 9.** SDR як прилад і напруженість
поля тут; виявлення глушіння, РЕБ і протидія — там.

**СПІРНА 7. Земляні петлі й екранування — суперник: том 14 «Власні плати».**
Забираю їх у розділ 3, бо кусають вони саме на виносному давачі, за 500 кроків до власної
плати. Томові 14 лишається «Спільна земля» як питання розводки.

**СПІРНА 8. Мікрофон/динамік як пара.** Беру вхідну половину; клас D, оформлення динаміка
й відтворення віддаю томові 12. Якщо автор захоче тримати аудіотракт цілим, розділ 11
виросте на 3 кроки й стане 15 — це ще в межах.

---

# Частина 6. Відкрите питання до автора (не вирішую сам)

Попередній прохід поставив авторові питання про межу курсу й лишив його без відповіді.
Відповіді досі немає — **лишаю відкритим**, але тепер із цінами, порахованими по резерву:

| напрям | що вже є | ціна вести |
|---|---|---|
| **Ґрунт і вода** (вологість ґрунту, рівень, дощ) | **4 написані каталожні картки** (`sensors/water-soil/soil-moisture`, `sensors/water-soil/capacitive-soil`, `sensors/water-soil/hw-038-water-level`, `sensors/water-soil/funduino-rain`) — уся секція `water-soil` каталогу | найдешевше: 4 `ref` + 1 ВЛАСНА. Вистачить **половини розділу**, окремий розділ не потрібен |
| **Хімія рідин** (pH, провідність, TDS, каламутність, розчинений кисень) | нічого: у корпусі немає жодної теми (є лише `chemistry/…/ions-solution`) | 5–7 **НОВИХ** тем + власна стаття. Це справді окремий розділ |
| **Спектрометрія речовини** | `physics/nuclear-particle/mass-spectrometry`, `physics/optics/diffraction-grating` (обидві написані) | 3–4 **НОВІ** теми. Дуже далеко від цілі курсу |
| **Біосигнали** (пульс, SpO₂, ЕКГ) | 2 написані каталожні картки (`sensors/temp-gas/max30102`, `sensors/temp-gas/ky-039-pulse`) + `physics/electromagnetism/bioelectricity` | 3–5 **НОВИХ** тем; плюс питання відповідальності за медичні твердження |

Моя рекомендація, якщо автор захоче відповісти коротко: **ґрунт і воду — узяти** (майже
безкоштовно, і це прямий шлях до «розумного дому/теплиці», куди курс і так іде); **хімію
рідин, спектрометрію й біосигнали — не вести**, бо жодна з них не наближає читача до
апарата, що вимірює світ і діє.

---

# Частина 7. Заперечення

**1. «Емі» автора читаю як давач, а не як заваду — і це два розділи, а не один.**
Автор поставив «емі» в один ряд зі звуком, відео й температурою, тобто серед **давачів**.
Звідси розділ 8 (поле, ефір, випромінювання) і розділ 9 (мережа, потужність, енергія).
Без розділу 9 обіцянка курсу — «від розумної розетки» — лишається невиконаною через
п'ятнадцять томів. Боротьбу із завадами при цьому не забираю: вона томова 9.

**2. Начерк автора віддав томові 8 ще й навігацію — і сам же її звідти забрав.**
Окремим рішенням навігація пішла в том 7. Тому все «де я» я віддаю туди без залишку
(Частина 3), а собі лишаю «що навколо». Один наслідок, який варто назвати вголос:
**том 7 стоїть переді мною, але спирається на моє ремесло** — калібрування, шумова
підлога, спільна шкала часу потрібні IMU не менше, ніж термістору. Найдешевший фікс:
або том 7 бере три кроки з мого розділу 1–2 як короткий ранній дотик (правило «рано
коротко — пізніше глибоко»), або розділи 1–2 переїжджають у кінець тому 7. **Рекомендую
перше**: розривати «живлення → мотори → положення» не варто, автор побудував цю пару навмисно.

**3. Розділ 3 «Виносний давач» — це не «розділ про інтерфейси».**
I²C, SPI і RS-485 уводить том 4/5. Тут — єдина ситуація: давач далеко, і через це ламається
все, що працювало на столі. Такий розділ не породжує жоден каталог дисциплін, а кусає він
у кожному другому проєкті.

**4. Теорію не виношу в окремий розділ — свідомо.** Спектр живе в розділі про звук,
згортка — в розділі про кадр, статистика Пуассона — в розділі про випромінювання,
найменші квадрати — в розділі про калібрування. Розділу «математичні основи вимірювань»
у тому немає й не буде.

**5. Том великий: 13 розділів, 156 кроків — і я вважаю це виправданим.**
Обіцянка курсу: «пристрій, що **вимірює світ**, приймає рішення й діє». Перше з трьох —
цілком цей том, і автор просив саме тут «більше детально». Але якщо різати доведеться,
чесний порядок такий: (а) розчинити розділ 3 у розділі 1, лишивши чотири найкусючіші
кроки (−1 розділ, −7 кроків; ціна: виносний давач перестає бути окремим заходом);
(б) віддати половину розділу 8 томові 9 (−5 кроків; ціна: «емі» автора лишається без
половини змісту); (в) стиснути розділи 12–13 в один на 15 кроків (−1 розділ, −9; ціна:
камера й обробка кадру стають одним заходом, хоч це два). Разом це дає ≈135 кроків і
11 розділів. **Різати розділи 4, 5, 6 і 9 не можна** — саме вони закривають те, чого
курс обіцяв і не має.

**6. Головна правка до попереднього проходу — не структура, а арифметика.**
Його тринадцять розділів по суті збіглися з моїми (я прийшов до свого списку до того,
як відкрив його файл). Розійшлися ми в іншому: він доповів **90 нових тем**, бо не бачив
ні резерву, ні маніфестів. Насправді нових — **21** (з них 4 — каталожні картки), ще
**86** тем **уже мають адресу** в корпусі зі статусом `pending`, а решту закриває написане.
Тобто писати з нуля треба приблизно **вп'ятеро менше**, ніж здавалося; і майже все, що
лишилося, — це не «діра в корпусі», а **черга письма, яку корпус уже собі поставив**.

**7. Каталог — окремий урок, і не лише для мене.** У першій версії `pool-embedded.md`
каталогу не було зовсім, а це 138 написаних топіків, із яких **25 лягли просто в розкладку
цього тому** (HC-SR04, HC-SR501, DHT11, Si7021, BMP280, BMP180, MS5611, MQ, DS18B20,
TOF250, TOF10120, AS3935, ESP32-CAM, KY-серія…). Резерв відтоді оновлено, і я перерахував
усе по ньому. Але інші томи, які проєктувалися до оновлення, свої діри рахували без цього
шматка — їхні числа варто перевірити так само.

---

# Підсумок числами

- **Розділів:** 13 · **кроків:** 156 (10–15 на розділ)
- **Наявних тем курсу лягло:** 60
- **`+ref` у написане з резерву:** **199 різних статей** — 174 з книг і довідників + **25 каталожних карток**. Кожен шлях перевірено проти оновленого `pool-embedded.md`: **0 неіснуючих**
- **`+ref(pend)` — адреса є, стаття не написана:** **86** (усі перевірено: у резерві, усі справді `[pending]`)
- **`НОВА` — немає ніде:** **21** (17 у книги + 4 каталожні картки)
- **`ВЛАСНА`:** **12**
- **Кандидатів узято:** 4 з `newtopics-embedded.md` («Об'єктив і експозиція» → розділ 12, «Оптика: лінза, фокусна, поле зору» → розділ 7, «Калібрування камери» → розділ 12, «Часові мітки й спільна шкала часу» → розділ 10)
- **Спірних меж названо:** 8 · **відкритих питань до автора:** 1 (ґрунт/вода · хімія рідин · спектрометрія · біосигнали)

Співвідношення, заради якого все це рахувалося: на кожну тему, яку треба **вигадати**,
припадає чотири, які треба лише **написати** за вже заведеною адресою, і дев’ять, які
просто треба **прочитати**.
