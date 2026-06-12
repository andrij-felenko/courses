/* ──────────────────────────────────────────────────────────────────────────
   manifest-comp.js — структура книги «Компоненти»
   Каталог реальних компонентів ЗА СЕКТОРАМИ. Це згрупований вигляд тих самих
   прикладних 🔌-тем, що живуть у книгах курсу: текст не переїжджає — книга
   «Компоненти» дає вхід «за пристроєм», а прикладні теми далі лінкуються
   inline-popup'ом (just-in-time). Теми-стаби (status:"pending", «в розробці»)
   наповнюються за першим крос-лінком book:components/<slug>.

   Модулі = сектори (давачі / живлення / зв'язок / приводи / пам'ять /
   інтерфейси / захист / пасивні / активні / дисплеї); «розділи» (chapters) =
   окремі компоненти.
   ────────────────────────────────────────────────────────────────────────── */
window.BOOK = {
  title: "Компоненти",
  subtitle: "Каталог компонентів за секторами — давачі, живлення, зв'язок, приводи, " +
            "пам'ять, інтерфейси, захист, пасивні, активні, дисплеї. Той самий матеріал, " +
            "що в прикладних темах інших книг, але згрупований за фізичними пристроями.",
  shortTitle: "Компоненти",
  libraryHref: "index.html",
  basePath: "components/",

  modules: [
    {
      n: 1, title: "Давачі", slug: "sensors",
      chapters: [
        { n: "1", status: "pending", title: "NTC-термістор: опір як термометр" },
        { n: "2", status: "pending", title: "Фоторезистор, фотодіод, фототранзистор" },
        { n: "3", status: "pending", title: "Інструментальний підсилювач (INA-клас)" },
        { n: "4", status: "pending", title: "Монітор струму з шунтом (INA219-клас)" },
        { n: "5", status: "pending", title: "Давач струму на ефекті Холла (ACS712-клас)" },
        { n: "6", status: "pending", title: "Тензобалка з підсилювачем (HX711-клас)" },
        { n: "7", status: "pending", title: "Ультразвуковий далекомір (HC-SR04-клас)" },
        { n: "8", status: "pending", title: "Лазерний ToF-модуль (VL53-клас)" },
        { n: "9", status: "pending", title: "IMU-плата (MPU-клас, BMI-клас)" },
        { n: "10", status: "done", slug: "clamp-meter", dir: "sensors/clamp-meter/", main: "clamp-meter.md", title: "Кліщі струмові (clamp meter)" }
      ]
    },
    {
      n: 2, title: "Живлення", slug: "power",
      chapters: [
        { n: "1", status: "pending", title: "Лінійний стабілізатор (LDO)" },
        { n: "2", status: "pending", title: "Понижувальний перетворювач (buck)" },
        { n: "3", status: "pending", title: "Підвищувальний перетворювач (boost)" },
        { n: "4", status: "pending", title: "Зарядка Li-ion (TP4056-клас)" },
        { n: "5", status: "done", slug: "tp4056-charger", dir: "power/tp4056-charger/", main: "tp4056-charger.md", title: "TP4056: зарядний контролер Li-ion" },
        { n: "6", status: "done", slug: "fuel-gauge", dir: "power/fuel-gauge/", main: "fuel-gauge.md", title: "Fuel gauge: лічильник заряду" },
        { n: "7", status: "done", slug: "usb-cc-resistors", dir: "power/usb-cc-resistors/", main: "usb-cc-resistors.md", title: "USB CC-резистори" },
        { n: "8", status: "done", slug: "usb-pd-sink", dir: "power/usb-pd-sink/", main: "usb-pd-sink.md", title: "USB PD sink-контролер" },
        { n: "9", status: "done", slug: "power-path", dir: "power/power-path/", main: "power-path.md", title: "Power-path менеджер" },
        { n: "10", status: "done", slug: "sync-rectifier", dir: "power/sync-rectifier/", main: "sync-rectifier.md", title: "Синхронний випрямляч" },
        { n: "11", status: "done", slug: "charge-pump", dir: "power/charge-pump/", main: "charge-pump.md", title: "Charge pump (індуктивний без)" },
        { n: "12", status: "done", slug: "wall-adapter", dir: "power/wall-adapter/", main: "wall-adapter.md", title: "Мережевий адаптер (wall adapter)" },
        { n: "13", status: "done", slug: "dc-dc-module", dir: "power/dc-dc-module/", main: "dc-dc-module.md", title: "DC-DC модуль живлення" },
        { n: "14", status: "done", slug: "electronic-load", dir: "power/electronic-load/", main: "electronic-load.md", title: "Електронне навантаження" }
      ]
    },
    {
      n: 3, title: "Зв'язок", slug: "comms",
      chapters: [
        { n: "1", status: "pending", title: "Радіомодуль (nRF24-клас)" },
        { n: "2", status: "pending", title: "LoRa-модуль" },
        { n: "3", status: "pending", title: "GNSS-модуль (NEO-клас) і вихід PPS" },
        { n: "4", status: "done", slug: "nfc-rfid", dir: "comms/nfc-rfid/", main: "nfc-rfid.md", title: "NFC/RFID-модуль" },
        { n: "5", status: "done", slug: "utp-cable", dir: "comms/utp-cable/", main: "utp-cable.md", title: "UTP-кабель (витата пара)" },
        { n: "6", status: "done", slug: "shielded-cable", dir: "comms/shielded-cable/", main: "shielded-cable.md", title: "Екранований кабель" },
        { n: "7", status: "done", slug: "wroom-module", dir: "comms/wroom-module/", main: "wroom-module.md", title: "ESP32-WROOM модуль" },
        { n: "8", status: "done", slug: "esp32-antenna", dir: "comms/esp32-antenna/", main: "esp32-antenna.md", title: "Антена ESP32" }
      ]
    },
    {
      n: 4, title: "Приводи", slug: "actuators",
      chapters: [
        { n: "1", status: "pending", title: "Мотор-редуктор (TT-клас)" },
        { n: "2", status: "pending", title: "Драйвер DC-моторів (L298-клас, TB6612-клас)" },
        { n: "3", status: "pending", title: "Драйвер крокового (A4988-клас, TMC-клас)" },
        { n: "4", status: "pending", title: "Hobby-серво (SG90-клас, MG996-клас)" },
        { n: "5", status: "pending", title: "PWM-розширювач (PCA9685-клас)" }
      ]
    },
    {
      n: 5, title: "Пам'ять", slug: "memory",
      chapters: [
        { n: "1", status: "pending", title: "SPI-флеш" },
        { n: "2", status: "pending", title: "EEPROM по I²C" },
        { n: "3", status: "pending", title: "microSD-картка" },
        { n: "4", status: "done", slug: "psram", dir: "memory/psram/", main: "psram.md", title: "PSRAM (псевдостатична RAM)" }
      ]
    },
    {
      n: 6, title: "Інтерфейси", slug: "interfaces",
      chapters: [
        { n: "1", status: "pending", title: "Розширювач портів I²C (PCF8574-клас)" },
        { n: "2", status: "pending", title: "Зсувний регістр (74HC595)" },
        { n: "3", status: "pending", title: "Перетворювач рівнів логіки" },
        { n: "4", status: "done", slug: "usb-c-connector", dir: "interfaces/usb-c-connector/", main: "usb-c-connector.md", title: "USB-C конектор" },
        { n: "5", status: "done", slug: "solenoid-relay", dir: "interfaces/solenoid-relay/", main: "solenoid-relay.md", title: "Соленоїд і реле" },
        { n: "6", status: "done", slug: "74hc165-piso", dir: "interfaces/74hc165-piso/", main: "74hc165-piso.md", title: "74HC165: паралельний вхід / послідовний вихід" },
        { n: "7", status: "done", slug: "74hc595-sipo", dir: "interfaces/74hc595-sipo/", main: "74hc595-sipo.md", title: "74HC595: послідовний вхід / паралельний вихід" },
        { n: "8", status: "done", slug: "74hc138-decoder", dir: "interfaces/74hc138-decoder/", main: "74hc138-decoder.md", title: "74HC138: дешифратор / chip-select" },
        { n: "9", status: "done", slug: "gpio-expander", dir: "interfaces/gpio-expander/", main: "gpio-expander.md", title: "GPIO-розширювач" }
      ]
    },
    {
      n: 7, title: "Захист", slug: "protection",
      chapters: [
        { n: "1", status: "pending", title: "Запобіжник і самовідновний (PTC)" },
        { n: "2", status: "pending", title: "TVS-діод і захист від ESD" },
        { n: "3", status: "pending", title: "Захист від переполюсування" },
        { n: "4", status: "done", slug: "gas-discharge-tube", dir: "protection/gas-discharge-tube/", main: "gas-discharge-tube.md", title: "Газорозрядник (GDT / spark gap)" },
        { n: "5", status: "done", slug: "battery-protection-ic", dir: "protection/battery-protection-ic/", main: "battery-protection-ic.md", title: "Мікросхема захисту акумулятора (DW01-клас)" },
        { n: "6", status: "done", slug: "mov-varistor", dir: "protection/mov-varistor/", main: "mov-varistor.md", title: "MOV-варистор" },
        { n: "7", status: "done", slug: "inrush-ntc", dir: "protection/inrush-ntc/", main: "inrush-ntc.md", title: "Inrush NTC термістор" },
        { n: "8", status: "done", slug: "fuse-types", dir: "protection/fuse-types/", main: "fuse-types.md", title: "Типи запобіжників" },
        { n: "9", status: "done", slug: "crowbar", dir: "protection/crowbar/", main: "crowbar.md", title: "Crowbar-захист" }
      ]
    },
    {
      n: 8, title: "Пасивні", slug: "passive",
      chapters: [
        { n: "1", status: "done", slug: "mlcc", dir: "passive/mlcc/", main: "mlcc.md", title: "MLCC-конденсатор" },
        { n: "2", status: "done", slug: "electrolytic", dir: "passive/electrolytic/", main: "electrolytic.md", title: "Електролітичний та танталовий конденсатор" },
        { n: "3", status: "done", slug: "capacitor-marking", dir: "passive/capacitor-marking/", main: "capacitor-marking.md", title: "Маркування конденсаторів і типорозміри" },
        { n: "4", status: "done", slug: "bleeder", dir: "passive/bleeder/", main: "bleeder.md", title: "Розрядний резистор (bleeder)" },
        { n: "5", status: "done", slug: "decoupling", dir: "passive/decoupling/", main: "decoupling.md", title: "Розв'язувальний конденсатор (decoupling)" },
        { n: "6", status: "done", slug: "supercap", dir: "passive/supercap/", main: "supercap.md", title: "Суперконденсатор (backup)" },
        { n: "7", status: "done", slug: "power-inductor", dir: "passive/power-inductor/", main: "power-inductor.md", title: "Силовий дросель" },
        { n: "8", status: "done", slug: "transformer", dir: "passive/transformer/", main: "transformer.md", title: "Трансформатор" },
        { n: "9", status: "done", slug: "ferrite-clamp", dir: "passive/ferrite-clamp/", main: "ferrite-clamp.md", title: "Феритова клема (ferrite clamp)" },
        { n: "10", status: "done", slug: "resistor-marking", dir: "passive/resistor-marking/", main: "resistor-marking.md", title: "Маркування резисторів" },
        { n: "11", status: "done", slug: "wire-gauge", dir: "passive/wire-gauge/", main: "wire-gauge.md", title: "Калібр проводу (AWG/мм²)" },
        { n: "12", status: "done", slug: "kelvin-shunt", dir: "passive/kelvin-shunt/", main: "kelvin-shunt.md", title: "Шунт Кельвіна" },
        { n: "13", status: "done", slug: "heatsink", dir: "passive/heatsink/", main: "heatsink.md", title: "Радіатор охолодження" },
        { n: "14", status: "done", slug: "peltier", dir: "passive/peltier/", main: "peltier.md", title: "Елемент Пельтьє" },
        { n: "15", status: "done", slug: "magnet-grades", dir: "passive/magnet-grades/", main: "magnet-grades.md", title: "Класи постійних магнітів" },
        { n: "16", status: "done", slug: "ferrite-bead", dir: "passive/ferrite-bead/", main: "ferrite-bead.md", title: "Феритова намистина (ferrite bead)" },
        { n: "17", status: "done", slug: "watch-crystal", dir: "passive/watch-crystal/", main: "watch-crystal.md", title: "Годинниковий кварц" },
        { n: "18", status: "done", slug: "potentiometer", dir: "passive/potentiometer/", main: "potentiometer.md", title: "Потенціометр" },
        { n: "19", status: "done", slug: "packages", dir: "passive/packages/", main: "packages.md", title: "Корпуси компонентів (packages)" },
        { n: "20", status: "done", slug: "smd-marking", dir: "passive/smd-marking/", main: "smd-marking.md", title: "Маркування SMD-компонентів" }
      ]
    },
    {
      n: 9, title: "Активні", slug: "active",
      chapters: [
        { n: "1", status: "done", slug: "diode-families", dir: "active/diode-families/", main: "diode-families.md", title: "Родини діодів" },
        { n: "2", status: "done", slug: "bjt-families", dir: "active/bjt-families/", main: "bjt-families.md", title: "Родини BJT-транзисторів" },
        { n: "3", status: "done", slug: "darlington-uln", dir: "active/darlington-uln/", main: "darlington-uln.md", title: "Дарлінгтон і ULN" },
        { n: "4", status: "done", slug: "mosfet-body-diode", dir: "active/mosfet-body-diode/", main: "mosfet-body-diode.md", title: "MOSFET body-діод" },
        { n: "5", status: "done", slug: "gate-driver", dir: "active/gate-driver/", main: "gate-driver.md", title: "Gate driver" },
        { n: "6", status: "done", slug: "logic-level-mosfet", dir: "active/logic-level-mosfet/", main: "logic-level-mosfet.md", title: "Logic-level MOSFET" },
        { n: "7", status: "done", slug: "pmos-load-switch", dir: "active/pmos-load-switch/", main: "pmos-load-switch.md", title: "P-MOS load switch" },
        { n: "8", status: "done", slug: "ideal-diode-ic", dir: "active/ideal-diode-ic/", main: "ideal-diode-ic.md", title: "Ideal diode IC" },
        { n: "9", status: "done", slug: "comparator-ics", dir: "active/comparator-ics/", main: "comparator-ics.md", title: "Компараторні мікросхеми" },
        { n: "10", status: "done", slug: "rail-to-rail-opamp", dir: "active/rail-to-rail-opamp/", main: "rail-to-rail-opamp.md", title: "Rail-to-rail операційний підсилювач" },
        { n: "11", status: "done", slug: "ldo-module", dir: "active/ldo-module/", main: "ldo-module.md", title: "LDO-модуль" },
        { n: "12", status: "done", slug: "optocoupler", dir: "active/optocoupler/", main: "optocoupler.md", title: "Оптопара" },
        { n: "13", status: "done", slug: "bridge-rectifier", dir: "active/bridge-rectifier/", main: "bridge-rectifier.md", title: "Діодний міст" },
        { n: "14", status: "done", slug: "led-practice", dir: "active/led-practice/", main: "led-practice.md", title: "LED: практика підключення" },
        { n: "15", status: "done", slug: "tvs-diode", dir: "active/tvs-diode/", main: "tvs-diode.md", title: "TVS-діод" },
        { n: "16", status: "done", slug: "logic-74-families", dir: "active/logic-74-families/", main: "logic-74-families.md", title: "Родини логіки 74-серії" },
        { n: "17", status: "done", slug: "schmitt-74hc14", dir: "active/schmitt-74hc14/", main: "schmitt-74hc14.md", title: "74HC14: тригер Шмітта" },
        { n: "18", status: "done", slug: "tl431", dir: "active/tl431/", main: "tl431.md", title: "TL431: програмований стабілітрон" },
        { n: "19", status: "done", slug: "analog-mux", dir: "active/analog-mux/", main: "analog-mux.md", title: "Аналоговий мультиплексор" },
        { n: "20", status: "done", slug: "ssr", dir: "active/ssr/", main: "ssr.md", title: "Твердотільне реле (SSR)" }
      ]
    },
    {
      n: 10, title: "Дисплеї", slug: "displays",
      chapters: [
        { n: "1", status: "done", slug: "ssd1306-oled", dir: "displays/ssd1306-oled/", main: "ssd1306-oled.md", title: "SSD1306 OLED" },
        { n: "2", status: "done", slug: "spi-tft", dir: "displays/spi-tft/", main: "spi-tft.md", title: "SPI TFT-дисплей" },
        { n: "3", status: "done", slug: "backlight-driver", dir: "displays/backlight-driver/", main: "backlight-driver.md", title: "Драйвер підсвічування" },
        { n: "4", status: "done", slug: "eink-module", dir: "displays/eink-module/", main: "eink-module.md", title: "E-ink модуль" },
        { n: "5", status: "done", slug: "touch-controller", dir: "displays/touch-controller/", main: "touch-controller.md", title: "Контролер сенсорного екрана" }
      ]
    }
  ]
};
