/* guide/embedded-ultra/manifest.js — КУРС «Ембеддед ультракоротко» (тип "guide").
   Стислий зріз ембеддеда: 21 модуль, 96 кроків, УСІ — ref на готові book-атоми.
   Модулі 1–13 — база (2 дні читання); модулі 14–21 — прикладний трек «наземна станція ↔ борт»:
   мережа TCP/UDP, бінарні протоколи, MAVLink/телеметрія, радіоканал, навігація, політ, борт, відео.
   Власних статей курс не має й не потребує: це доріжка-компіляція поверх написаного.
   Довгий шлях із тими самими темами вглиб — guide/embedded (643 кроки).
   Схема v6 (AUTHORING §2): modules[] → chapters[] → steps[]; нумерація Модуль·Розділ·Крок — з порядку масивів. */
(window.__GUIDES__ = window.__GUIDES__ || []).push({
  type: "guide", slug: "embedded-ultra", title: "Ембеддед ультракоротко",
  modules: [
    { n: 1, slug: "elektryka", title: "Електрика: чим міряють і що тече", scope: "", chapters: [
      { title: "Величини", steps: [
        { ref: "physics/electromagnetism/voltage", title: "Напруга" },
        { ref: "physics/electromagnetism/electric-current", title: "Струм" },
        { ref: "electronics/analog/ohms-law", title: "Закон Ома" },
        { ref: "physics/electromagnetism/electric-power", title: "Потужність" },
      ] },
      { title: "Найкорисніше коло", steps: [
        { ref: "electronics/analog/voltage-divider", title: "Дільник напруги" },
      ] },
    ] },
    { n: 2, slug: "syhnal", title: "Сигнал у часі", scope: "", chapters: [
      { title: "Конденсатор і час", steps: [
        { ref: "electronics/components/capacitor", title: "Конденсатор" },
        { ref: "electronics/analog/rc-time-constant", title: "Стала RC" },
        { ref: "electronics/analog/rc-low-pass", title: "RC-ФНЧ" },
      ] },
      { title: "Побачити сигнал", steps: [
        { ref: "electronics/metrology/oscilloscope", title: "Осцилограф" },
      ] },
    ] },
    { n: 3, slug: "napivprovidnyky", title: "Напівпровідники", scope: "", chapters: [
      { title: "Діод і транзистор", steps: [
        { ref: "electronics/components/diode-iv-curve", title: "ВАХ діода" },
        { ref: "electronics/analog/transistor-idea", title: "Транзистор" },
        { ref: "electronics/analog/mosfet-switch", title: "MOSFET як ключ" },
      ] },
      { title: "Аналогова цеглина", steps: [
        { ref: "electronics/analog/opamp", title: "Оппідсилювач" },
      ] },
    ] },
    { n: 4, slug: "zhyvlennia", title: "Живлення", scope: "", chapters: [
      { title: "Перетворювачі", steps: [
        { ref: "electronics/power-electronics/ldo", title: "LDO" },
        { ref: "electronics/power-electronics/buck", title: "Buck-перетворювач" },
      ] },
      { title: "Чиста шина й батарея", steps: [
        { ref: "electronics/components/decoupling", title: "Decoupling-конденсатор" },
        { ref: "electronics/power-electronics/li-ion-charger", title: "Зарядка Li-ion" },
      ] },
    ] },
    { n: 5, slug: "cyfra", title: "Цифра", scope: "", chapters: [
      { title: "Рівні й вентилі", steps: [
        { ref: "electronics/digital/why-digital", title: "Навіщо цифра" },
        { ref: "electronics/digital/logic-levels-as-ranges", title: "Рівні «0» і «1»" },
        { ref: "electronics/digital/basic-gates", title: "Базові вентилі" },
      ] },
      { title: "Такт", steps: [
        { ref: "electronics/digital/clock-signal", title: "Тактовий сигнал" },
      ] },
    ] },
    { n: 6, slug: "kod", title: "Числа й код", scope: "", chapters: [
      { title: "Як залізо бачить числа", steps: [
        { ref: "programming/computer-architecture/bits-bytes-endianness", title: "Біти й порядок байтів" },
        { ref: "programming/computer-architecture/integer-types-c", title: "Цілі типи в C/C++" },
        { ref: "programming/computer-architecture/overflow-wraparound", title: "Переповнення" },
      ] },
      { title: "Від тексту до прошивки", steps: [
        { ref: "programming/languages/compilation", title: "Компіляція" },
      ] },
    ] },
    { n: 7, slug: "pamyat", title: "Пам'ять", scope: "", chapters: [
      { title: "Адреси й карта", steps: [
        { ref: "programming/systems/addresses-pointers", title: "Адреси й покажчики" },
        { ref: "programming/systems/memory-map", title: "Карта пам'яті" },
        { ref: "programming/systems/flash-vs-ram", title: "Flash і RAM" },
      ] },
      { title: "Класична аварія", steps: [
        { ref: "programming/systems/stack-overflow", title: "Переповнення стека" },
      ] },
    ] },
    { n: 8, slug: "mk", title: "Мікроконтролер", scope: "", chapters: [
      { title: "Що це", steps: [
        { ref: "programming/embedded-systems/microcontroller", title: "Мікроконтролер" },
        { ref: "programming/computer-architecture/mcu-blocks", title: "Складові МК" },
      ] },
      { title: "Як ним керують", steps: [
        { ref: "programming/embedded-systems/memory-mapped-io", title: "Memory-mapped IO" },
        { ref: "programming/embedded-systems/gpio-registers", title: "GPIO-регістри" },
        { ref: "electronics/digital/floating-pullups", title: "Підтяжки" },
      ] },
      { title: "Залити код", steps: [
        { ref: "programming/embedded-systems/flashing", title: "Прошивка у Flash" },
      ] },
    ] },
    { n: 9, slug: "peryferiia", title: "Периферія", scope: "", chapters: [
      { title: "Час і події", steps: [
        { ref: "programming/embedded-systems/interrupts", title: "Переривання" },
        { ref: "programming/embedded-systems/timer-counter", title: "Таймер-лічильник" },
        { ref: "programming/embedded-systems/pwm", title: "ШІМ" },
      ] },
      { title: "Аналог і потік", steps: [
        { ref: "electronics/digital/adc", title: "АЦП" },
        { ref: "programming/computer-architecture/dma-controller", title: "DMA-контролер" },
      ] },
    ] },
    { n: 10, slug: "shyny", title: "Шини", scope: "", chapters: [
      { title: "Три шини", steps: [
        { ref: "communications/buses/uart-frame", title: "Кадр UART" },
        { ref: "communications/buses/i2c-bus", title: "Шина I2C" },
        { ref: "communications/buses/spi-bus", title: "Шина SPI" },
      ] },
      { title: "Як говорять із чипом", steps: [
        { ref: "communications/buses/register-map", title: "Регістрова карта" },
      ] },
    ] },
    { n: 11, slug: "systema", title: "Системний шар", scope: "", chapters: [
      { title: "Задачі й дані", steps: [
        { ref: "programming/embedded-systems/freertos", title: "FreeRTOS" },
        { ref: "programming/systems/task-ipc", title: "Черги й семафори" },
        { ref: "programming/embedded-systems/nvs", title: "NVS" },
      ] },
      { title: "Оновлення й сон", steps: [
        { ref: "programming/embedded-systems/ota-update", title: "OTA-оновлення" },
        { ref: "programming/embedded-systems/sleep-modes", title: "Режими сну" },
      ] },
    ] },
    { n: 12, slug: "nadiynist", title: "Щоб не падало", scope: "", chapters: [
      { title: "Правильний цикл", steps: [
        { ref: "programming/embedded-systems/nonblocking-time", title: "Неблокуючий час" },
        { ref: "programming/systems/atomicity-races", title: "Атомарність і гонки" },
        { ref: "programming/languages/std-atomic", title: "std::atomic і порядок пам'яті" },
      ] },
      { title: "Коли падає", steps: [
        { ref: "programming/embedded-systems/watchdog", title: "Watchdog" },
        { ref: "programming/embedded-systems/hardfault", title: "Розбір HardFault" },
      ] },
    ] },
    { n: 13, slug: "svit", title: "Світ навколо МК", scope: "", chapters: [
      { title: "Давачі", steps: [
        { ref: "electronics/sensors/what-is-a-sensor", title: "Що таке давач" },
        { ref: "electronics/sensors/imu", title: "IMU-давач" },
      ] },
      { title: "Привід", steps: [
        { ref: "electronics/power-electronics/dc-motor-driver", title: "Драйвер DC-моторів" },
      ] },
      { title: "Бездротовий зв'язок", steps: [
        { ref: "communications/networks/wifi", title: "Wi-Fi" },
        { ref: "communications/protocols/ble-gatt", title: "BLE GATT" },
      ] },
    ] },
    { n: 14, slug: "merezha", title: "Мережа: TCP і UDP", scope: "", chapters: [
      { title: "Два транспорти", steps: [
        { ref: "communications/protocols/tcp-vs-udp", title: "TCP проти UDP" },
        { ref: "programming/networking/sockets-tcp-udp", title: "Сокети TCP/UDP" },
      ] },
      { title: "Що під ними", steps: [
        { ref: "communications/networks/mac-ip-arp", title: "MAC, IP і ARP" },
        { ref: "communications/networks/ip-routing", title: "Маршрутизація" },
        { ref: "communications/coding-theory/internet-checksum", title: "Інтернет-контрольна сума" },
      ] },
    ] },
    { n: 15, slug: "protokol", title: "Бінарний протокол", scope: "", chapters: [
      { title: "Байти на дроті", steps: [
        { ref: "programming/embedded-systems/data-serialization", title: "Серіалізація даних" },
        { ref: "communications/protocols/packet-design", title: "Проєктування пакета" },
      ] },
      { title: "Цілісність", steps: [
        { ref: "communications/coding-theory/checksums", title: "Контрольні суми" },
        { ref: "communications/coding-theory/crc", title: "CRC" },
      ] },
    ] },
    { n: 16, slug: "mavlink", title: "Телеметрія і MAVLink", scope: "", chapters: [
      { title: "Земля-борт", steps: [
        { ref: "communications/protocols/control-telemetry", title: "Керування й телеметрія" },
        { ref: "communications/protocols/telemetry-stream", title: "Телеметрія" },
      ] },
      { title: "MAVLink", steps: [
        { ref: "communications/protocols/mavlink-packet", title: "Пакет MAVLink" },
        { ref: "communications/protocols/mavlink-commands", title: "Команди MAVLink" },
      ] },
      { title: "Бортова шина", steps: [
        { ref: "communications/buses/dronecan", title: "DroneCAN" },
      ] },
    ] },
    { n: 17, slug: "radiokanal", title: "Радіоканал", scope: "", chapters: [
      { title: "Хвиля несе дані", steps: [
        { ref: "communications/modulation/why-modulation", title: "Навіщо модуляція" },
        { ref: "communications/modulation/spread-spectrum", title: "Розширений спектр" },
      ] },
      { title: "Антена", steps: [
        { ref: "communications/antennas/antenna", title: "Антена" },
        { ref: "communications/antennas/antenna-gain", title: "Підсилення антени" },
      ] },
      { title: "Лінк до борта", steps: [
        { ref: "communications/radio-engineering/telemetry-link", title: "Канал земля-борт" },
      ] },
    ] },
    { n: 18, slug: "navihatsiia", title: "Навігація", scope: "", chapters: [
      { title: "Де я", steps: [
        { ref: "communications/synchronization/gnss", title: "GNSS" },
      ] },
      { title: "Злиття давачів", steps: [
        { ref: "algorithms/signal-robotics/sensor-fusion", title: "Поєднання давачів" },
        { ref: "algorithms/signal-robotics/complementary-filter", title: "Комплементарний фільтр" },
      ] },
      { title: "Фільтр Калмана", steps: [
        { ref: "algorithms/signal-robotics/predict-vs-measure", title: "Передбачення vs вимір" },
        { ref: "algorithms/signal-robotics/kalman-filter", title: "Фільтр Калмана" },
        { ref: "algorithms/signal-robotics/kalman-ekf", title: "Розширений Калман (EKF)" },
      ] },
    ] },
    { n: 19, slug: "polit", title: "Політ і керування", scope: "", chapters: [
      { title: "Чому літає", steps: [
        { ref: "physics/mechanics/propeller-geometry", title: "Гвинт" },
        { ref: "physics/mechanics/fixed-wing-lift", title: "Літак" },
      ] },
      { title: "Утримати курс", steps: [
        { ref: "algorithms/signal-robotics/discrete-pid", title: "Дискретний ПІД" },
        { ref: "algorithms/signal-robotics/quaternion-attitude-control", title: "Кватерніонне керування орієнтацією" },
      ] },
    ] },
    { n: 20, slug: "bort", title: "Борт: мотор і батарея", scope: "", chapters: [
      { title: "Тяга", steps: [
        { ref: "electronics/electromechanics/bldc-motor", title: "BLDC-мотор" },
        { ref: "electronics/power-electronics/esc", title: "ESC-регулятор" },
      ] },
      { title: "Батарея під навантаженням", steps: [
        { ref: "electronics/power-electronics/battery-sag", title: "Просадка під навантаженням" },
        { ref: "electronics/power-electronics/bms", title: "Захист і BMS" },
      ] },
    ] },
    { n: 21, slug: "video", title: "Відео з борту", scope: "", chapters: [
      { title: "Стиснути", steps: [
        { ref: "algorithms/data-compression/jpeg-intra", title: "JPEG" },
        { ref: "algorithms/data-compression/inter-frame", title: "Міжкадрове стиснення" },
      ] },
      { title: "Донести і встигнути", steps: [
        { ref: "communications/networks/video-transmission", title: "Передача відео" },
        { ref: "programming/embedded-systems/video-latency", title: "Затримка відео" },
      ] },
    ] },
  ]
});
