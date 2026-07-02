# Аналіз модуля «zvyazok» — Звʼязок і радіо (guide/embedded)

Дата: 2026-07-02. Джерела: `E:/develop/courses/guide/embedded/manifest.js` (прочитано повністю),
`E:/develop/courses/book/communications/manifest.js` (повний перелік slug/title), grep по `book/programming/manifest.js`.

## 1. Поточний стан модуля

22 теми пласким списком, порядок за маніфестом:

| № | id | Назва |
|---|----|-------|
| 1 | ref:communications/ip-routing | Маршрутизація |
| 2 | own:data-reliability | Надійність даних |
| 3 | own:jamming-fhss | Лінк під глушінням |
| 4 | own:link-budget | Бюджет лінії |
| 5 | own:esp32-antenna | Антена ESP32 |
| 6 | own:nfc-rfid | NFC/RFID |
| 7 | own:esp32-module | ESP32-модуль |
| 8 | own:mavlink-from-ground | MAVLink із землі |
| 9 | own:pymavlink | pymavlink |
| 10 | own:pcb-antenna-layout | Топологія антени на PCB |
| 11 | own:arq-strategies | Стратегії ARQ |
| 12 | own:fpv-video-systems | FPV-відеосистеми |
| 13 | own:multiple-access-methods | Методи множинного доступу |
| 14 | own:video-streaming-protocols | Протоколи відеострімінгу |
| 15 | own:802-11-versions | Стандарти 802.11 |
| 16 | own:itu-r-propagation-models | Моделі розповсюдження ITU-R і 3GPP |
| 17 | own:propagation-modes | Режими поширення радіохвиль |
| 18 | own:lpwan | LPWAN |
| 19 | own:thread-matter-zigbee | Thread, Zigbee і Matter |
| 20 | own:rpc-embedded | RPC у вбудованих системах |
| 21 | own:frequency-budget-analysis | Частотний бюджет у системах зв'язку |
| 22 | own:rf-frontend | RF-тракт: підсилювачі, перемикач і балун |

Профіль: 21 own + 1 ref. Це аномалія на тлі решти курсу — і головна причина прогалин: книга
`book/communications` містить **десятки готових done-статей** (децибели, поширення, антени, модуляція,
пакети, TCP/UDP, BLE, RC-лінк, MQTT, LoRa), а модуль використовує з неї ОДНУ (ip-routing) — і ту першим
кроком без жодної підготовки.

## 2. Порушення порядку (з урахуванням попередніх секцій)

1. **ip-routing стоїть кроком №1 модуля** — маршрутизація IP без жодного введення в мережі: у курсі до
   цього немає ані поняття пакета (communications/channel-band-packet не залучено), ані адресації
   MAC/IP/ARP (communications/mac-ip-arp не залучено). Новачок відкриває модуль «радіо» зі стрибка в
   середину мережевого стека.
2. **jamming-fhss (№3) стоїть перед link-budget (№4)**, хоча запас на глушіння (jamming margin) — це
   поняття з бюджету лінка; і перед будь-яким поясненням модуляції: FHSS/DSSS — техніки розширеного
   спектра, а communications/spread-spectrum (done) у курсі не з'являється взагалі.
3. **link-budget (№4) оперує децибелами (dB/dBm) і підсиленням антен**, але децибели в курсі ніде не
   вводились (communications/power-decibels не залучено), а перша антенна тема (esp32-antenna) стоїть
   лише кроком №5 — тобто Friis і antenna gain використано ДО того, як читач бачив антену.
4. **itu-r-propagation-models (№16) стоїть перед propagation-modes (№17)** — емпіричні моделі поширення
   (Hata, 3GPP) подано раніше за самі фізичні режими поширення, які ці моделі описують. Прямий переворот.
5. **nfc-rfid (№6) вклинюється між esp32-antenna (№5) і esp32-module (№7)** — індуктивний зв'язок
   ближнього поля розриває антенно-модульну нитку ESP32.
6. **mavlink-from-ground (№8) і pymavlink (№9) стоять посеред радіозаліза** — перед pcb-antenna-layout
   (№10) і rf-frontend (№22): прикладний протокол дрона перериває фізичний блок, після чого курс знову
   повертається до антен і RF-тракту.
7. **data-reliability (№2) і arq-strategies (№11) — одна нитка** (цілісність даних → повтори передачі),
   розірвана вісьмома радіотемами.
8. **video-streaming-protocols (№14) пакетизує H.264**, але кодеки курс пояснює лише в НАСТУПНІЙ секції
   drony (mjpeg-vs-h264); також протоколи RTP/WebRTC/SRT потребують TCP/UDP, а
   communications/tcp-vs-udp у курсі не залучено ніде.
