# Том 5. Комунікація

**13 розділів · 143 кроки · 21 власна стаття курсу**

> Розкладку звірено з **оновленим резервом (3676 статей)**: разом із каталогом і з темами
> `[pending]` — тими, що вже заведені в маніфесті, але ще не написані. Адреса в них є, тож
> `ref` туди законний, а вигадувати на те саме нову тему — ні. Через це три мої `НОВА`
> й чотири власні статті скасовано на користь наявних адрес — див. §4.

Дріт між пристроями · Кадр і підтвердження · Локальна мережа · Стек IP · Радіоканал ·
Спільний ефір · Радіомодулі · Зв'язок із телефоном · Wi-Fi · Пристрій і сервер ·
Мережі операторів · Життя з'єднання · Свій протокол

---

## Головне рішення тому: спершу дріт, і не лише заради кадру

Том 4 закінчився шиною **на платі**: один господар, спільна земля, тридцять сантиметрів,
ведений, який не сміє заговорити першим. Том 5 починається там, де на іншому кінці —
**інший пристрій**: своє живлення, свій кварц, свій господар, іноді кілометри, іноді
середовище, яке губить пакети й ділиться з чужими.

Попередній прохід дійшов правильного висновку: **логіку обміну вчать на дроті**. Кадр,
контрольна сума, підтвердження, повтор, номер послідовності однакові на RS-485, у LoRa
і в TCP, і найдешевше вони вивчаються там, де середовище не бреше, а логічний аналізатор
показує кожен біт. Я цей висновок беру — і **продовжую його на два розділи далі**.

Попередній прохід зупинив «дріт» на кадрі й повів читача в ефір, а Ethernet із IP лишив
аж за Wi-Fi. Виходило, що читач приєднується до точки доступу в розділі 8, а надіслати
байт уміє з розділу 10 — два розділи «приєднаний, але німий». Тут інакше: **на дроті
вивчається і кадр, і вся IP-мережа**. Ethernet або працює, або не працює; кабель не
завмирає, не ділить смугу з сусідом і не гріється на сонці. Читач розбирається з адресою,
маскою, DHCP, DNS, TCP, сокетом і NAT там, де жодна невдача не має двох пояснень.

Аж тоді — ефір, який додає рівно дві речі: **середовище губить** і **середовище спільне**.
І коли приходить Wi-Fi, він додає до вже знайомого стека рівно одне: приєднання до чужої
точки та ефір над ним. Наступний розділ одразу дає розплату — пристрій говорить із
сервером.

Драбина тому — п'ять блоків:

| блок | розділи | що додає |
|---|---|---|
| **А. Дріт** | 1–2 | обмін як домовленість, на середовищі, яке не бреше |
| **Б. Мережа на дроті** | 3–4 | адреси, маршрут, з'єднання, сокет — теж без брехні середовища |
| **В. Ефір** | 5–7 | фізика, спільність, закон і перший власний радіоканал |
| **Г. Чужі кінці** | 8–11 | телефон, точка доступу, сервер, мережа оператора |
| **Ґ. Будні** | 12–13 | що робить лінк, коли ламається, і як спроєктувати свій |

Том закінчується не технологією, а вмінням: читач має власний протокол між власними
пристроями і знає, що робить кожен із них, коли роутер перезавантажили на дві хвилини.

**Про вагу.** 143 кроки — це багато, і це навмисно. Начерк автора складає в цей том
«радіо, вайфай, інтернет, локальні мережі», тобто чотири самостійні світи; на нього
прямо спираються том 9 (лінк під глушінням), том 10 (IoT), том 11 (дрони) і том 12
(віддалене керування). Якщо том усе-таки треба полегшити, є два чесні різи, і обидва
названо в §6 «Заперечення»: злити розділи 3–4 в один (мінус ~8 кроків) і віддати розділ
13 томові 10 (мінус 8).

---

# 1. Розділи тому

## Розділ 1. Дріт між пристроями — 11 кроків
Що ставлять замість UART, коли до співрозмовника не тридцять сантиметрів, а сто метрів:
диференційна пара, RS-485, CAN, термінація, розв'язка, кабель і земля, якої немає.
**Спирається на:** том 2 (лінія передачі, наводки, імпеданс), том 3–4 (UART, рівні,
логічний аналізатор, даташит чужої мікросхеми).

## Розділ 2. Кадр і підтвердження — 12 кроків
Домовленість, яка перетворює потік байтів на повідомлення й доставляє його попри помилки:
кадрування, CRC, адреса, підтвердження, повтор, номер, керування потоком — на прикладі
Modbus і CANopen, і потім свого власного кадру.
**Спирається на:** розділ 1 (є фізичний канал), том 3 (переривання, буфери, кільцева черга).

## Розділ 3. Локальна мережа — 9 кроків
Ethernet як провідний канал вбудованого вузла: кадр, MAC, комутатор, автопогодження, PoE
і те, як PHY чіпляється до мікроконтролера.
**Спирається на:** розділи 1–2 (диференційна фізика, кадр і контрольна сума).

