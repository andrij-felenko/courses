/* manifest.js — кореневий ІНДЕКС книги (генерується трансформом index-from-manifest.js).
   Мета книги + список модулів. Зовнішній модуль — рядок-URL "<slug>/manifest.js"
   (власний per-module файл, що робить window.__MODREG__.push({…})); ще не
   винесені модулі лишаються inline-обʼєктами. Складанням опікується
   scripts/bookbuild.js (assembleBook). Нумерація — М.Р.Т. */
window.BOOK_META = {
  "title": "Вбудована електроніка й автономні системи",
  "subtitle": "Глибокий курс — від заряду в атомі до машинного бачення на борту. Сім модулів, шістдесят розділів, побудованих від першопричин.",
  "shortTitle": "Вбудована електроніка",
  "libraryHref": "index.html",
  "basePath": "embedded/"
};

window.BOOK_MODULES = [
  "block-1-circuits-physics/manifest.js",
  "block-2-components-analog/manifest.js",
  "block-3-digital-processor/manifest.js",
  "block-4-mcu-esp32/manifest.js",
  "block-5-sensors-control/manifest.js",
  "block-6-comms-radio/manifest.js",
  "block-7-systems/manifest.js",
  {
    "n": 8,
    "title": "Схемотехніка власних плат",
    "slug": "block-8-circuit-design",
    "chapters": [
      {
        "n": 1,
        "status": "pending",
        "title": "Від ідеї до структурної схеми"
      },
      {
        "n": 2,
        "status": "pending",
        "title": "Вибір компонентів і розрахунок обв'язки"
      },
      {
        "n": 3,
        "status": "pending",
        "title": "Вузол живлення на схемі"
      },
      {
        "n": 4,
        "status": "pending",
        "title": "Скидання, тактування, прошивання: обв'язка мікроконтролера"
      },
      {
        "n": 5,
        "status": "pending",
        "title": "Інтерфейси назовні й захист виводів"
      },
      {
        "n": 6,
        "status": "pending",
        "title": "SPICE: схема в симуляторі"
      },
      {
        "n": 7,
        "status": "pending",
        "title": "САПР: бібліотеки, символи, нетліст"
      },
      {
        "n": 8,
        "status": "pending",
        "title": "Рев'ю схеми і підготовка до розведення"
      }
    ]
  },
  {
    "n": 9,
    "title": "Плати фізично: розведення, виготовлення, монтаж",
    "slug": "block-9-pcb-layout-assembly",
    "chapters": [
      {
        "n": 1,
        "status": "pending",
        "title": "Плата зсередини: шари, стек, матеріали"
      },
      {
        "n": 2,
        "status": "pending",
        "title": "Трасування сигналів"
      },
      {
        "n": 3,
        "status": "pending",
        "title": "Земля, полігони і EMI плати"
      },
      {
        "n": 4,
        "status": "pending",
        "title": "DFM і DFT: спроєктовано для фабрики"
      },
      {
        "n": 5,
        "status": "pending",
        "title": "Замовлення: файли, фабрика, компоненти"
      },
      {
        "n": 6,
        "status": "pending",
        "title": "Паяння і монтаж"
      },
      {
        "n": 7,
        "status": "pending",
        "title": "Бріг-ап нової плати"
      },
      {
        "n": 8,
        "status": "pending",
        "title": "Ревізії і життя плати"
      },
      {
        "n": 9,
        "status": "pending",
        "title": "Пристрій у корпусі: механіка саморобки"
      }
    ]
  },
  {
    "n": 10,
    "title": "Живлення і енергія",
    "slug": "block-10-power-energy",
    "chapters": [
      {
        "n": 1,
        "status": "pending",
        "title": "Топології перетворювачів"
      },
      {
        "n": 2,
        "status": "pending",
        "title": "Спроєктувати і виміряти перетворювач"
      },
      {
        "n": 3,
        "status": "pending",
        "title": "USB-живлення і розумна зарядка"
      },
      {
        "n": 4,
        "status": "pending",
        "title": "Батареї і заряд"
      },
      {
        "n": 5,
        "status": "pending",
        "title": "Сонячна енергія і MPPT"
      },
      {
        "n": 6,
        "status": "pending",
        "title": "Енергоощадна архітектура"
      },
      {
        "n": 7,
        "status": "pending",
        "title": "Захисти живлення"
      }
    ]
  },
  {
    "n": 11,
    "title": "Автономія і робототехніка",
    "slug": "block-11-autonomy-robotics",
    "chapters": [
      {
        "n": 1,
        "status": "pending",
        "title": "Бортовий Linux і одноплатники"
      },
      {
        "n": 2,
        "status": "pending",
        "title": "ROS2: нервова система робота"
      },
      {
        "n": 3,
        "status": "pending",
        "title": "Сприйняття: лідар, камера, карта"
      },
      {
        "n": 4,
        "status": "pending",
        "title": "Локалізація і ймовірність"
      },
      {
        "n": 5,
        "status": "pending",
        "title": "Планування шляху"
      },
      {
        "n": 6,
        "status": "pending",
        "title": "Локальне керування і обхід перешкод"
      },
      {
        "n": 7,
        "status": "pending",
        "title": "Платформи: ровер, маніпулятор, коптер"
      },
      {
        "n": 8,
        "status": "pending",
        "title": "Симуляція робота"
      }
    ]
  },
  {
    "n": 12,
    "title": "Глибокий ШІ на краю",
    "slug": "block-12-edge-ai",
    "chapters": [
      {
        "n": 1,
        "status": "pending",
        "title": "Навчання по-справжньому: бекпроп і оптимізатори"
      },
      {
        "n": 2,
        "status": "pending",
        "title": "Від CNN до трансформерів"
      },
      {
        "n": 3,
        "status": "pending",
        "title": "Дані і розмітка"
      },
      {
        "n": 4,
        "status": "pending",
        "title": "Стиснення моделей: квантування, прунінг, дистиляція"
      },
      {
        "n": 5,
        "status": "pending",
        "title": "NPU і акселератори"
      },
      {
        "n": 6,
        "status": "pending",
        "title": "MLOps парку пристроїв"
      },
      {
        "n": 7,
        "status": "pending",
        "title": "Надійність ML на краю"
      }
    ]
  },
  {
    "n": 13,
    "title": "UI та HMI на залізі",
    "slug": "block-13-ui-hmi",
    "chapters": [
      {
        "n": 1,
        "status": "done",
        "title": "Дисплеї і дотик як компоненти",
        "dir": "block-13-ui-hmi/displays-touch",
        "main": "displays-touch.md",
        "histories": [
          "hist-lcd.md",
          "hist-eink.md"
        ],
        "extras": [
          "../../../components/displays/ssd1306-oled/ssd1306-oled.md",
          "math-bandwidth-budget.md",
          "../../../components/displays/spi-tft/spi-tft.md",
          "../../../components/displays/backlight-driver/backlight-driver.md",
          "../../../components/displays/touch-controller/touch-controller.md",
          "../../../components/displays/eink-module/eink-module.md"
        ]
      },
      {
        "n": 2,
        "status": "done",
        "title": "Графічний конвеєр",
        "dir": "block-13-ui-hmi/graphics-pipeline",
        "main": "graphics-pipeline.md",
        "histories": [
          "hist-alto.md"
        ]
      },
      {
        "n": 3,
        "status": "pending",
        "title": "Архітектура UI-застосунку"
      },
      {
        "n": 4,
        "status": "pending",
        "title": "Qt: від десктопа до MCU"
      },
      {
        "n": 5,
        "status": "pending",
        "title": "LVGL і TouchGFX"
      },
      {
        "n": 6,
        "status": "pending",
        "title": "Slint, Embedded Wizard і вибір фреймворку"
      },
      {
        "n": 7,
        "status": "pending",
        "title": "Практичні патерни UI на залізі"
      }
    ]
  },
  {
    "n": 14,
    "title": "Продукт: від прототипа до серії",
    "slug": "block-14-product",
    "chapters": [
      {
        "n": 1,
        "status": "pending",
        "title": "Вимоги і архітектура виробу"
      },
      {
        "n": 2,
        "status": "pending",
        "title": "DFM і вартість BOM"
      },
      {
        "n": 3,
        "status": "pending",
        "title": "EMC і сертифікація"
      },
      {
        "n": 4,
        "status": "pending",
        "title": "Тестування: від юнітів до HIL і фабрики"
      },
      {
        "n": 5,
        "status": "pending",
        "title": "Надійність і аналіз відмов"
      },
      {
        "n": 6,
        "status": "pending",
        "title": "OTA-флот і версіонування"
      },
      {
        "n": 7,
        "status": "pending",
        "title": "Безпека продукту"
      },
      {
        "n": 8,
        "status": "pending",
        "title": "Документація, постачання, підтримка"
      },
      {
        "n": 9,
        "status": "pending",
        "title": "Пристрій в екосистемі: стільниковий IoT, Matter і хмара"
      }
    ]
  }
];