9. **802-11-versions (№15) описує покоління Wi-Fi через OFDM/QAM/MIMO** — але ні введення у Wi-Fi
   (communications/wifi done — не залучено), ні модуляції в курсі до цього кроку немає.
10. **multiple-access-methods (№13) стоїть після прикладних відеотем (№12)** і далеко після jamming-fhss
    (№3), хоча поділ ефіру — база для всіх стандартів (Wi-Fi CSMA/CA, LoRaWAN, Zigbee).
11. **rf-frontend (№22) — останній крок модуля**, хоча антенні теми (№5, №10) і link-budget (№4)
    концептуально на нього спираються (каскад Фріїса, LNA перед приймачем). Радіозалізо розірвано на
    три шматки (5, 7, 10 … 22).
12. **frequency-budget-analysis (№21) затиснуто між rpc-embedded (№20) і rf-frontend (№22)** — тема про
    дрейф опорних генераторів і канальний план стоїть між програмним протоколом і залізом без нитки
    (її пререквізити tcxo-ocxo з komponenty — ок, але місце випадкове).
13. **Міжсекційне: mk/wifi-fast-connect** (секція mk, №7 у курсі) вимагає розуміння Wi-Fi і WPA
    (кешування PMK!), яке з'являється лише тут, у 802-11-versions — Wi-Fi-практику подано за 6 секцій
    до першого пояснення Wi-Fi. → move_in сюди.
14. **Міжсекційне: mk/mavlink-commands** — «Команди MAVLink» живе в секції «Мікроконтролер і процесор»
    посеред тем архітектури МК, а її пара mavlink-from-ground/pymavlink — тут. Нитка MAVLink розірвана
    між секціями. → move_in сюди.
15. **Міжсекційне: drony/mjpeg-vs-h264** мусить передувати video-streaming-protocols (див. п.8).
    → move_in сюди.

## 3. Цільова структура: 10 розділів

Логіка наскрізна: фізика ефіру → як дані сідають на хвилю → антени → радіозалізо → бюджет і живучість
лінка → поділ ефіру і стандарти → пакети й мережа → канали дрона (RC/MAVLink) → відеолінк.
Блок «дані/мережа» свідомо ПІСЛЯ радіоблоку: Thread/Matter — IPv6-mesh, але сам розділ стандартів
читається на рівні «хто з ким і в якій смузі», а IP-глибина приходить у R8 перед MAVLink-über-UDP і відео.

### R1. Ефір: хвиля, загасання, децибели (5)
1. ref:communications/power-decibels — ДОДАТИ: уся розмова радіо ведеться в dB/dBm; у курсі децибелів ще не було (done-стаття).
2. own:propagation-modes — режими поширення (перенесено з №17 на початок).
3. ref:communications/free-space-loss — ДОДАТИ: загасання у вільному просторі — фізична основа бюджету (done).
4. ref:communications/multipath-fading — ДОДАТИ: багатопроменевість/завмирання — без неї ITU-R-моделі і FPV-флікер незрозумілі (done).
5. ref:communications/ism-bands — ДОДАТИ: чому ESP32 живе у 2.4 ГГц; правила безліцензійних смуг (стаття існує, basic pending).

Пререквізити ззовні: osnovy/frequency-wavelength (спектр, done) — виконано.

### R2. Модуляція: дані сідають на хвилю (5)
1. ref:communications/why-modulation — ДОДАТИ (done).
2. ref:communications/am-fm — ДОДАТИ (done).
3. ref:communications/fsk-psk — ДОДАТИ: цифрові модуляції — база для 802.11/LoRa/BLE (done).
4. ref:communications/ofdm — ДОДАТИ: без OFDM стандарти 802.11a…7 — магія (стаття існує, pending).
5. ref:communications/spread-spectrum — ДОДАТИ: FHSS/DSSS — прямий пререквізит jamming-fhss (done).

### R3. Антени: від диполя до друкованої (7)
1. ref:communications/antenna — ДОДАТИ: що взагалі таке антена (done).
2. ref:communications/resonance-dipole — ДОДАТИ: резонанс і чвертьхвильова довжина → звідки розміри антени ESP32 (done).
3. ref:communications/antenna-gain — ДОДАТИ: підсилення — доданок бюджету лінка (done).
4. ref:communications/antenna-polarization — ДОДАТИ: поляризація — критично для FPV-антен (done).
5. ref:communications/vswr — ДОДАТИ: відбиття і КСХ — метрика узгодження перед π-match (done; спирається на kola/impedance-matching-networks і cyfra-pamyat/transmission-lines — обидва вже пройдено).
6. own:esp32-antenna — тепер має всі пререквізити.
7. own:pcb-antenna-layout — одразу після антени ESP32, а не через 5 тем.