## Розділ 4. Стек IP — 15 кроків
Пристрій як вузол мережі: адреса й маска, DHCP, DNS, маршрут, UDP і TCP, сокет, MTU, NAT —
і скільки все це коштує в кілобайтах RAM.
**Спирається на:** розділ 3 (є лінк, який не губить), том 3 (задачі, черги, пам'ять).

## Розділ 5. Радіоканал — 12 кроків
Уся фізика, яку том несе з собою: хвиля, діапазон, антена, узгодження, загасання,
багатопроменевість, чутливість і бюджет лінка, що закінчується числом у децибелах.
**Спирається на:** том 1–2 (поле, резонанс, децибели, фільтри), розділ 1 (лінія передачі
й відбиття — те саме, тільки тепер навмисне).

## Розділ 6. Спільний ефір — 11 кроків
Чому ефір — не дріт: модуляція як плата за дальність, розширений спектр і стрибки,
хто говорить зараз, і закон, який визначає потужність та робочий цикл.
**Спирається на:** розділ 5 (є канал і бюджет), розділ 2 (є ARQ — тепер зрозуміло, навіщо).

## Розділ 7. Радіомодулі — 11 кроків
Готовий модуль у руках: даташит, обв'язка, канал і адреса, LoRa проти 2,4 ГГц, перший
власний радіоканал тим самим кадром із розділу 2 — і криптомінімум, бо цей канал зараз
повторить будь-хто.
**Спирається на:** розділи 2, 5, 6 (кадр, бюджет, закон ефіру).

## Розділ 8. Зв'язок із телефоном — 9 кроків
BLE від реклами до GATT, спарювання, маячки, ціна інтервалу з'єднання, телефон як другий
кінець і NFC як спосіб з'єднати дотиком.
**Спирається на:** розділ 7 (модуль, канал, ключ), розділ 2 (характеристика — та сама
регістрова карта, тільки віддалена).

## Розділ 9. Wi-Fi — 11 кроків
Найскладніше радіо тому й водночас двері в уже вивчену IP-мережу: приєднання, WPA2/WPA3,
канали, провізіонування, споживання і реальна пропускна.
**Спирається на:** розділ 4 (весь стек уже відомий), розділи 5–6 (чому крізь дві стіни
не працює), розділ 7 (ключ і тег), розділ 8 (провізіонування через BLE).

## Розділ 10. Пристрій і сервер — 12 кроків
Розплата за попередні дев'ять розділів: асиметрична крипта, TLS, час, HTTP, MQTT, CoAP,
формат повідомлення — пристрій, який доповідає в інтернет і слухає команди.
**Спирається на:** розділ 4 (сокет, DNS, NAT), розділ 7 (симетрична крипта), розділ 9
(канал до роутера).

## Розділ 11. Мережі операторів — 11 кроків
Коли покриття не будують, а орендують: LoRaWAN, стільниковий модем, SIM і APN, NB-IoT,
супутниковий канал — і підсумковий вибір каналу під задачу.
**Спирається на:** розділи 5–7 (радіо й модуль), розділ 10 (є що передавати й куди).

## Розділ 12. Життя з'єднання — 11 кроків
Що робить пристрій, коли зв'язку немає: автомат стану, виявлення обриву, відступ, черга
офлайну, дублікати, час без годинника, деградація, перемикання каналу — і чим у канал
подивитися.
**Спирається на:** усі попередні розділи; це перший розділ тому, де жоден канал не новий.

## Розділ 13. Свій протокол — 8 кроків
Капстоун: набір повідомлень, порядок байтів, версія і сумісність, виявлення, автентичність,
специфікація як документ і стенд, який ламає протокол навмисно.
**Спирається на:** розділ 2 (кадр), розділи 7–11 (п'ять чужих протоколів у розборі),
розділ 12 (обриви й дублікати як вимога до дизайну).

---

# 2. Розкладка

Позначки: `наявна` — курс уже веде в цю тему (у дужках — шлях `ref` або «курсова», якщо
це власна стаття курсу) · `+ref` — написана стаття з резерву (`pool-embedded.md`) ·
`кандидат` — тема з `newtopics-embedded.md` · `НОВА` / `ВЛАСНА` — писати.

## Розділ 1. Дріт між пристроями

1. **Де вмирає шина з плати** — `+ref communications/buses/single-ended-line-limits`
2. **Диференційна пара і вита пара** — наявна (`communications/buses/differential-pair`) ·
   `+ref electronics/pcb/twisted-pair`
3. **RS-485 і RS-422** — наявна (`communications/buses/rs-485`) ·
   `+ref communications/interfaces/rs422-rs485` · `+ref communications/buses/rs-422`
4. **Термінація і відбиття в кабелі** — `+ref communications/buses/termination`
5. **Напівдуплекс: хто керує напрямком** — `+ref communications/buses/half-duplex-uart`
6. **Земля, якої немає: спільна земля й земляні петлі** — наявні
   (`electronics/pcb/common-ground`, `electronics/pcb/ground-loops`) — *переїзд із блоку
   плат: тут вони вперше кусають*
7. **Гальванічна розв'язка** — `+ref electronics/digital/digital-isolator`
8. **Кабель, екран, ферит** — наявна (`electronics/pcb/shielding`) ·
   `+ref electronics/pcb/shielded-cable` · `+ref electronics/pcb/ferrite-clamp` ·
   `+ref electronics/pcb/cable-emi` `[pending]` ·
   `+ref electronics/pcb/hybrid-shield-grounding` `[pending]` ·
   `+ref electronics/pcb/cables-connectors` `[pending]` ·
   `+ref КАТАЛОГ components/connectors/jst-gh-cable`
9. **CAN: шина, арбітраж, кадр помилки** — наявна (`communications/buses/can-arbitration`) ·
   `+ref communications/protocols/can-bus` · `+ref communications/buses/can-frame-errors`
10. **Струмова петля 4–20 мА і LIN: дріт там, де завади сильніші за дані** —
    `+ref communications/interfaces/current-loop` · `+ref communications/protocols/lin-bus`
11. **ВЛАСНА «Лінія на сто метрів: збираємо RS-485 і ламаємо її»** — той самий кабель без
    термінації, без спільної землі, з мотором поруч; осцилограф показує чому.

## Розділ 2. Кадр і підтвердження

1. **Потік байтів проти повідомлення** — `+ref programming/embedded-systems/stream-parser`
2. **Кадрування: маркер, стафінг, COBS, SLIP** — `+ref communications/protocols/cobs-framing` ·
   `+ref communications/protocols/slip-protocol`
3. **Проєктування пакета** — наявна (`communications/protocols/packet-design`)
4. **Контрольна сума і CRC** — наявна (`communications/coding-theory/crc`) ·
   `+ref communications/coding-theory/checksums` ·
   `+ref communications/coding-theory/internet-checksum` ·
   `+ref programming/embedded-systems/crc-in-firmware`
5. **Коли повтор задорогий: коди, що виправляють** — `кандидат` «Коди з виправленням
   помилок» · `+ref communications/networks/fec-codes` ·
   `+ref communications/coding-theory/hamming-code` ·
   `+ref communications/coding-theory/burst-error` ·
   `+ref communications/coding-theory/interleaving`
6. **Рівні: чому обмін розкладають шарами** — `+ref communications/protocols/osi-model`
7. **Підтвердження й повтор: ARQ** — наявна («Стратегії ARQ», курсова) ·
   `+ref communications/reliability/arq` · `+ref communications/protocols/arq-protocol` ·
   `+ref communications/protocols/sliding-window-arq`
8. **Номер послідовності, дублікати, безлад** —
   `+ref communications/protocols/sequence-numbering` ·
   `+ref programming/distributed-systems/delivery-guarantees` ·
   `+ref programming/distributed-systems/out-of-order-tolerance`
9. **Таймаут як частина протоколу** — `+ref programming/distributed-systems/timeouts-deadlines`
10. **Керування потоком і надійний обмін** — наявні
    (`communications/protocols/flow-control`, `communications/protocols/reliable-link`,
    «Надійність даних» курсова)
11. **Чужий протокол у розборі: Modbus RTU і CANopen** —
    `+ref communications/protocols/modbus` · `+ref communications/protocols/can-open`
12. **ВЛАСНА «Свій кадр між двома платами»** — структура, CRC, ACK, повтор, номер;
    аналізатор поруч; навмисно битий байт.

## Розділ 3. Локальна мережа

1. **Кадр Ethernet** — `+ref communications/networks/ethernet-frame`
2. **Фізика лінка: пари, магнітка, швидкості** —
   `+ref communications/networks/ethernet-link-phy` ·
   `+ref communications/buses/usb-ethernet-differential`
3. **Кабель і роз'єм** — `+ref communications/networks/utp-cable` ·
   `+ref КАТАЛОГ components/cables/ethernet-cable`
4. **Автопогодження, дуплекс, MDI/MDI-X** — `+ref communications/networks/auto-negotiation` ·
   `+ref communications/networks/mdi-mdix`
5. **Комутатор і широкомовний домен; куди поділися колізії** —
   `+ref communications/networks/csma-cd`
6. **PoE: живлення тією самою парою** — `+ref communications/networks/poe`
7. **Ethernet на МК: MAC, PHY, RMII, MDIO** —
   `+ref programming/embedded-systems/ethernet-on-mcu` · `+ref communications/buses/mdi-mdio-bus`
8. **VLAN: два світи в одному дроті** — `+ref communications/networks/vlan-and-trunking`
9. **Петля в мережі й STP** — `+ref communications/networks/stp-rstp`

## Розділ 4. Стек IP

1. **MAC, IP і ARP** — `кандидат` «IP, DHCP і DNS» · `+ref communications/networks/mac-ip-arp`
2. **Адреса, маска, префікс** — `+ref communications/networks/subnet-addressing` ·
   `+ref communications/networks/cidr`
3. **DHCP: адреса, якої ти не призначав** — `+ref communications/networks/dhcp` ·
   `+ref communications/networks/dhcp-dns`
4. **DNS: ім'я замість числа** — `+ref communications/networks/dns-srv-naptr`
5. **Маршрутизація** — наявна (`communications/networks/ip-routing`)
6. **TCP проти UDP, семантика датаграми** — наявні (`communications/protocols/tcp-vs-udp`,
   `programming/networking/udp-datagram-semantics`)
7. **Життєвий цикл TCP-з'єднання** — `+ref communications/protocols/tcp-connection-lifecycle`
8. **Кадрування повідомлень у TCP** — наявна (`programming/networking/tcp-message-framing`)
9. **Сокети й опції сокета** — наявні (`programming/networking/sockets-tcp-udp`,
   `programming/networking/socket-options`) · `+ref programming/networking/socket-api` `[pending]`
10. **MTU, фрагментація і чому «воно працює до 1400 байтів»** —
    `+ref communications/networks/mtu-and-fragmentation`
11. **NAT: чому до пристрою не достукатися** — `+ref communications/networks/nat` ·
    `+ref communications/protocols/nat-traversal` · `+ref communications/networks/middleboxes`
12. **Затримка, джитер, черги** — `+ref communications/networks/jitter` ·
    `+ref communications/networks/queue-theory-networks` ·
    `+ref communications/networks/latency-reliability` ·
    `+ref communications/networks/bandwidth-loss`
13. **Дрібні пакети й мовчазна мережа: Нейгл, відкладене ACK, помилки ICMP** —
    `+ref programming/networking/nagle-and-delayed-ack` `[pending]` ·
    `+ref programming/networking/icmp-errors-in-code` `[pending]`
14. **Виявлення сусіда: багатоадресна розсилка, mDNS і DNS-SD** — наявна
    (`programming/networking/multicast-and-discovery`) ·
    `+ref programming/networking/mdns-dns-sd` `[pending]`
15. **Стек на 300 КБ RAM: lwIP, буфери, скільки сокетів** —
    `+ref programming/networking/lwip-internals` `[pending]`
    *(тут була моя ВЛАСНА — адреса вже існує, скасовано)*

*(3–4 і 12–13 у письмі, найімовірніше, зіллються в пари)*

## Розділ 5. Радіоканал

1. **Електромагнітна хвиля: чому струм відривається від дроту** —
   `+ref physics/electromagnetism/em-wave` · `+ref physics/electromagnetism/hertz-dipole` ·
   `+ref physics/electromagnetism/radiation-zones`
2. **Діапазони: що дає 433, 868, 2400, 5800** —
   `+ref communications/propagation/frequency-bands`
3. **Децибели як робоча одиниця** — наявна (`communications/propagation/power-decibels`) ·
   `+ref communications/propagation/db-reference-variants`
4. **Антена: залізо, яке стало хвилею** — наявна (`communications/antennas/antenna`) ·
   `+ref communications/antennas/resonance-dipole` ·
   `+ref communications/antennas/radiation-resistance`
5. **Підсилення, діаграма, поляризація** — наявна (`communications/antennas/antenna-gain`) ·
   `+ref communications/antennas/directivity` ·
   `+ref communications/antennas/radiation-pattern-3d` ·
   `+ref communications/antennas/antenna-polarization` ·
   `+ref communications/antennas/circular-polarization`
6. **Узгодження, КСХ, балун** — `кандидат` «КСХ, зворотні втрати й вимірювання антени» ·
   `+ref communications/antennas/antenna-impedance-matching` ·
   `+ref communications/radio-engineering/vswr` ·
   `+ref communications/radio-engineering/return-loss` ·
   `+ref communications/radio-engineering/balun`
7. **Антена на власній платі** — наявні («Антена ESP32», «Топологія антени на PCB»,
   курсові) · `+ref electronics/pcb/pcb-stackup-rf` ·
   `+ref electronics/radio/wavelength-in-medium`
8. **Загасання у просторі й рівняння Фрііса** —
   `+ref communications/propagation/free-space-loss` ·
   `+ref communications/propagation/friis-transmission`
9. **Зони Френеля й перешкода на шляху** — наявна («Режими поширення радіохвиль», курсова) ·
   `+ref communications/propagation/fresnel-zones` ·
   `+ref communications/propagation/atmospheric-absorption`
10. **Багатопроменевість і завмирання** — `+ref communications/propagation/multipath-fading` ·
    `+ref communications/propagation/fading-statistics` ·
    `+ref communications/propagation/delay-spread`
11. **Чутливість, шум, запас: бюджет лінка як число** — наявні («Бюджет лінії»,
    «Частотний бюджет у системах зв'язку», курсові) ·
    `+ref communications/propagation/link-budget` *(глибша версія: шумовий поріг,
    коефіцієнт шуму, SNR, запас на завмирання — усе, чого бракувало курсовій)* ·
    `+ref communications/propagation/rssi-signal-strength` ·
    `+ref communications/propagation/link-quality-metrics` ·
    `+ref communications/information-theory/awgn-channel`
12. **ВЛАСНА «Дальність у полі»** — як міряти, що записувати, чому вийшло втричі менше
    за обіцяне в даташиті.

## Розділ 6. Спільний ефір

1. **Навіщо модуляція** — наявна (`communications/modulation/why-modulation`)
2. **AM і FM** — наявна (`communications/modulation/am-fm`)
3. **FSK, PSK та IQ-подання** — наявна (`communications/modulation/fsk-psk`) ·
   `+ref communications/modulation/iq-representation` · `+ref communications/modulation/qam`
4. **Швидкість, смуга, чутливість: за що платиш дальністю** —
   `+ref communications/information-theory/bandwidth-capacity` ·
   `+ref communications/networks/shannon-capacity` ·
   `+ref communications/coding-theory/ber-snr-curve` ·
   `+ref communications/modulation/adaptive-modulation`
5. **Розширений спектр і чирп** — наявна (`communications/modulation/spread-spectrum`) ·
   `+ref communications/signal-processing/pn-sequences` ·
   `+ref communications/modulation/chirp-coding`
6. **Стрибки частоти й синхронізація** — `+ref communications/modulation/fhss-sync`
7. **Хто говорить зараз: множинний доступ і CSMA/CA** — наявна («Методи множинного
   доступу», курсова) · `+ref communications/networks/csma-ca` ·
   `+ref communications/multiple-access/cdma` · `+ref communications/multiple-access/ofdma`
8. **Дуплекс і захисні смуги** — `+ref communications/networks/guard-band-duplexing`
9. **ISM-діапазони й правила ефіру: смуга, потужність, робочий цикл** — `кандидат`
   (назвали тричі) · `+ref communications/propagation/ism-bands` ·
   `+ref communications/radio-engineering/time-on-air`
10. **Сертифікація радіо** — `+ref communications/protocols/regulatory-radio-certification` ·
    наявна («Модульна сертифікація: FCC, CE та EMC-випроби» —
    `communications/radio-engineering/emc-certification`)
11. **ВЛАСНА «Співіснування 2,4 ГГц і власна самоперешкода»** — Wi-Fi, BLE й пульт в одній
    смузі; імпульсний перетворювач і USB-3 на твоїй же платі як найближча глушилка ·
    `+ref electronics/pcb/electromagnetic-compatibility` `[pending]` ·
    `+ref electronics/metrology/near-field-probing` `[pending]` *(чим це видно)*

## Розділ 7. Радіомодулі

1. **Радіомодуль: що всередині й що в даташиті** —
   `+ref communications/radio-engineering/rf-module` · наявна («RF-тракт: підсилювачі,
   перемикач і балун», курсова) · `+ref communications/networks/on-chip-radio` ·
   `+ref electronics/radio/rf-board-reading` · `+ref communications/radio-engineering/rf-amplifiers` ·
   `+ref programming/embedded-systems/nrf-radio-mcu` *(радіо як периферія МК)*
2. **Пропрієтарні 2,4 ГГц: nRF24 і його труби** — `+ref КАТАЛОГ connect/radio/nrf24-radio`
3. **ESP-NOW: пакет без мережі** — наявна (`communications/networks/esp-now`)
4. **Sub-GHz: чому 868 далі за 2400** — `+ref communications/networks/channel-band-packet`
5. **LoRa: SF, BW, CR і час у ефірі** — `+ref communications/radio-engineering/lora` ·
   `+ref КАТАЛОГ connect/radio/lora-module` · наявна («LPWAN», курсова)
6. **Керування модулем: AT-порт проти регістрів по SPI** —
   `+ref КАТАЛОГ connect/radio/bluetooth-hc05` *(як зразок AT-модуля)*
7. **ВЛАСНА «Перший радіоканал на двох платах»** — той самий кадр із розділу 2 поверх
   модуля; що зламалося саме через ефір, а що — через код.
8. **Готовий телеметрійний лінк: що купують для апарата** —
   `+ref КАТАЛОГ connect/radio/fpv-telemetry-air` ·
   `+ref КАТАЛОГ connect/radio/fpv-telemetry-ground`
9. **Імпульс передавача: 120 мА на 10 мс і скид МК** —
   `+ref programming/embedded-systems/peak-current-budgeting` `[pending]`
   *(тут була моя ВЛАСНА — адреса вже існує, скасовано; рахунки енергії — том 6)*
10. **ВЛАСНА «Криптомінімум пристрою»** — `кандидат` (назвали п'ять джерел) — геш, код
    автентичності, симетричний шифр, одноразове число, джерело випадковості; складає
    докупи атоми, зокрема ті, що вже мають адресу:
    `+ref math/number-theory/cryptographic-hash-functions` ·
    `+ref algorithms/cryptographic-algorithms/keyed-hash-mac` `[pending]` ·
    `+ref algorithms/cryptographic-algorithms/block-cipher` `[pending]` ·
    `+ref algorithms/cryptographic-algorithms/stream-cipher` `[pending]` ·
    `+ref algorithms/cryptographic-algorithms/diffie-hellman` `[pending]` ·
    `+ref algorithms/cryptographic-algorithms/entropy-source` `[pending]` ·
    `+ref algorithms/cryptographic-algorithms/csprng` ·
    `+ref communications/cryptographic-comm/hmac` ·
    `+ref communications/cryptographic-comm/aead` ·
    `+ref programming/security/key-derivation-function` `[pending]`
    *(обидві мої `НОВА` — «симетричний шифр» і «обмін ключами» — скасовано: адреси є)*
11. **ВЛАСНА «Захист власного радіоканалу: ключ, лічильник, тег»** — `кандидат` «Захист
    бездротового каналу» · `+ref programming/security/replay-protection` ·
    `+ref communications/cryptographic-comm/challenge-response` ·
    `+ref communications/cryptographic-comm/authenticated-encryption`

## Розділ 8. Зв'язок із телефоном

1. **Bluetooth і BLE: два різні світи** — `кандидат` «Bluetooth і BLE: стек, ролі, реклама» ·
   `+ref communications/networks/bluetooth-classic-stack` ·
   `+ref communications/networks/bluetooth-spp` · `+ref communications/networks/rfcomm`
2. **Реклама й ролі: GAP** — `+ref communications/protocols/ble-gap`
3. **Канальний рівень: стрибки й події з'єднання** —
   `+ref communications/protocols/ble-link-layer`
4. **ATT і GATT: віддалена регістрова карта** — наявна (`communications/protocols/ble-gatt`) ·
   `+ref communications/protocols/ble-att` ·
   `+ref programming/embedded-systems/ble-gatt-practice` `[pending]`
5. **Спарювання, прив'язка, приватність** — `+ref communications/protocols/ble-security` ·
   `+ref communications/networks/bt-pairing-security`
6. **Маячки: передати, не з'єднуючись** — `+ref communications/protocols/ble-beacon-formats`
7. **ВЛАСНА «Інтервал з'єднання проти батареї»** — connection interval, latency, MTU:
   як три числа вирішують і швидкість, і місяці роботи.
8. **ВЛАСНА «Телефон як другий кінець»** — застосунок, дозволи, фонові обмеження,
   Web Bluetooth · `+ref programming/client-architecture/android-app-model`
9. **NFC: з'єднати дотиком** — наявна («NFC/RFID», курсова) ·
   `+ref communications/radio-engineering/nfc-protocols`

## Розділ 9. Wi-Fi

1. **Wi-Fi: точка доступу, STA, приєднання** — наявна (`communications/networks/wifi`)
2. **Стандарти й канали: 2,4 проти 5 ГГц** — наявна («Стандарти 802.11: від b/g/n до
   Wi-Fi 7», курсова) · `+ref communications/radio-engineering/wifi-6-basics` ·
   `+ref communications/modulation/ofdm` · `+ref communications/multiple-access/mimo`
3. **WPA2 і WPA3** — `+ref communications/networks/wpa-security` *(спирається на
   криптомінімум із розділу 7)*
4. **Відкрита точка й чому це дірка** — `+ref communications/networks/arp-security`
5. **Швидке підключення: кеш PMK і IP** — наявна («Швидке підключення Wi-Fi», курсова)
6. **Пристрій без клавіатури: SoftAP і BLE-провізіонування** — наявна («Перше налаштування
   пристрою», курсова)
7. **ВЛАСНА «Captive portal і своя сторінка налаштувань»** — пристрій як точка доступу,
   форма, збереження в NVS, перехід у STA.
8. **Скільки коштує Wi-Fi: DTIM, сон, час у ефірі** —
   `+ref programming/embedded-systems/wi-fi-power-modes` `[pending]`
   *(тут була моя `НОВА` — адреса вже існує, скасовано)*
9. **Рух між точками доступу** — `НОВА` «Роумінг у 802.11: 802.11k, 802.11v, 802.11r»
10. **Wi-Fi-чип як периферія до чужого МК** — `+ref programming/networking/esp-hosted`
11. **ВЛАСНА «Wi-Fi у полі»** — вибір каналу, стіни, реальна пропускна на МК, чому
    «5 ГГц швидший» тут неправда.

## Розділ 10. Пристрій і сервер

1. **Асиметричний ключ, підпис, сертифікат** —
   `+ref communications/cryptographic-comm/public-key-crypto` ·
   `+ref math/number-theory/hash-and-digital-signature` ·
   `+ref math/number-theory/rsa-cryptosystem`
2. **TLS: рукостискання й ланцюг довіри** — `+ref communications/cryptographic-comm/tls` ·
   `+ref communications/protocols/tls-handshake`
3. **TLS на мікроконтролері** — наявна («TLS на мікроконтролері», курсова) — *переїзд із
   модуля прошивки: тут воно вперше потрібне*
4. **Час, без якого сертифікат не перевірити** — `кандидат` «Синхронізація часу: NTP,
   мітки часу в телеметрії й дрейф годинника» (назвали п'ять джерел) ·
   `+ref communications/protocols/ntp-sync` ·
   `+ref programming/web-backend/monotonic-vs-wall-time` ·
   `+ref communications/synchronization/clock-offset-drift`
5. **HTTP: запит, відповідь, коди, тіло** — `кандидат` · `+ref programming/web-backend/http` ·
   `+ref programming/web-backend/rest-api` · `+ref programming/web-backend/http-caching`
6. **Веб-сервер на МК** — наявна (`programming/networking/web-server-mcu`)
7. **MQTT: брокер, тема, QoS, заповіт** — наявна (`communications/protocols/mqtt`) ·
   `+ref programming/distributed-systems/publish-subscribe`
8. **CoAP: REST для обмежених пристроїв** — `НОВА`
9. **Що всередині повідомлення: JSON, CBOR, бінарний** — наявні («Серіалізація даних» —
   `programming/embedded-systems/data-serialization`, «Пакування бінарного протоколу» —
   `programming/networking/wire-format-packing`) · `+ref programming/representation/json-format` ·
   `НОВА` «Компактні бінарні формати: CBOR і protobuf»
10. **Потік у зворотний бік: WebSocket, SSE, long-poll** —
    `+ref programming/web-backend/streaming-push-transports`
11. **Хто цей пристрій: токен, ключ, клієнтський сертифікат** —
    `+ref programming/web-backend/authentication` · `+ref programming/web-backend/jwt-tokens` ·
    `+ref programming/security/secrets-management`
12. **ВЛАСНА «HTTP, MQTT чи свій: вибір протоколу до сервера»** — трафік, енергія,
    затримка, хто ініціює, що буде за NAT.

*(1–2 у письмі можуть злитися в один крок)*

## Розділ 11. Мережі операторів

1. **ВЛАСНА «Чужа мережа: що ти купуєш і що втрачаєш»** — покриття без щогли, але з
   тарифом, чужими ключами, чужою затримкою й чужим правом вимкнути тебе.
2. **LoRaWAN: приєднання, класи, ADR, шлюз** — `+ref communications/protocols/lorawan`
3. **Стільникова мережа: сота, реєстрація, естафета** — `НОВА`
4. **Покоління: від GSM до 5G і що з них лишилося пристроям** — `НОВА`
5. **LTE-M і NB-IoT** — `НОВА`
6. **SIM, IMSI, APN: як пристрій входить у мережу оператора** — `НОВА`
7. **Модем і AT-команди** — `НОВА`
8. **IP через модем: PPP і вбудований стек** — `НОВА` ·
   `+ref communications/protocols/slip-protocol`
9. **ВЛАСНА «Модем на платі»** — 2 А в імпульсі, антена поруч із власним приймачем,
   AT-сесія як кінцевий автомат, реєстрація, що триває 40 секунд.
10. **Супутниковий канал для пристроїв** — `НОВА` «Супутниковий зв'язок пристроїв:
    короткі повідомлення й NTN»
11. **ВЛАСНА «Вибір каналу під задачу»** — дальність, енергія на байт, ціна, затримка,
    закон; таблиця рішень, яку читач заповнює під свій апарат.

## Розділ 12. Життя з'єднання

1. **Вісім оман про мережу** — `+ref programming/distributed-systems/distributed-fallacies`
2. **Стан з'єднання як автомат** — від «немає живлення» до «передаю», і кожен перехід
   назад · `+ref programming/networking/connection-management` ·
   `+ref programming/embedded-systems/mode-state-machine` `[pending]`
   *(тут була моя ВЛАСНА — адреси вже існують, скасовано)*
3. **Мертвий чи повільний: виявлення обриву** —
   `+ref programming/distributed-systems/failure-detection` ·
   `+ref programming/distributed-systems/health-checks` ·
   `+ref programming/distributed-systems/phi-accrual-failure-detector` ·
   `+ref programming/embedded-systems/health-monitor` `[pending]`
4. **Відступ і тремтіння: як перепідключатися, не вбиваючи мережу** —
   `+ref programming/distributed-systems/retries-backoff` ·
   `+ref programming/distributed-systems/thundering-herd`
5. **Черга офлайну: збережи-й-перешли** — що зберігати, що викидати, у якому порядку
   віддавати після повернення · `+ref programming/networking/store-and-forward` `[pending]` ·
   `+ref programming/client-architecture/offline-first-client` ·
   `+ref programming/distributed-systems/queue-load-leveling` ·
   `+ref programming/distributed-systems/dead-letter-queue`
   *(тут була моя ВЛАСНА — адреса вже існує, скасовано)*
6. **Дублікати після повернення: ідемпотентність** —
   `+ref programming/distributed-systems/idempotency` ·
   `+ref programming/distributed-systems/delivery-guarantees`
7. **Час у журналі, коли годинника немає** — `+ref communications/synchronization/timestamps` ·
   `+ref communications/synchronization/ptp-1588` ·
   `+ref programming/distributed-systems/hybrid-logical-clocks`
8. **Деградація: працювати гірше, але працювати** —
   `+ref programming/embedded-systems/graceful-degradation` ·
   `+ref programming/distributed-systems/graceful-degradation-primary` ·
   `+ref programming/distributed-systems/load-shedding`
9. **ВЛАСНА «Перемикання каналу»** — Wi-Fi → стільниковий → LoRa: правило переходу,
   гістерезис, що з чергою й що з адресою.
10. **Телеметрія як потік: частота, пріоритет, проріджування** — наявні («Телеметрія» —
    `communications/protocols/telemetry-stream`, «Керування й телеметрія» —
    `communications/protocols/control-telemetry`) · `+ref programming/operations/structured-logging`
11. **ВЛАСНА «Як подивитися в канал»** — логічний аналізатор (наявна,
    `electronics/metrology/logic-analyzer`), дамп трафіку, журнал RSSI, водоспад SDR ·
    `НОВА` «Захоплення трафіку: дзеркало порту, фільтр, читання дампу» · `НОВА` «SDR:
    приймач, зроблений програмою» · `НОВА` «Аналізатор спектра»

## Розділ 13. Свій протокол

1. **ВЛАСНА «Набір повідомлень і ролі сторін»** — хто ініціює, що обов'язкове, що
   опційне, скільки станів у кожної сторони ·
   `+ref programming/networking/interface-definition-language` `[pending]`
   *(опис інтерфейсу й генерація коду — коли набір уже усталився)*
2. **Порядок байтів, вирівнювання, пакування** — наявна («Пакування бінарного протоколу») ·
   `+ref programming/representation/zero-copy-serialization` ·
   `+ref programming/representation/twos-complement`
3. **ВЛАСНА «Версія протоколу»** — `кандидат` «Версіювання прошивки й сумісність
   протоколу» · `+ref programming/web-backend/api-versioning` ·
   `+ref programming/distributed-systems/schema-registry` ·
   `+ref programming/representation/self-describing-format`
4. **Виявлення й рукостискання** — `+ref programming/distributed-systems/service-discovery` ·
   наявна («Багатоадресна розсилка й виявлення»)
5. **Виклик проти повідомлення: RPC** — наявна («RPC у вбудованих системах», курсова) ·
   `+ref programming/networking/rpc`
6. **Автентичність свого каналу** — `+ref communications/cryptographic-comm/authenticated-encryption` ·
   `+ref communications/protocols/sequence-numbering` *(лічильник як захист від повтору)*
7. **ВЛАСНА «Специфікація як документ»** — таблиця повідомлень, стан-машина, приклади
   байтів, розділ «що робити при помилці»; те, без чого протокол живе лише в голові автора.
8. **ВЛАСНА «Стенд протоколу»** — запис, повтор, ін'єкція помилок, тест «половина
   пакета» · наявні («Тестування відмовостійкості: fault injection», «HIL-стенд»)

---

# 3. Не лягло нікуди — з адресою

Нічого не викинуто мовчки. Нижче — усе, що стосується зв'язку, але цьому томові не
належить.

| що | куди | чому |
|---|---|---|
| MAVLink: пакет, команди, місії, параметри, підпис, діалекти, FTP, HEARTBEAT, high-latency, події, рельєф, sysid/compid, граблі (`communications/protocols/mavlink-*`, `param-protocol`, `mission-protocol`, `stream-rates`, `motion-control-setpoints`, `gcs-failsafe`, `flight-log-formats`, `cryptographic-comm/mavlink-security`) | **том 11 «Дрони»** (частина — том 13, наземна станція) | це протокол керування апаратом, а не спосіб з'єднати два пристрої; том 5 дає йому кадр, CRC, підпис і канал |
| RC-лінк, RC-сигнал (PWM/PPM/S.BUS), CRSF, режими failsafe RC, ExpressLRS, канал земля-борт, телекерування із затримками | **том 11**, частково **том 12** | керування апаратом у реальному часі — окрема дисципліна з власними вимогами до затримки |
| DroneCAN | **том 11** | профіль CAN для дронової периферії; сама шина CAN — мій розділ 1 |
| Відео: RTP/RTCP, RTSP/SDP, H.264 NAL, MPEG-TS, HLS/DASH, CMAF, WebRTC, SRTP, адаптивний бітрейт, FPV-системи, канали 5,8 ГГц, GStreamer, апаратний кодек | **том 8 «Читання світу»** (камера й кодек), **том 11** (FPV) | відеотракт несе свою теорію з собою — кодек, а не канал |
| GNSS, NMEA 0183, SBAS, RTK, PPS, іоносферна затримка | **том 7 «Положення в просторі»** | приймач сигналу, а не канал обміну |
| Глибоке кодування: турбо, LDPC, полярні, Вітербі, BCH, Рід–Соломон, фонтанні, згорткові, Голея, Ріда–Маллера, циклічні, добуткові, виколоті, LLR, Гілберт–Елліот, конкатеновані, досконалі, SECDED, ECC пам'яті | **лишається в резерві**; стійкість до глушіння — **том 9** | курс бере Геммінга, FEC як поняття, перемежування й пакетну помилку — цього досить, щоб читати даташит LoRa |
| BGP, OSPF, anycast, CDN, балансування L4/L7, зворотний проксі, IPv6-маршрутизація, Happy Eyeballs, SVCB/HTTPS-записи | **том 10 «Архітектура IoT»** (серверний бік) або резерв | це мережа провайдера, а не пристрою |
| Брокери, шини повідомлень, саги, outbox/inbox, кворуми, CAP, консистентність, кеші, плітки — увесь `programming/distributed-systems` понад те, що я взяв | **том 10** | архітектура парку пристроїв, а не один лінк |
| MQTT як архітектура (дизайн тем, тіні пристроїв, парк) | **том 10** | механіку MQTT беру собі, архітектуру віддаю |
| Телефонія: SIP, H.323, ISDN/Q.931, ENUM, E.164, PSTN, модеми серії V, мовні кодеки, ASN.1/PER | **резерв, курс не веде** | немає шляху до цілі курсу |
| Фотоніка: оптоволокно, WDM, EDFA, дисперсія, зрощення | **резерв**; згадка в розділі 11 як варіант між будівлями | вбудованому вузлу волокно потрібне раз на сто проєктів |
| I²C, SPI, USB, 1-Wire, I3C, SD/SDIO, QSPI, тайминги й підтяжки (`communications/buses/*` понад узяте) | **томи 3–4** | шина на платі — периферія МК |
| Синхронне зчитування давачів, джитер вибірки, компенсація затримки давача, час вимірювання | **том 8** | синхронізація вимірювань, а не мережі |
| Веб-автентифікація: OAuth, OIDC, passkeys, MFA, SASL, Kerberos, SCRAM, дайджест, DNSSEC, PKCS#7, DRM | **том 10** (хмара) і **том 15** (продукт) | пристрій обходиться токеном і клієнтським сертифікатом |
| Secure boot, TPM/TrustZone, шифрування Flash, моделювання загроз, межі довіри, поверхня атаки, zero-trust | **том 9** (і том 15) | я даю крипто як інструмент зв'язку; захист пристрою — окремий том |
| Повні EMC-випроби, гіпот-тест, класи ізоляції мережевих пристроїв | **том 14** (плата) і **том 6** (мережеве живлення) | у розділі 6 беру лише сертифікацію радіомодуля як факт, що впливає на вибір |
| PoE як джерело енергії (бюджет, класи, узгодження) | **том 6** | беру PoE як спосіб дотягти живлення дротом; рахунки — там |
| Home Assistant, Matter-інтеграція, вузол розумного дому | **том 10** | сценарій системи, не канал |
| OTA-слоти, серверна частина OTA, заводське провізіонування | **том 3** (механіка), **том 15** (супровід) | том 5 дає під них HTTP, TLS і чергу офлайну |

---

# 4. Діри — з вироком

Спершу — **чого вже НЕ бракує**, попри вирок попереднього проходу. Це не дрібниця: там
шість «зон, яких у корпусі НУЛЬ», і п'ять із них написані.

| «діра» попереднього проходу | насправді |
|---|---|
| «Ethernet — слова немає в корпусі» | 10 написаних статей: `ethernet-frame`, `ethernet-link-phy`, `utp-cable`, `auto-negotiation`, `mdi-mdix`, `csma-cd`, `poe`, `vlan-and-trunking`, `stp-rstp`, `ethernet-on-mcu` |
| «Життя з'єднання — у корпусі НУЛЬ» | `retries-backoff`, `timeouts-deadlines`, `failure-detection`, `health-checks`, `phi-accrual-failure-detector`, `idempotency`, `delivery-guarantees`, `out-of-order-tolerance`, `offline-first-client`, `graceful-degradation`, `load-shedding`, `connection-management`, `distributed-fallacies` |
| «Мережева реальність: NAT, MTU» | `nat`, `nat-traversal`, `middleboxes`, `mtu-and-fragmentation`, `jitter`, `queue-theory-networks` |
| «Бюджет лінка стоїть із невідомим: немає чутливості, SNR, Френеля» | `propagation/link-budget` містить шумовий поріг, коефіцієнт шуму, SNR і запас на завмирання цілим розділом; плюс `free-space-loss`, `friis-transmission`, `fresnel-zones`, `multipath-fading`, `fading-statistics` |
| «BLE понад GATT» | `ble-gap`, `ble-att`, `ble-link-layer`, `ble-security`, `ble-beacon-formats`, `bt-pairing-security`, `bluetooth-classic-stack`, `rfcomm` |
| «Радіомодуль у руках — жодного» | `radio-engineering/rf-module`, `lora`, `time-on-air` + написаний каталог: `connect/radio/nrf24-radio`, `lora-module`, `fpv-telemetry-air`, `fpv-telemetry-ground`, `bluetooth-hc05`, `elrs-air-unit` |
| «ISM і дюті-цикл» | `propagation/ism-bands`, `radio-engineering/time-on-air`, `protocols/regulatory-radio-certification` |

**І окремо — те, що я сам ледь не оголосив дірою, доки не побачив оновленого резерву**
(теми `[pending]`: адреса є, тексту ще немає):

| моя чернеткова діра | справжня адреса |
|---|---|
| `НОВА` «Симетричний шифр і режими» | `algorithms/cryptographic-algorithms/block-cipher`, `stream-cipher` |
| `НОВА` «Обмін ключами DH/ECDH» | `algorithms/cryptographic-algorithms/diffie-hellman` |
| *(додатково знайдено)* | `keyed-hash-mac`, `entropy-source`, `programming/security/key-derivation-function` |
| `НОВА` «Енергозбереження в 802.11: DTIM, TWT» | `programming/embedded-systems/wi-fi-power-modes` |
| `ВЛАСНА` «Стек IP на 300 КБ RAM» | `programming/networking/lwip-internals`, `socket-api` |
| `ВЛАСНА` «Черга офлайну» | `programming/networking/store-and-forward` |
| `ВЛАСНА` «Імпульс передавача» | `programming/embedded-systems/peak-current-budgeting` |
| `ВЛАСНА` «Стан з'єднання як автомат» | `programming/networking/connection-management` + `programming/embedded-systems/mode-state-machine` |
| *(бонус до розділів 4, 8, 13)* | `mdns-dns-sd`, `nagle-and-delayed-ack`, `icmp-errors-in-code`, `ble-gatt-practice`, `interface-definition-language`, `health-monitor` |

**Арифметика тому після звірки.** Зі 143 кроків: **100 спираються на резерв** (`+ref`,
разом із `[pending]`-адресами), **14 — суто наявні теми курсу**, **21 — власна стаття
курсу**, і лише **8 кроків несуть тему, якої в корпусі немає ніде**. Десять кроків
покривають кандидатів із `newtopics-embedded.md`. Тобто діра тому — не «половина
порожнеча», а один розділ (стільниковий зв'язок) плюс п'ять окремих тем.

Тепер — справжні діри: **13 нових тем у книги** (сім із них — стільниковий зв'язок) і
**21 власна стаття курсу**.

## А. Стільниковий зв'язок — у корпусі справді НУЛЬ

Перевірено грепом по всьому резерву: жодної статті про соту, модем, SIM, APN, NB-IoT,
LTE-M чи покоління мереж. Це найбільша діра тому й найдорожча за наслідками: без неї
пристрій живе лише там, де є чужий Wi-Fi, а том 10 будує IoT виключно всередині квартири.

- `НОВА` **«Стільникова мережа: сота, реєстрація, естафета»** → `book/communications/networks`
- `НОВА` **«Покоління стільникового зв'язку: від GSM до 5G»** → `book/communications/networks`
- `НОВА` **«LTE-M і NB-IoT: стільниковий канал для пристроїв»** → `book/communications/networks`
- `НОВА` **«SIM, IMSI і APN»** → `book/communications/networks`
- `НОВА` **«AT-команди: керування модемом»** → `book/communications/interfaces`
  *(поруч із наявним `interfaces/modem-standards-v-series`)*
- `НОВА` **«PPP: IP поверх послідовного каналу»** → `book/communications/protocols`
  *(поруч із наявним `protocols/slip-protocol`)*
- `НОВА` **«Супутниковий зв'язок пристроїв: короткі повідомлення й NTN»** →
  `book/communications/networks`
- `ВЛАСНА` **«Модем на платі»** — 2 А в імпульсі, антена біля власного приймача,
  AT-сесія як автомат: атом цього не дасть, бо це стик модуля, живлення й прошивки.

*Каталог теж порожній:* у `catalog/connect` є nRF24, LoRa, HC-05, ELRS і FPV-телеметрія,
але жодного стільникового модуля. Якщо в автора є SIM7600/A7670 чи подібний — природна
адреса `catalog/connect/cellular`, і тоді розділ 11 отримає ще два-три каталожні `ref`.
Якщо модуля в руках немає — каталожної теми заводити не треба, книжкових вистачить.

## Б. Криптомінімум — атоми всі є, немає зрізу

Тему назвали **п'ять незалежних джерел** — і правильно: WPA2 у розділі 9 і TLS у розділі 10
без неї не читаються, а том 9 іде **після** мого. Але **жодної нової теми заводити не
треба**: написані `cryptographic-hash-functions`, `hash-and-digital-signature`,
`rsa-cryptosystem`, `hmac`, `aead`, `authenticated-encryption`, `public-key-crypto`,
`challenge-response`, `csprng`, `replay-protection`; заведені `[pending]` `block-cipher`,
`stream-cipher`, `diffie-hellman`, `keyed-hash-mac`, `entropy-source`,
`key-derivation-function`. Це повний набір цеглин.

Бракує рівно одного — **зрізу**:

- `ВЛАСНА` **«Криптомінімум пристрою»** — атом цього дати не може, бо атом самодостатній,
  а тут потрібен саме відбір: «стільки, щоб зрозуміти WPA2, TLS і власний тег», з бюджетом
  у байтах і мілісекундах на МК і з чесним «а решта — том 9». Одинадцять атомів читач
  підряд не подужає, і не мусить.

## В. Подивитися в канал — інструмента немає

У корпусі є логічний аналізатор, осцилограф, а в `metrology` заведено `[pending]`
`fft-spectrum` (спектральний аналіз сигналу), `near-field-probing` (зонд ближнього поля)
і `mixed-signal-oscilloscope`. Немає жодної адреси для трьох речей:

- `НОВА` **«Захоплення трафіку: дзеркало порту, фільтр, читання дампу»** →
  `book/communications/networks` — перевірено: ані tcpdump, ані дампу, ані дзеркала порту
  в резерві немає (у `reference/unix-linux` є лише ядрові теми на кшталт XDP і nftables).
- `НОВА` **«SDR: приймач, зроблений програмою»** → `book/communications/radio-engineering`
  *(поруч із `zero-if-receiver`, `iq-representation`, `frequency-synthesizer`)*
- `НОВА` **«Аналізатор спектра як прилад»** → `book/electronics/metrology` — саме прилад,
  а не перетворення: `fft-spectrum` поруч і про інше. Якщо автор вважає їх однією темою —
  об'єднати, і тоді це `+ref`, а не `НОВА`.
- `ВЛАСНА` **«Як подивитися в канал»** — зшиває чотири інструменти під одне питання
  «чому не працює» і вчить обирати між ними за симптомом.

## Г. Wi-Fi понад базовою статтею

Стаття `networks/wifi` дає скан, приєднання, STA/AP і DHCP; `wpa-security` дає WPA2/WPA3
повністю; енергоощадність має адресу `embedded-systems/wi-fi-power-modes` `[pending]`.
Лишається одне:

- `НОВА` **«Роумінг у 802.11: 802.11k, 802.11v, 802.11r»** → `book/communications/networks` —
  для всього, що рухається складом, цехом чи полем між двома точками. Курсова «Швидке
  підключення Wi-Fi» дає кеш PMK, але не перехід між точками під час руху.

## Ґ. Прикладний рівень

- `НОВА` **«CoAP: REST для обмежених пристроїв»** → `book/communications/protocols` —
  у корпусі є HTTP, MQTT, WebSocket, але не CoAP, а це стандартний вибір для NB-IoT.
- `НОВА` **«Компактні бінарні формати: CBOR і protobuf»** → `book/programming/representation` —
  є JSON, XML, самоописові формати й формати без копіювання; компактних бінарних немає.

## Д. Те, що може дати лише курс — 21 власна стаття

Атом самодостатній; ці статті — навпаки, зшивають пройдене або доводять до працюючого
результату, і тому належать курсові. Чотири чернеткові власні статті звідси **знято**,
бо резерв має на них адреси (див. таблицю вище).

| № | стаття | чому не атом |
|---|---|---|
| 1.11 | Лінія на сто метрів: збираємо RS-485 і ламаємо її | практичний доказ чотирьох попередніх кроків одразу |
| 2.12 | Свій кадр між двома платами | зшиває кадрування, CRC, ACK, повтор і аналізатор |
| 5.12 | Дальність у полі | методика заміру, а не явище |
| 6.11 | Співіснування 2,4 ГГц і власна самоперешкода | перетин ефіру, живлення й розводки |
| 7.7 | Перший радіоканал на двох платах | переносить кадр із розділу 2 в ефір — сенс усього тому |
| 7.10 | Криптомінімум пристрою | зріз одинадцяти атомів під одну потребу |
| 7.11 | Захист власного радіоканалу | застосування крипти до **свого** кадру |
| 8.7 | Інтервал з'єднання проти батареї | три параметри BLE проти енергобюджету; атоми дають механіку, не компроміс |
| 8.8 | Телефон як другий кінець | інша платформа, а не інша тема |
| 9.7 | Captive portal і своя сторінка налаштувань | зшиває SoftAP, HTTP і NVS |
| 9.11 | Wi-Fi у полі | практика вибору каналу й вимірювання |
| 10.12 | HTTP, MQTT чи свій | рішення на перетині чотирьох протоколів |
| 11.1 | Чужа мережа: що ти купуєш і що втрачаєш | рамка для LoRaWAN, стільникового й супутника |
| 11.9 | Модем на платі | стик модуля, живлення й прошивки |
| 11.11 | Вибір каналу під задачу | капстоун-рішення по всьому тому |
| 12.9 | Перемикання каналу | правило переходу між трьома каналами — тільки курс має всі три |
| 12.11 | Як подивитися в канал | зшиває чотири інструменти під один симптом |
| 13.1 | Набір повідомлень і ролі сторін | метод проєктування, не поняття |
| 13.3 | Версія протоколу | те саме, і на пристрої це не те саме, що версіювання веб-API |
| 13.7 | Специфікація як документ | те саме |
| 13.8 | Стенд протоколу | доведення до працюючого результату |

---

# 5. Криптомінімум: рішення й що дістається тому 9

**Рішення: криптомінімум лишається в томі 5, у розділі 7.** Не тому, що так зручно, а
тому, що інакше том ламає залізне правило курсу.

- Том 9 «Безпека і перешкоди» іде **після** мого. Якщо ключ, геш і код автентичності
  лежать там, то мої кроки WPA2 (9.3), TLS (10.2) і захист власного каналу (7.11)
  вимагають небаченого. Це не питання смаку, а питання порядку.
- Місце вибрано за болем, а не за програмою: **не** окремим розділом «математичні основи»
  на початку тому (розділ несе свою теорію з собою), а рівно там, де читач щойно зробив
  власний радіоканал і побачив, що його повторить будь-хто з таким самим модулем за 4 долари.

**Що том 5 віддає томові 9 готовим** (перевчати не треба, треба спиратися):
геш і код автентичності · симетричний шифр і режим · одноразове число й лічильник проти
повтору · джерело випадковості на МК · обмін ключами (DH/ECDH) · відкритий ключ, підпис,
ланцюг сертифікатів · рукостискання TLS і його ціна в RAM · чотириетапне рукостискання
WPA2 і що таке PSK · ключі LoRaWAN при приєднанні · автентифікований кадр власного протоколу.

**Що том 5 навмисно НЕ бере і лишає томові 9:**
модель загроз і межі довіри · атаки (deauth, evil twin, KRACK, MITM, підміна команд,
глушіння, РЕБ, спуфінг GNSS) · зберігання ключа в залізі (fuse, secure element,
TrustZone) · secure boot і шифрування Flash · ротація й відкликання ключів у парку ·
бічні канали · стійкість лінка до навмисної завади понад те, що дає бюджет.

**Що том 5 лишає томові 15 «Продукт»:** заводське провізіонування ключів, ліцензування,
підпис прошивок, супровід сертифікатів після продажу.

---

# 6. Заперечення й спірні межі

## 6.1 Проти начерку автора

**«Комунікація — тут більше про радіо, вайфай, інтернет, локальні мережі».** По суті так,
але порядок у цьому переліку — пастка. Якщо почати з радіо, читач учить дві складні речі
одночасно: середовище, яке губить, і протокол, який це компенсує. Половина тому до радіо
взагалі стосунку не має. Тому розділи 1–4 стоять перед ефіром — і це не лише кадр
(як у попередньому проході), а й уся IP-мережа. **Це моє головне відхилення від начерку.**

**У начерку немає стільникового зв'язку.** Ані модема, ані SIM, ані NB-IoT. Це різниця між
«пристрій у квартирі» й «пристрій у полі», тобто між половиною курсу й цілим курсом.
Додаю розділ 11 і сім нових тем у корпус.

**У начерку немає буднів з'єднання.** Автор поклав «втрату зв'язку» в том 9 — і там їй
справді місце, коли причина **ворожа**. Але дев'ять обривів із десяти — не атака: роутер
перезавантажили, пристрій виїхав за край покриття, оператор скинув сесію. Це щоденна
робота лінка. Додаю розділ 12.

**«Локальні мережі» я читаю як Ethernet і IP**, а не як «мережа розумного дому». Друге —
том 10.

**Спіраль ужита свідомо тричі** (і лише там, де без раннього дотику далі не читається):
LoRa як модуляція в розділі 7 → LoRaWAN як чужа мережа в розділі 11 · симетрична крипта
в розділі 7 → асиметрична й PKI в розділі 10 → атаки в томі 9 · власний кадр у розділі 2
→ проєктування протоколу в розділі 13.

## 6.2 Спірні теми — з суперником і аргументом

**СПІРНА: Ethernet і IP до радіо. Суперник — попередній прохід і буква начерку.**
За суперника: читач із ESP32 хоче Wi-Fi, а не виту пару; Ethernet на МК трапляється рідше.
За мене: (1) сокет, DNS, MTU й NAT однакові над обома середовищами, і вчити їх дешевше
там, де невдача має одне пояснення; (2) інакше Wi-Fi у розділі 8 дає «приєднаний, але
німий» стан на два розділи; (3) PoE-датчик, панель і промисловий вузол сидять на дроті.
Ціна мого рішення чесна: ~21 крок дроту до першої хвилі.

**СПІРНА: криптомінімум. Суперник — том 9.** Розібрано в §5. Вирішено на мою користь
через порядок томів, а не через важливість.

**СПІРНА: RS-485, CAN, диференційна пара. Суперник — том 4 «Периферія МК».**
За суперника: це шини, а шини — том 4. За мене: том 4 — про те, що чіпляється **до МК**
на платі; RS-485 і CAN — зв'язок між **окремими пристроями** через десятки метрів, зі
своєю фізикою (синфазна завада, термінація, розв'язка, арбітраж). Це те саме, що радіо,
тільки середовище дротове, і саме тут найдешевший майданчик для протоколу. Якщо том 4
їх забирає, мій розділ 1 треба перебудувати навколо Ethernet-фізики, і том утратить
найкращий вступ. `DroneCAN` віддаю тому 11 без спору.

**СПІРНА: MQTT. Суперник — том 10 «Архітектура IoT».**
Ділю: механіка (брокер, тема, QoS, retained, заповіт, keepalive) — мені, бо без неї
«інтернет» у томі 5 порожній; дизайн тем, тіні пристроїв, парк на тисячу вузлів,
мостування — тому 10. Том 10 має знати, що отримує готовим: сокет, TLS, HTTP, MQTT-клієнт,
NAT, DNS/mDNS, час, стан з'єднання, відступ і чергу офлайну.

**СПІРНА: «Життя з'єднання» як окремий розділ. Суперники — том 9 і том 10.**
Том 9 забирає ворожу причину обриву, том 10 — стійкість системи з багатьох вузлів. Лишаю
собі поведінку **одного лінка одного пристрою**: автомат стану, відступ, черга, дублікати,
деградація. Якщо цей розділ віддати, обидва сусіди отримають його як передумову, якої
ніхто не давав.

**СПІРНА: «Свій протокол» як розділ. Суперник — том 10 (контракти, схеми, версіювання).**
За суперника: версіювання й еволюція схем — архітектурна тема. За мене: у томі 10 це буде
про сервіси, а тут — про два мікроконтролери й 200 байтів. Це найлегший розділ для різу,
якщо том треба полегшити: 8 кроків, і всі вони мають дім у томі 10.

**СПІРНА: ISM, дюті-цикл, сертифікація, самоперешкода. Суперники — том 9 і том 14.**
Беру: без законної межі потужності бюджет лінка дає відповідь, яку не можна застосувати,
а вибір діапазону робиться саме тут. Віддаю: EMC-випроби й повний протокол сертифікації —
том 14; навмисна завада й РЕБ — том 9.

**СПІРНА: енергія радіо (DTIM, імпульс TX, PoE). Суперник — том 6 «Керування живленням».**
Називаю біль там, де він кусає: радіо перезавантажує МК просадкою, а Wi-Fi з'їдає
батарею за добу. Рахунки, банк конденсаторів, енергобюджет і вибір хімії — том 6.

**СПІРНА: провізіонування. Суперник — том 15 (і частково том 14).**
Беру перше приєднання: пристрій без клавіатури мусить якось дізнатися пароль. Заводське
й масове провізіонування, ключі на конвеєрі — том 15.

**СПІРНА: NFC/RFID. Суперник — том 4 (периферія) і том 8 (читання світу).**
Претензія слабка з обох боків. Лишаю в розділі 8, бо зчитування мітки — це обмін
з чужим пристроєм, а не читання регістра. Якщо том 4 забере — заперечувати не буду.

**СПІРНА: телеметрійні радіо (ELRS, SiK, канал земля-борт). Суперник — том 11.**
Беру один крок «що купують для апарата» з каталожними refʼами; архітектуру ELRS, CRSF
і failsafe RC віддаю тому 11 повністю.

**СПІРНА: антена на власній платі (keep-out, стек, КСХ-замір). Суперник — том 14.**
Лишаю тут: читач саме зараз обирає модуль і має знати, що keep-out під антеною — не
примха. Повна RF-розводка, контрольований імпеданс і виробництво — том 14.

## 6.3 Дві правки до наявного матеріалу курсу

1. **Курсова «Бюджет лінії» дублює написаний атом `propagation/link-budget`,** причому атом
   глибший: у ньому шумовий поріг, коефіцієнт шуму, SNR і запас на завмирання — рівно те,
   чого попередній прохід шукав як «діру». Те саме з парами «Методи множинного доступу» ↔
   `csma-ca`/`cdma`/`ofdma`, «Стратегії ARQ» ↔ `reliability/arq`/`sliding-window-arq`,
   «Режими поширення радіохвиль» ↔ `frequency-bands`/`atmospheric-absorption`.
   Обидві версії написані, тож пропоную не різати, а зробити з пари **явну спіраль**:
   курсова стаття — крок, атом — наступний крок «глибше», з чесною позначкою.
2. **«Спільна земля», «Земляні петлі», «Екранування» і «TLS на мікроконтролері» зараз
   лежать в інших модулях** (плати та прошивка). Перші три потрібні в розділі 1, четверта —
   в розділі 10. Це переїзд, а не дублювання.

## 6.4 Чого том вимагає від попередніх — інакше він не читається

- **Том 2:** спектр і смуга сигналу, децибели (якщо їх не дасть том 2, мій розділ 5 бере
  «Потужність і децибели» на себе — так і закладено), лінія передачі на PCB, наводки.
- **Том 3:** задачі й черги RTOS (для стека й черги офлайну), NVS (для пароля й ключа),
  watchdog, кільцевий буфер.
- **Том 4:** UART/SPI, переривання й DMA, перетворювач рівнів, логічний аналізатор,
  уміння читати чужий даташит — без нього розділ 7 неможливий.

---

# 7. Що том гарантує сусідам

- **Тому 6 (живлення):** профіль струму радіо й модема, дюті-цикл як параметр енергії,
  PoE як спосіб живити вузол дротом.
- **Тому 7 (положення):** канал для передавання поправок і телеметрії, час і мітки.
- **Тому 8 (читання світу):** транспорт для потоку давача, бюджет смуги, чому відео не
  влізе в LoRa.
- **Тому 9 (безпека і перешкоди):** шумовий поріг, SNR, запас у децибелах, розширений
  спектр і стрибки, криптомінімум, автентифікований кадр, поведінка лінка при обриві —
  усе, без чого «лінк під глушінням» і підміна команди не читаються.
- **Тому 10 (IoT):** сокет, HTTP, MQTT, TLS, NAT, DNS/mDNS, CoAP, час, стан з'єднання,
  відступ, черга офлайну, метрики каналу і стільниковий канал для вузла поза домом.
- **Тому 11 (дрони):** бюджет лінка з чутливістю, дуплекс і затримка, FHSS, кадр із CRC
  і підписом як основа MAVLink, поведінка при втраті лінка.
- **Тому 12 (автоматизація):** транспорт для віддаленого керування, бюджет затримки й
  джитера, ідемпотентність команди, перемикання каналів.
- **Тому 14 (власні плати):** вимоги до RF-розводки, keep-out, роз'єми й екран кабелю,
  сертифікаційні обмеження, які треба закласти до розводки.
