/* book/communications/manifest.js — книга-предмет «Зв'язок» (тип "book").
   Галузі → теми (плейсхолдери: status:"empty", origin = старе розташування для кроку 5).
   Схема: { type, slug, title, sections:[ {slug,title,scope, topics:[ {slug,title,status,origin} ]} ] } */
(window.__BOOKS__ = window.__BOOKS__ || []).push({
  type: "book",
  slug: "communications",
  title: "Зв'язок",
  sections: [
    { slug: "information-theory", title: "Теорія інформації", scope: "Математична межа стиснення й передачі: ентропія, пропускна здатність каналу, теореми Шеннона.",
      topics: [
      { slug: "bandwidth-capacity", title: "Смуга і межа Шеннона", status: "empty", origin: "embedded/block-6-comms-radio/modulation-link-budget#6.7.4" }
      ] },
    { slug: "coding-theory", title: "Кодування", scope: "Захист повідомлення від помилок і його компактне подання кодами джерела й каналу.",
      topics: [
      { slug: "parity-bit", title: "Біт парності", status: "empty", origin: "embedded/block-3-digital-processor/error-correction#3.9.2" },
      { slug: "checksums", title: "Контрольні суми", status: "empty", origin: "embedded/block-3-digital-processor/error-correction#3.9.3" },
      { slug: "crc", title: "CRC", status: "empty", origin: "embedded/block-3-digital-processor/error-correction#3.9.4" },
      { slug: "hamming-distance", title: "Відстань Геммінга", status: "empty", origin: "embedded/block-3-digital-processor/error-correction#3.9.5" },
      { slug: "hamming-code", title: "Код Геммінга", status: "empty", origin: "embedded/block-3-digital-processor/error-correction#3.9.6" },
      { slug: "ecc-ram-flash", title: "ECC у пам'яті", status: "empty", origin: "embedded/block-3-digital-processor/error-correction#3.9.7" },
      { slug: "reed-solomon", title: "Рід–Соломон", status: "empty", origin: "embedded/block-3-digital-processor/error-correction#3.9.8" },
      { slug: "data-reliability", title: "Надійність даних", status: "empty", origin: "embedded/block-3-digital-processor/error-correction#3.9.9" }
      ] },
    { slug: "modulation", title: "Модуляція", scope: "Накладання інформації на несучу: амплітудні, частотні, фазові та квадратурні схеми.",
      topics: [
      { slug: "why-modulation", title: "Навіщо модуляція", status: "empty", origin: "embedded/block-6-comms-radio/modulation-link-budget#6.7.1" },
      { slug: "am-fm", title: "AM і FM", status: "empty", origin: "embedded/block-6-comms-radio/modulation-link-budget#6.7.2" },
      { slug: "fsk-psk", title: "FSK і PSK", status: "empty", origin: "embedded/block-6-comms-radio/modulation-link-budget#6.7.3" },
      { slug: "spread-spectrum", title: "Розширений спектр", status: "empty", origin: "embedded/block-6-comms-radio/modulation-link-budget#6.7.5" },
      { slug: "lora", title: "LoRa", status: "empty", origin: "embedded/block-6-comms-radio/modulation-link-budget#6.7.8" },
      { slug: "jamming-fhss", title: "Лінк під глушінням", status: "empty", origin: "embedded/block-6-comms-radio/telemetry-mavlink#6.9.9" },
      { slug: "analog-video", title: "Аналогове відео", status: "empty", origin: "embedded/block-7-systems/video-signals-1#7.7.6" }
      ] },
    { slug: "signal-processing", title: "Обробка сигналів", scope: "Перетворення, фільтрація та виявлення сигналів у цифровій і аналоговій формі.",
      topics: [
      { slug: "nyquist-aliasing", title: "Найквіст і аліасинг", status: "empty", origin: "embedded/block-4-mcu-esp32/adc#4.8.5" },
      { slug: "signal-acquisition", title: "Зчитування сигналу", status: "empty", origin: "embedded/block-4-mcu-esp32/adc#4.8.7" },
      { slug: "resolution-framerate", title: "Роздільність і кадри", status: "empty", origin: "embedded/block-7-systems/video-signals-1#7.7.5" }
      ] },
    { slug: "propagation", title: "Поширення хвиль", scope: "Поведінка електромагнітних хвиль у середовищі: загасання, відбиття, завмирання, дальність.",
      topics: [
      { slug: "propagation-polarization", title: "Поширення й поляризація", status: "empty", origin: "embedded/block-6-comms-radio/radio-em-waves#6.6.3" },
      { slug: "frequency-bands", title: "Діапазони частот", status: "empty", origin: "embedded/block-6-comms-radio/radio-em-waves#6.6.4" },
      { slug: "power-decibels", title: "Потужність і децибели", status: "empty", origin: "embedded/block-6-comms-radio/radio-em-waves#6.6.5" },
      { slug: "free-space-loss", title: "Загасання у просторі", status: "empty", origin: "embedded/block-6-comms-radio/radio-em-waves#6.6.6" },
      { slug: "link-budget", title: "Бюджет лінії", status: "empty", origin: "embedded/block-6-comms-radio/modulation-link-budget#6.7.6" },
      { slug: "multipath-fading", title: "Багатопроменевість", status: "empty", origin: "embedded/block-6-comms-radio/modulation-link-budget#6.7.7" },
      { slug: "ism-bands", title: "ISM-діапазони", status: "empty", origin: "embedded/block-6-comms-radio/antennas#6.8.8" },
      { slug: "gnss", title: "GNSS", status: "empty", origin: "embedded/block-7-systems/flight-components#7.3.3" }
      ] },
    { slug: "antennas", title: "Антени", scope: "Випромінювання й приймання хвиль: діаграми спрямованості, підсилення, апертури, решітки.",
      topics: [
      { slug: "esp32-antenna", title: "Антена ESP32", status: "empty", origin: "components/comms/esp32-antenna/" },
      { slug: "antenna", title: "Антена", status: "empty", origin: "embedded/block-6-comms-radio/antennas#6.8.1" },
      { slug: "resonance-dipole", title: "Резонанс і диполь", status: "empty", origin: "embedded/block-6-comms-radio/antennas#6.8.2" },
      { slug: "antenna-gain", title: "Підсилення антени", status: "empty", origin: "embedded/block-6-comms-radio/antennas#6.8.3" },
      { slug: "antenna-polarization", title: "Поляризація антени", status: "empty", origin: "embedded/block-6-comms-radio/antennas#6.8.4" }
      ] },
    { slug: "radio-engineering", title: "Радіотехніка", scope: "Схемотехніка приймачів і передавачів: підсилювачі, змішувачі, гетеродини, синтезатори.",
      topics: [
      { slug: "rf-module", title: "Радіомодуль", status: "empty", origin: "components/comms/undefined" },
      { slug: "lora", title: "LoRa-модуль", status: "empty", origin: "components/comms/undefined" },
      { slug: "nfc-rfid", title: "NFC/RFID", status: "empty", origin: "components/comms/nfc-rfid/" },
      { slug: "esp32-module", title: "ESP32-модуль", status: "empty", origin: "components/comms/wroom-module/" },
      { slug: "superheterodyne", title: "Супергетеродин", status: "empty", origin: "embedded/block-6-comms-radio/modulation-link-budget#6.7.9" },
      { slug: "transmission-lines", title: "Лінії передачі", status: "empty", origin: "embedded/block-6-comms-radio/antennas#6.8.5" },
      { slug: "vswr", title: "Відбиття і КСХ", status: "empty", origin: "embedded/block-6-comms-radio/antennas#6.8.6" },
      { slug: "telemetry-link", title: "Канал земля-борт", status: "empty", origin: "embedded/undefined#7.13.2" }
      ] },
    { slug: "photonics", title: "Фотоніка", scope: "Передача світлом по волокну й у вільному просторі: лазери, детектори, дисперсія, підсилювачі.",
      topics: [
      { slug: "optical-fiber", title: "Оптоволокно", status: "empty", origin: "embedded/block-6-comms-radio/radio-em-waves#6.6.7" },
      { slug: "fiber-in-network", title: "Оптоволокно в мережі", status: "empty", origin: "embedded/undefined#6.10.8" }
      ] },
    { slug: "networks", title: "Мережі", scope: "Топологія, комутація й маршрутизація потоків між вузлами в локальних і глобальних структурах.",
      topics: [
      { slug: "utp-cable", title: "UTP-кабель", status: "empty", origin: "components/comms/utp-cable/" },
      { slug: "on-chip-radio", title: "Радіо на чіпі", status: "empty", origin: "embedded/block-6-comms-radio/wifi-bluetooth#6.5.1" },
      { slug: "channel-band-packet", title: "Канал і пакет", status: "empty", origin: "embedded/block-6-comms-radio/wifi-bluetooth#6.5.2" },
      { slug: "wifi", title: "Wi-Fi", status: "empty", origin: "embedded/block-6-comms-radio/wifi-bluetooth#6.5.3" },
      { slug: "bluetooth-spp", title: "Bluetooth SPP", status: "empty", origin: "embedded/block-6-comms-radio/wifi-bluetooth#6.5.5" },
      { slug: "esp-now", title: "ESP-NOW", status: "empty", origin: "embedded/block-6-comms-radio/wifi-bluetooth#6.5.8" },
      { slug: "latency-reliability", title: "Затримка й надійність", status: "empty", origin: "embedded/block-6-comms-radio/telemetry-mavlink#6.9.4" },
      { slug: "video-transmission", title: "Передача відео", status: "empty", origin: "embedded/block-7-systems/video-signals-2#7.8.6" },
      { slug: "bandwidth-loss", title: "Пропускна й втрати", status: "empty", origin: "embedded/block-7-systems/video-signals-2#7.8.7" },
      { slug: "ethernet-frame", title: "Кадр Ethernet", status: "empty", origin: "embedded/undefined#6.10.1" },
      { slug: "ethernet-link-phy", title: "Фізика лінка", status: "empty", origin: "embedded/undefined#6.10.2" },
      { slug: "mac-ip-arp", title: "MAC, IP і ARP", status: "empty", origin: "embedded/undefined#6.10.3" },
      { slug: "ip-routing", title: "Маршрутизація", status: "empty", origin: "embedded/undefined#6.10.4" },
      { slug: "dhcp-dns", title: "DHCP і DNS", status: "empty", origin: "embedded/undefined#6.10.5" },
      { slug: "nat", title: "NAT", status: "empty", origin: "embedded/undefined#6.10.6" }
      ] },
    { slug: "protocols", title: "Протоколи", scope: "Правила обміну й керування з'єднанням: стеки, рівні, контроль потоку й помилок.",
      topics: [
      { slug: "flow-control", title: "Керування потоком", status: "empty", origin: "embedded/block-6-comms-radio/uart#6.1.5" },
      { slug: "packet-design", title: "Проєктування пакета", status: "empty", origin: "embedded/block-6-comms-radio/uart#6.1.6" },
      { slug: "tcp-vs-udp", title: "TCP проти UDP", status: "empty", origin: "embedded/block-6-comms-radio/wifi-bluetooth#6.5.4" },
      { slug: "ble-gatt", title: "BLE GATT", status: "empty", origin: "embedded/block-6-comms-radio/wifi-bluetooth#6.5.6" },
      { slug: "reliable-link", title: "Надійний обмін", status: "empty", origin: "embedded/block-6-comms-radio/wifi-bluetooth#6.5.7" },
      { slug: "mqtt", title: "MQTT", status: "empty", origin: "embedded/block-6-comms-radio/wifi-bluetooth#6.5.10" },
      { slug: "control-telemetry", title: "Керування й телеметрія", status: "empty", origin: "embedded/block-6-comms-radio/telemetry-mavlink#6.9.1" },
      { slug: "rc-link", title: "RC-лінк", status: "empty", origin: "embedded/block-6-comms-radio/telemetry-mavlink#6.9.2" },
      { slug: "telemetry-stream", title: "Телеметрія", status: "empty", origin: "embedded/block-6-comms-radio/telemetry-mavlink#6.9.3" },
      { slug: "mavlink-packet", title: "Пакет MAVLink", status: "empty", origin: "embedded/block-6-comms-radio/telemetry-mavlink#6.9.5" },
      { slug: "mavlink-message-dictionary", title: "Словник MAVLink", status: "empty", origin: "embedded/undefined#6.11.1" },
      { slug: "coordinate-frames-units", title: "Координати й одиниці", status: "empty", origin: "embedded/undefined#6.11.2" },
      { slug: "stream-rates", title: "Частоти потоків", status: "empty", origin: "embedded/undefined#6.11.3" },
      { slug: "param-protocol", title: "Протокол параметрів", status: "empty", origin: "embedded/undefined#6.11.4" },
      { slug: "mission-protocol", title: "Протокол місій", status: "empty", origin: "embedded/undefined#6.11.5" },
      { slug: "mavlink-commands", title: "Команди MAVLink", status: "empty", origin: "embedded/undefined#6.11.6" },
      { slug: "motion-control-setpoints", title: "Керування рухом", status: "empty", origin: "embedded/undefined#6.11.7" },
      { slug: "mavlink-pitfalls", title: "Граблі MAVLink", status: "empty", origin: "embedded/undefined#6.11.9" },
      { slug: "mavlink-from-ground", title: "MAVLink із землі", status: "empty", origin: "embedded/undefined#7.13.3" }
      ] },
    { slug: "multiple-access", title: "Множинний доступ", scope: "Спільне використання середовища багатьма абонентами через поділ ресурсу й арбітраж.",
      topics: [
      { slug: "clock-stretch-arbitration", title: "Розтягування й арбітраж", status: "empty", origin: "embedded/block-6-comms-radio/i2c#6.2.6" }
      ] },
    { slug: "synchronization", title: "Синхронізація", scope: "Узгодження часу, частоти й фази між передавачем і приймачем, відновлення тактів.",
      topics: [
      { slug: "gnss", title: "GNSS-модуль", status: "empty", origin: "components/comms/undefined" },
      { slug: "baud-rate", title: "Швидкість baud", status: "empty", origin: "embedded/block-6-comms-radio/uart#6.1.3" },
      { slug: "measurement-time", title: "Час вимірювання", status: "empty", origin: "embedded/undefined#5.11.1" },
      { slug: "timestamps", title: "Мітки часу", status: "empty", origin: "embedded/undefined#5.11.2" },
      { slug: "sampling-jitter", title: "Джиттер вибірки", status: "empty", origin: "embedded/undefined#5.11.3" },
      { slug: "synchronous-multi-sensor-read", title: "Синхронне зчитування", status: "empty", origin: "embedded/undefined#5.11.4" },
      { slug: "pps-pulse", title: "PPS-імпульс", status: "empty", origin: "embedded/undefined#5.11.5" },
      { slug: "clock-offset-drift", title: "Дрейф годинників", status: "empty", origin: "embedded/undefined#5.11.6" },
      { slug: "sensor-latency-compensation", title: "Затримка давача", status: "empty", origin: "embedded/undefined#5.11.7" }
      ] },
    { slug: "cryptographic-comm", title: "Криптозв'язок", scope: "Захист конфіденційності, цілісності й автентичності переданих повідомлень.",
      topics: [
      { slug: "mavlink-security", title: "Безпека MAVLink", status: "empty", origin: "embedded/block-6-comms-radio/telemetry-mavlink#6.9.8" }
      ] },
    { slug: "buses", title: "Шини", scope: "Провідний обмін між пристроями на коротких відстанях: послідовні й паралельні інтерфейси.",
      topics: [
      { slug: "i2c-expander", title: "I²C-розширювач", status: "empty", origin: "components/interfaces/undefined" },
      { slug: "usb-c-connector", title: "USB-C конектор", status: "empty", origin: "components/interfaces/usb-c-connector/" },
      { slug: "async-serial", title: "Асинхронна передача", status: "empty", origin: "embedded/block-6-comms-radio/uart#6.1.1" },
      { slug: "uart-frame", title: "Кадр UART", status: "empty", origin: "embedded/block-6-comms-radio/uart#6.1.2" },
      { slug: "i2c-bus", title: "Шина I2C", status: "empty", origin: "embedded/block-6-comms-radio/i2c#6.2.1" },
      { slug: "i2c-addressing", title: "Адресація I2C", status: "empty", origin: "embedded/block-6-comms-radio/i2c#6.2.3" },
      { slug: "start-stop-ack", title: "Старт, стоп, ACK", status: "empty", origin: "embedded/block-6-comms-radio/i2c#6.2.4" },
      { slug: "i2c-transaction", title: "Транзакція I2C", status: "empty", origin: "embedded/block-6-comms-radio/i2c#6.2.5" },
      { slug: "register-map", title: "Регістрова карта", status: "empty", origin: "embedded/block-6-comms-radio/i2c#6.2.7" },
      { slug: "spi-bus", title: "Шина SPI", status: "empty", origin: "embedded/block-6-comms-radio/spi#6.3.1" },
      { slug: "spi-lines", title: "Лінії SPI", status: "empty", origin: "embedded/block-6-comms-radio/spi#6.3.2" },
      { slug: "cpol-cpha", title: "Режими CPOL/CPHA", status: "empty", origin: "embedded/block-6-comms-radio/spi#6.3.3" },
      { slug: "chip-select", title: "Вибір кристала", status: "empty", origin: "embedded/block-6-comms-radio/spi#6.3.4" },
      { slug: "spi-speed", title: "Швидкість SPI", status: "empty", origin: "embedded/block-6-comms-radio/spi#6.3.5" },
      { slug: "spi-vs-i2c", title: "SPI проти I2C", status: "empty", origin: "embedded/block-6-comms-radio/spi#6.3.6" },
      { slug: "single-ended-line-limits", title: "Межі односторонніх ліній", status: "empty", origin: "embedded/undefined#6.4.1" },
      { slug: "differential-pair", title: "Диференційна пара", status: "empty", origin: "embedded/undefined#6.4.2" },
      { slug: "rs-485", title: "RS-485", status: "empty", origin: "embedded/undefined#6.4.3" },
      { slug: "can-arbitration", title: "Арбітраж CAN", status: "empty", origin: "embedded/undefined#6.4.4" },
      { slug: "can-frame-errors", title: "Кадр CAN", status: "empty", origin: "embedded/undefined#6.4.5" },
      { slug: "dronecan", title: "DroneCAN", status: "empty", origin: "embedded/undefined#6.4.6" },
      { slug: "usb-ethernet-differential", title: "USB та Ethernet пари", status: "empty", origin: "embedded/undefined#6.4.7" },
      { slug: "bus-resource-conflicts", title: "Конфлікти шин", status: "empty", origin: "embedded/undefined#6.12.5" }
      ] }
  ]
});