### R4. Радіотракт і модуль (4)
1. own:rf-frontend — PA/LNA/перемикач/балун (перенесено з №22 до антен).
2. ref:communications/superheterodyne — ДОДАТИ: як приймач витягує сигнал; класика архітектури (done).
3. own:esp32-module — модуль як готовий радіотракт під бляшанкою.
4. own:frequency-budget-analysis — дрейф опорника → чи влучаємо у свій канал (спирається на komponenty/tcxo-ocxo — пройдено).

### R5. Бюджет лінка і живучість (4)
1. own:link-budget — тепер після dB, загасання, антен і тракту — все зійшлось.
2. ref:communications/rssi-signal-strength — ДОДАТИ: виміряти рівень і звірити з розрахунком (стаття існує, pending).
3. own:itu-r-propagation-models — уточнені моделі ПІСЛЯ фізики поширення (R1) і базового бюджету.
4. own:jamming-fhss — вінець блоку: бюджет + розширений спектр (R2.5) → лінк під глушінням.

### R6. Ділимо ефір: Wi-Fi і Bluetooth (7)
1. own:multiple-access-methods — TDMA/FDMA/CDMA/CSMA — база для всіх стандартів.
2. ref:communications/wifi — ДОДАТИ: що таке Wi-Fi (AP/STA, канали) перед еволюцією стандартів (done).
3. own:802-11-versions — тепер після Wi-Fi-вступу, модуляції й OFDM.
4. ref:communications/wpa-security — ДОДАТИ: WPA2/WPA3 і PMK — прямий пререквізит наступного кроку (стаття існує, pending).
5. own:wifi-fast-connect — MOVE_IN із mk: кешування PMK/IP — Wi-Fi-матерія, а не «мікроконтролер».
6. ref:communications/bluetooth-spp — ДОДАТИ: у курсі про ESP32 немає жодного Bluetooth (done).
7. ref:communications/ble-gatt — ДОДАТИ: BLE — головний IoT-протокол ближнього радіуса (done).

### R7. IoT-радіо: mesh, LPWAN, мітка (4)
1. own:thread-matter-zigbee
2. own:lpwan
3. ref:communications/lora — ДОДАТИ: конкретика LoRa одразу після огляду LPWAN (done).
4. own:nfc-rfid — ближнє поле як окремий вид бездротового зв'язку; сюди, а не між антеною і модулем ESP32.

### R8. Пакети, мережа, надійність (9)
1. ref:communications/channel-band-packet — ДОДАТИ: ідея пакета — вхідні ворота всього розділу (done).
2. ref:communications/packet-design — ДОДАТИ: кадр, заголовок, CRC-поле (done; перевірити перетин із data-reliability).
3. own:data-reliability — контрольні суми/цілісність (перенесено з №2).
4. own:arq-strategies — повтори; тепер одразу після своєї бази.
5. ref:communications/mac-ip-arp — ДОДАТИ: адресація перед маршрутизацією (done).
6. ref:communications/ip-routing — маршрутизація (перенесено з №1 на своє місце).
7. ref:communications/tcp-vs-udp — ДОДАТИ: без TCP/UDP не читаються ані pymavlink (UDP), ані відеострімінг (done).
8. ref:communications/mqtt — ДОДАТИ: головний IoT-протокол застосункового рівня; курс ESP32 без MQTT неповний (done basic+detailed).
9. own:rpc-embedded — виклик процедур поверх транспорту — завершує драбину.

### R9. Канали дрона: RC і MAVLink (6)
1. ref:communications/control-telemetry — ДОДАТИ: огляд каналів «керування й телеметрія» — рамка розділу (done).
2. ref:communications/rc-link — ДОДАТИ: RC-пульт (S.BUS тощо) — у курсі про дрони немає взагалі (done).
3. ref:communications/mavlink-packet — ДОДАТИ: структура пакета MAVLink перед роботою з командами (done).
4. own:mavlink-commands — MOVE_IN із mk: команди/ACK — це протокол зв'язку, і його місце в нитці MAVLink.
5. own:mavlink-from-ground
6. own:pymavlink

### R10. Відеолінк (5)
1. ref:communications/video-transmission — ДОДАТИ: огляд «відео по радіо» (done).
2. ref:communications/analog-video — ДОДАТИ: аналоговий відеосигнал — база половини FPV-світу (done).
3. own:mjpeg-vs-h264 — MOVE_IN із drony: кодек мусить передувати протоколам стрімінгу, а не йти в наступній секції.
4. own:fpv-video-systems — аналог vs цифра: тепер обидві половини пояснені.
5. own:video-streaming-protocols — RTP/RTSP/WebRTC/SRT поверх TCP/UDP (R8) і кодеків.

Разом 56 кроків. Усі 22 поточні теми модуля збережені; move_out — немає; move_in — 3; доданих ref — 31, new — 0.

## 4. move_out / move_in

