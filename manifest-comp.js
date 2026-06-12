/* ──────────────────────────────────────────────────────────────────────────
   manifest-comp.js — структура книги «Компоненти»
   Каталог реальних компонентів ЗА СЕКТОРАМИ. Це згрупований вигляд тих самих
   прикладних 🔌-тем, що живуть у книгах курсу: текст не переїжджає — книга
   «Компоненти» дає вхід «за пристроєм», а прикладні теми далі лінкуються
   inline-popup'ом (just-in-time). Теми-стаби (status:"pending", «в розробці»)
   наповнюються за першим крос-лінком book:components/<slug>.

   Модулі = сектори (давачі / живлення / зв'язок / приводи / пам'ять /
   інтерфейси / захист); «розділи» (chapters) = окремі компоненти.
   ────────────────────────────────────────────────────────────────────────── */
window.BOOK = {
  title: "Компоненти",
  subtitle: "Каталог компонентів за секторами — давачі, живлення, зв'язок, приводи, " +
            "пам'ять, інтерфейси, захист. Той самий матеріал, що в прикладних темах " +
            "інших книг, але згрупований за фізичними пристроями.",
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
        { n: "9", status: "pending", title: "IMU-плата (MPU-клас, BMI-клас)" }
      ]
    },
    {
      n: 2, title: "Живлення", slug: "power",
      chapters: [
        { n: "1", status: "pending", title: "Лінійний стабілізатор (LDO)" },
        { n: "2", status: "pending", title: "Понижувальний перетворювач (buck)" },
        { n: "3", status: "pending", title: "Підвищувальний перетворювач (boost)" },
        { n: "4", status: "pending", title: "Зарядка Li-ion (TP4056-клас)" }
      ]
    },
    {
      n: 3, title: "Зв'язок", slug: "comms",
      chapters: [
        { n: "1", status: "pending", title: "Радіомодуль (nRF24-клас)" },
        { n: "2", status: "pending", title: "LoRa-модуль" },
        { n: "3", status: "pending", title: "GNSS-модуль (NEO-клас) і вихід PPS" }
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
        { n: "3", status: "pending", title: "microSD-картка" }
      ]
    },
    {
      n: 6, title: "Інтерфейси", slug: "interfaces",
      chapters: [
        { n: "1", status: "pending", title: "Розширювач портів I²C (PCF8574-клас)" },
        { n: "2", status: "pending", title: "Зсувний регістр (74HC595)" },
        { n: "3", status: "pending", title: "Перетворювач рівнів логіки" }
      ]
    },
    {
      n: 7, title: "Захист", slug: "protection",
      chapters: [
        { n: "1", status: "pending", title: "Запобіжник і самовідновний (PTC)" },
        { n: "2", status: "pending", title: "TVS-діод і захист від ESD" },
        { n: "3", status: "pending", title: "Захист від переполюсування" }
      ]
    }
  ]
};