**move_out: порожньо.** Усі 22 теми — про зв'язок; безлад був у порядку, не в приналежності.
(rpc-embedded розглядався як кандидат у proshyvka, але в розділі «Пакети, мережа, надійність» він
закриває драбину «біти → пакети → транспорт → виклик процедури» — лишається.)

**move_in (3):**
1. own:mavlink-commands ← mk. У mk стоїть посеред архітектури МК; тут складає цільну нитку
   пакет → команди → із землі → pymavlink.
2. own:wifi-fast-connect ← mk. PMK/WPA-кешування — Wi-Fi-матерія; у mk стояла за 6 секцій до першого
   пояснення Wi-Fi.
3. own:mjpeg-vs-h264 ← drony. Кодек — ланка ланцюга передачі відео; video-streaming-protocols без нього
   непрохідний (зараз кодек пояснюється ПІЗНІШЕ за протоколи його передачі).

## 5. Прогалини (missing) — усі закриваються книгою communications, new не потрібен

Ключовий факт: **26 із 31 доданої теми вже написані (basic done)** у book/communications, ще 5 існують
у маніфесті зі статусом pending (ism-bands, ofdm, rssi-signal-strength, wpa-security — плюс 27 done).
Тобто прогалини модуля — не «треба писати», а «треба залучити готове».

Для новачка (без стіни незнаного): power-decibels, why-modulation, am-fm, fsk-psk, spread-spectrum,
antenna, resonance-dipole, antenna-gain, vswr, channel-band-packet, mac-ip-arp, tcp-vs-udp, wifi.
Для повного покриття теми модуля: free-space-loss, multipath-fading, ism-bands, ofdm,
antenna-polarization, superheterodyne, rssi-signal-strength, wpa-security, bluetooth-spp, ble-gatt,
lora, packet-design, mqtt, control-telemetry, rc-link, mavlink-packet, video-transmission, analog-video.

Свідомо НЕ додано (щоб не роздувати): communications/esp-now (pending; природний бонус після BLE),
communications/fresnel-zones, noise-figure, csma-ca, reliable-link (перетинається з arq-strategies),
friis-transmission (Friis уже у вставках esp32-antenna/rf-frontend).

## 6. Органічність ref/own

- Зараз модуль — 21 own і 1 ref: курс сам понаписував статті там, де в book лежать готові атоми, і
  водночас не залучив атомів для власного фундаменту. Єдиний ref (ip-routing) стоїть без мосту, першим
  кроком — антиприклад вписаного ref-а.
- Цільова структура створює в R2 (модуляція: 5 ref поспіль) і R8 (по 2–3 ref поспіль) щільні ref-ланцюги.
  Для guide це прийнятно, якщо розділи мають короткі власні підводки; альтернатива — написати власну
  оглядову статтю-міст «модуляція очима ESP32», яка зшиває why-modulation → fsk-psk, і тоді am-fm/ofdm
  лишити довідковими ref. Вирішувати на етапі написання.
- own, які за природою — book-атоми: itu-r-propagation-models і multiple-access-methods (обидві
  довідково-атомні, могли б жити в communications/propagation і /multiple-access). Уже написані як own
  (done) — переносити не варто, але на майбутнє такі теми краще класти в book і посилатись.
- pymavlink: аудиторія «нуль програмування», а Python у курсі й у book/programming не вводиться ніде
  (grep порожній). Стаття мусить сама давати мінімальний старт (перевірити при recheck) — інакше це
  прихована стіна.

## 7. Модуль як ціле

- **Назва «Звʼязок і радіо» влучна** для поточного набору, але після реструктуризації модуль фактично
  розпадається на два природні модулі:
  **(А) «Радіо: від хвилі до стандартів»** = R1–R7 (~36 кроків: ефір, модуляція, антени, тракт, бюджет,
  Wi-Fi/BLE, IoT-радіо) і **(Б) «Мережі, телеметрія і відео дрона»** = R8–R10 (~20 кроків: пакети/IP/
  транспорт, RC/MAVLink, відеолінк). Рекомендую різати: 56 кроків для одного модуля забагато, а шов
  R7/R8 — природна межа «ефір ↔ дані».
- **Місце в курсі (13-та секція з 14) правильне**: спирається на osnovy (частота/довжина хвилі, шум),
  kola (узгодження імпедансів), komponenty (кварци TCXO/OCXO), cyfra-pamyat (лінії передачі), mk
  (ESP32), peryferiia (UART/RS-485) — і безпосередньо готує drony (відеолінк, RC, MAVLink переходять у
  автономність). Якщо різати на А/Б — обидва лишаються між keruvannia і drony в цьому ж порядку.
- Після move_in секція mk позбувається двох чужорідних тем, drony віддає кодек, але отримує повністю
  підготовленого читача (відеолінк уже пояснений).
