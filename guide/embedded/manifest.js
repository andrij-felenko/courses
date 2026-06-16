/* guide/embedded/manifest.js — КУРС (тип "guide").
   Доріжка-надбудова: впорядковані кроки-посилання (ref) на теми книг book/<книга>/<галузь>/<slug>,
   плюс згодом власні теми-містки (kind:"bridge"). Зібрано з кроку 4 (origin→ref).
   Схема: { type:"guide", slug, title, modules:[ {n,slug,title, chapters:[ {title, steps:[ {ref,title} | {bridge,slug,title} ]} ]} ] } */
(window.__GUIDES__ = window.__GUIDES__ || []).push({
  type: "guide",
  slug: "embedded",
  title: "Вбудована електроніка й автономні системи",
  modules: [
  {
    "n": 1,
    "slug": "block-1-circuits-physics",
    "title": "Фізика електрики й кіл",
    "chapters": [
      {
        "title": "Заряд, електричне поле й потенціал",
        "steps": [
          {
            "ref": "physics/electromagnetism/electric-charge",
            "title": "Заряд"
          },
          {
            "ref": "physics/electromagnetism/coulomb-law",
            "title": "Закон Кулона"
          },
          {
            "ref": "physics/electromagnetism/electric-field",
            "title": "Електричне поле"
          },
          {
            "ref": "physics/electromagnetism/electric-potential",
            "title": "Потенціал"
          },
          {
            "ref": "physics/electromagnetism/volt",
            "title": "Вольт"
          },
          {
            "ref": "physics/electromagnetism/field-and-potential",
            "title": "Поле й потенціал"
          },
          {
            "ref": "physics/electromagnetism/electrostatics-summary",
            "title": "Зведення електростатики"
          },
          {
            "ref": "physics/electromagnetism/faraday-cage",
            "title": "Клітка Фарадея"
          }
        ]
      },
      {
        "title": "Напруга, струм і провідність",
        "steps": [
          {
            "ref": "physics/electromagnetism/electric-current",
            "title": "Струм"
          },
          {
            "ref": "physics/electromagnetism/current-direction",
            "title": "Напрямок струму"
          },
          {
            "ref": "physics/condensed-matter-physics/electron-drift",
            "title": "Дрейф електронів"
          },
          {
            "ref": "physics/electromagnetism/signal-speed",
            "title": "Швидкість сигналу"
          },
          {
            "ref": "physics/electromagnetism/current-continuity",
            "title": "Неперервність струму"
          },
          {
            "ref": "physics/electromagnetism/voltage",
            "title": "Напруга"
          },
          {
            "ref": "physics/electromagnetism/closed-circuit",
            "title": "Замкнене коло"
          },
          {
            "ref": "physics/condensed-matter-physics/conductors-insulators",
            "title": "Провідники й діелектрики"
          },
          {
            "ref": "physics/condensed-matter-physics/resistance-origin",
            "title": "Природа опору"
          },
          {
            "ref": "physics/condensed-matter-physics/conductivity",
            "title": "Провідність"
          },
          {
            "ref": "physics/electromagnetism/ionic-conduction",
            "title": "Іонна провідність"
          },
          {
            "ref": "physics/electromagnetism/dc-vs-ac",
            "title": "DC і AC"
          },
          {
            "ref": "physics/electromagnetism/current-safety",
            "title": "Електробезпека"
          }
        ]
      },
      {
        "title": "Опір, потужність і тепло",
        "steps": [
          {
            "ref": "physics/condensed-matter-physics/resistance",
            "title": "Опір"
          },
          {
            "ref": "electronics/analog/ohms-law",
            "title": "Закон Ома"
          },
          {
            "ref": "physics/condensed-matter-physics/resistivity",
            "title": "Питомий опір"
          },
          {
            "ref": "physics/condensed-matter-physics/resistance-temperature",
            "title": "Опір і температура"
          },
          {
            "ref": "physics/electromagnetism/electric-power",
            "title": "Потужність"
          },
          {
            "ref": "physics/electromagnetism/joule-heating",
            "title": "Джоулеве тепло"
          },
          {
            "ref": "electronics/components/resistor",
            "title": "Резистор"
          },
          {
            "ref": "electronics/components/fuses-ptc",
            "title": "Запобіжники"
          },
          {
            "ref": "physics/thermal-statistical/thermal-resistance",
            "title": "Тепловий опір"
          },
          {
            "ref": "physics/thermal-statistical/heat-transfer",
            "title": "Передача тепла"
          }
        ]
      },
      {
        "title": "Закони Кірхгофа й аналіз кіл",
        "steps": [
          {
            "ref": "electronics/analog/nodes-branches-loops",
            "title": "Вузли й контури"
          },
          {
            "ref": "electronics/analog/kcl",
            "title": "Закон струмів Кірхгофа"
          },
          {
            "ref": "electronics/analog/kvl",
            "title": "Закон напруг Кірхгофа"
          },
          {
            "ref": "electronics/analog/series-connection",
            "title": "Послідовне з'єднання"
          },
          {
            "ref": "electronics/analog/parallel-connection",
            "title": "Паралельне з'єднання"
          },
          {
            "ref": "electronics/analog/voltage-divider",
            "title": "Дільник напруги"
          },
          {
            "ref": "electronics/analog/current-divider",
            "title": "Дільник струму"
          },
          {
            "ref": "electronics/analog/circuit-analysis",
            "title": "Аналіз кіл"
          },
          {
            "ref": "electronics/analog/wheatstone-bridge",
            "title": "Міст Вітстона"
          }
        ]
      },
      {
        "title": "Еквівалентні схеми: Тевенін, Нортон, суперпозиція",
        "steps": [
          {
            "ref": "electronics/analog/internal-resistance",
            "title": "Внутрішній опір"
          },
          {
            "ref": "electronics/analog/superposition",
            "title": "Суперпозиція"
          },
          {
            "ref": "electronics/analog/thevenin",
            "title": "Теорема Тевеніна"
          },
          {
            "ref": "electronics/analog/norton",
            "title": "Теорема Нортона"
          },
          {
            "ref": "electronics/analog/thevenin-equivalent",
            "title": "Пошук еквівалента"
          },
          {
            "ref": "electronics/analog/power-matching",
            "title": "Узгодження потужності"
          }
        ]
      },
      {
        "title": "Мова схем і вимірювання",
        "steps": [
          {
            "ref": "electronics/analog/schematic-purpose",
            "title": "Принципова схема"
          },
          {
            "ref": "electronics/analog/component-symbols",
            "title": "Умовні позначення"
          },
          {
            "ref": "electronics/analog/nodes-connections",
            "title": "Вузли й з'єднання"
          },
          {
            "ref": "electronics/analog/ground-power-rails",
            "title": "Земля й шини"
          },
          {
            "ref": "electronics/analog/reading-schematics",
            "title": "Читання схем"
          },
          {
            "ref": "electronics/metrology/multimeter",
            "title": "Мультиметр"
          },
          {
            "ref": "electronics/metrology/oscilloscope",
            "title": "Осцилограф"
          },
          {
            "ref": "electronics/metrology/measurement-errors",
            "title": "Похибки вимірювань"
          },
          {
            "ref": "electronics/metrology/logic-analyzer",
            "title": "Логічний аналізатор"
          },
          {
            "ref": "electronics/metrology/lab-power-supply",
            "title": "Блок живлення"
          }
        ]
      },
      {
        "title": "Змінний струм: синусоїда, фаза й RMS",
        "steps": [
          {
            "ref": "physics/oscillations-waves/sine-wave",
            "title": "Синусоїда"
          },
          {
            "ref": "physics/oscillations-waves/amplitude-frequency",
            "title": "Амплітуда й частота"
          },
          {
            "ref": "physics/oscillations-waves/phase",
            "title": "Фаза"
          },
          {
            "ref": "physics/electromagnetism/rms-value",
            "title": "Діюче значення"
          },
          {
            "ref": "electronics/metrology/sine-on-scope",
            "title": "Синусоїда на осцилографі"
          },
          {
            "ref": "physics/electromagnetism/ac-power-grid",
            "title": "Змінна мережа"
          }
        ]
      },
      {
        "title": "Магнетизм і електромагніти",
        "steps": [
          {
            "ref": "physics/electromagnetism/magnetic-field",
            "title": "Магнітне поле"
          },
          {
            "ref": "physics/condensed-matter-physics/ferromagnetism",
            "title": "Феромагнетизм"
          },
          {
            "ref": "physics/condensed-matter-physics/permanent-magnets",
            "title": "Постійні магніти"
          },
          {
            "ref": "physics/electromagnetism/oersted-experiment",
            "title": "Дослід Ерстеда"
          },
          {
            "ref": "physics/electromagnetism/electromagnet",
            "title": "Електромагніт"
          },
          {
            "ref": "physics/condensed-matter-physics/saturation-hysteresis",
            "title": "Насичення й гістерезис"
          },
          {
            "ref": "physics/electromagnetism/ampere-force",
            "title": "Сила Ампера"
          },
          {
            "ref": "physics/electromagnetism/hall-effect",
            "title": "Ефект Холла"
          },
          {
            "ref": "physics/electromagnetism/earth-magnetic-field",
            "title": "Поле Землі"
          },
          {
            "ref": "physics/electromagnetism/electromagnetic-induction",
            "title": "Електромагнітна індукція"
          }
        ]
      },
      {
        "title": "Шум і завади: фізичні джерела",
        "steps": [
          {
            "ref": "physics/electromagnetism/noise-interference",
            "title": "Шум і завади"
          },
          {
            "ref": "physics/thermal-statistical/thermal-noise",
            "title": "Тепловий шум"
          },
          {
            "ref": "physics/condensed-matter-physics/shot-flicker-noise",
            "title": "Дробовий шум"
          },
          {
            "ref": "physics/electromagnetism/capacitive-coupling",
            "title": "Ємнісна наводка"
          },
          {
            "ref": "physics/electromagnetism/inductive-coupling",
            "title": "Індуктивна наводка"
          },
          {
            "ref": "electronics/pcb/ground-loops",
            "title": "Земляні петлі"
          },
          {
            "ref": "electronics/pcb/shielding",
            "title": "Екранування"
          },
          {
            "ref": "electronics/pcb/twisted-pair",
            "title": "Вита пара"
          },
          {
            "ref": "electronics/metrology/noise-hunting",
            "title": "Полювання на заваду"
          }
        ]
      },
      {
        "title": "Електростатика на практиці: іскри, блискавка й ESD",
        "steps": [
          {
            "ref": "physics/electromagnetism/triboelectricity",
            "title": "Трибоелектрика"
          },
          {
            "ref": "physics/electromagnetism/body-charge",
            "title": "Заряд тіла"
          },
          {
            "ref": "physics/condensed-matter-physics/air-breakdown",
            "title": "Пробій повітря"
          },
          {
            "ref": "physics/electromagnetism/lightning",
            "title": "Блискавка"
          },
          {
            "ref": "electronics/microelectronics/esd-damage",
            "title": "ESD-пошкодження"
          },
          {
            "ref": "electronics/pcb/antistatic-workplace",
            "title": "Антистатичне місце"
          },
          {
            "ref": "electronics/pcb/esd-packaging",
            "title": "ESD-пакування"
          },
          {
            "ref": "physics/electromagnetism/humidity-static-control",
            "title": "Вологість і статика"
          }
        ]
      }
    ]
  },
  {
    "n": 2,
    "slug": "block-2-components-analog",
    "title": "Компоненти й аналогова електроніка",
    "chapters": [
      {
        "title": "Конденсатор",
        "steps": [
          {
            "ref": "electronics/components/capacitor",
            "title": "Конденсатор"
          },
          {
            "ref": "electronics/components/capacitance",
            "title": "Ємність"
          },
          {
            "ref": "electronics/components/capacitor-energy",
            "title": "Енергія конденсатора"
          },
          {
            "ref": "electronics/analog/rc-time-constant",
            "title": "Стала RC"
          },
          {
            "ref": "electronics/components/capacitor-parasitics",
            "title": "Паразити конденсатора"
          },
          {
            "ref": "electronics/components/capacitor-uses",
            "title": "Застосування конденсаторів"
          },
          {
            "ref": "electronics/components/capacitors-series-parallel",
            "title": "Конденсатори: з'єднання"
          },
          {
            "ref": "electronics/components/supercapacitor",
            "title": "Суперконденсатор"
          }
        ]
      },
      {
        "title": "Котушка та індуктивність",
        "steps": [
          {
            "ref": "electronics/components/inductor-coil",
            "title": "Котушка"
          },
          {
            "ref": "electronics/components/inductance",
            "title": "Індуктивність"
          },
          {
            "ref": "electronics/components/inductor-energy",
            "title": "Енергія котушки"
          },
          {
            "ref": "electronics/analog/rl-time-constant",
            "title": "Стала RL"
          },
          {
            "ref": "electronics/components/inductor-kickback",
            "title": "Брикання котушки"
          },
          {
            "ref": "electronics/components/mutual-inductance",
            "title": "Взаємоіндукція"
          },
          {
            "ref": "electronics/components/inductor-types",
            "title": "Типи котушок"
          },
          {
            "ref": "electronics/components/ferrite-beads",
            "title": "Ферити"
          }
        ]
      },
      {
        "title": "Реактивність, фази й резонанс",
        "steps": [
          {
            "ref": "electronics/analog/reactance",
            "title": "Реактивність"
          },
          {
            "ref": "electronics/analog/capacitive-reactance",
            "title": "Опір конденсатора"
          },
          {
            "ref": "electronics/analog/inductive-reactance",
            "title": "Опір котушки"
          },
          {
            "ref": "electronics/analog/phase-shift",
            "title": "Зсув фаз"
          },
          {
            "ref": "electronics/analog/lc-resonance",
            "title": "LC-резонанс"
          },
          {
            "ref": "electronics/analog/quality-factor",
            "title": "Добротність Q"
          },
          {
            "ref": "electronics/analog/rlc-selectivity",
            "title": "RLC-вибірковість"
          }
        ]
      },
      {
        "title": "АЧХ, децибели й фільтри",
        "steps": [
          {
            "ref": "electronics/analog/frequency-response",
            "title": "Частотна характеристика"
          },
          {
            "ref": "electronics/analog/rc-low-pass",
            "title": "RC-ФНЧ"
          },
          {
            "ref": "electronics/analog/rc-high-pass",
            "title": "RC-ФВЧ"
          },
          {
            "ref": "electronics/analog/decibels",
            "title": "Децибели"
          },
          {
            "ref": "electronics/analog/bode-plot",
            "title": "Діаграма Боде"
          },
          {
            "ref": "electronics/analog/bandwidth-3db",
            "title": "Смуга −3 дБ"
          },
          {
            "ref": "electronics/analog/lc-rlc-filters",
            "title": "LC-фільтри"
          }
        ]
      },
      {
        "title": "Діод і PN-перехід",
        "steps": [
          {
            "ref": "physics/condensed-matter-physics/semiconductor",
            "title": "Напівпровідник"
          },
          {
            "ref": "physics/condensed-matter-physics/doping",
            "title": "Легування"
          },
          {
            "ref": "physics/condensed-matter-physics/pn-junction",
            "title": "PN-перехід"
          },
          {
            "ref": "electronics/components/diode-bias",
            "title": "Зміщення діода"
          },
          {
            "ref": "electronics/components/diode-iv-curve",
            "title": "ВАХ діода"
          },
          {
            "ref": "electronics/power-electronics/rectification",
            "title": "Випрямлення"
          },
          {
            "ref": "electronics/optoelectronics/led-photodiode",
            "title": "Світлодіод"
          },
          {
            "ref": "electronics/components/zener-schottky",
            "title": "Діоди Зенера"
          },
          {
            "ref": "electronics/components/flyback-protection",
            "title": "Захист flyback"
          },
          {
            "ref": "electronics/optoelectronics/optocoupler-2",
            "title": "Оптопара"
          }
        ]
      },
      {
        "title": "Біполярний транзистор (BJT)",
        "steps": [
          {
            "ref": "electronics/analog/transistor-idea",
            "title": "Транзистор"
          },
          {
            "ref": "electronics/microelectronics/bjt-structure",
            "title": "Будова BJT"
          },
          {
            "ref": "electronics/analog/bjt-operation",
            "title": "Робота BJT"
          },
          {
            "ref": "electronics/analog/bjt-gain",
            "title": "Підсилення β"
          },
          {
            "ref": "electronics/analog/bjt-regions",
            "title": "Режими BJT"
          },
          {
            "ref": "electronics/analog/bjt-switch",
            "title": "BJT-ключ"
          },
          {
            "ref": "electronics/analog/bjt-amplifier",
            "title": "BJT-підсилювач"
          },
          {
            "ref": "electronics/analog/bjt-load-driving",
            "title": "BJT: навантаження"
          },
          {
            "ref": "electronics/electromechanics/relay-driver",
            "title": "Реле і драйвер"
          }
        ]
      },
      {
        "title": "Польовий транзистор (MOSFET)",
        "steps": [
          {
            "ref": "electronics/analog/field-control",
            "title": "Керування полем"
          },
          {
            "ref": "electronics/microelectronics/mosfet-structure",
            "title": "Будова MOSFET"
          },
          {
            "ref": "electronics/microelectronics/mosfet-threshold",
            "title": "Поріг MOSFET"
          },
          {
            "ref": "electronics/microelectronics/nmos-pmos",
            "title": "NMOS/PMOS"
          },
          {
            "ref": "electronics/components/rds-on",
            "title": "Опір Rds(on)"
          },
          {
            "ref": "electronics/power-electronics/mosfet-power-switch",
            "title": "Силовий ключ"
          },
          {
            "ref": "electronics/power-electronics/gate-capacitance",
            "title": "Ємність затвора"
          },
          {
            "ref": "electronics/analog/bjt-vs-mosfet",
            "title": "BJT проти MOSFET"
          },
          {
            "ref": "electronics/microelectronics/cmos",
            "title": "CMOS"
          },
          {
            "ref": "electronics/power-electronics/h-bridge",
            "title": "H-міст"
          },
          {
            "ref": "electronics/power-electronics/high-side-switch",
            "title": "Верхній ключ"
          }
        ]
      },
      {
        "title": "Операційний підсилювач і компаратор",
        "steps": [
          {
            "ref": "electronics/analog/ideal-opamp",
            "title": "Ідеальний ОП"
          },
          {
            "ref": "electronics/analog/negative-feedback",
            "title": "Від'ємний ЗЗ"
          },
          {
            "ref": "electronics/analog/virtual-short",
            "title": "Віртуальне коротке"
          },
          {
            "ref": "electronics/analog/inverting-noninverting",
            "title": "Інвертуючий підсилювач"
          },
          {
            "ref": "electronics/analog/voltage-follower",
            "title": "Повторювач"
          },
          {
            "ref": "electronics/analog/summing-difference-amp",
            "title": "Суматор"
          },
          {
            "ref": "electronics/analog/comparator-2",
            "title": "Компаратор"
          },
          {
            "ref": "electronics/analog/schmitt-trigger",
            "title": "Тригер Шмітта"
          },
          {
            "ref": "electronics/analog/real-opamp-limits",
            "title": "Реальний ОП"
          },
          {
            "ref": "electronics/analog/differential-pair",
            "title": "Диференційна пара"
          },
          {
            "ref": "electronics/power-electronics/ldo-internals",
            "title": "LDO зсередини"
          }
        ]
      },
      {
        "title": "Як читати даташит",
        "steps": [
          {
            "ref": "electronics/components/datasheet-structure",
            "title": "Структура даташита"
          },
          {
            "ref": "electronics/components/abs-max-ratings",
            "title": "Граничні режими"
          },
          {
            "ref": "electronics/metrology/min-typ-max",
            "title": "Min/typ/max"
          },
          {
            "ref": "electronics/components/datasheet-graphs",
            "title": "Графіки даташита"
          },
          {
            "ref": "electronics/components/packages-pinout",
            "title": "Корпуси й розпіновка"
          },
          {
            "ref": "electronics/components/datasheet-fine-print",
            "title": "Дрібний шрифт"
          },
          {
            "ref": "electronics/components/datasheet-practice",
            "title": "Практикум даташитів"
          }
        ]
      },
      {
        "title": "Резонатори й опорні частоти",
        "steps": [
          {
            "ref": "electronics/analog/reference-frequency",
            "title": "Опорна частота"
          },
          {
            "ref": "physics/condensed-matter-physics/piezoelectric-effect",
            "title": "П'єзоефект"
          },
          {
            "ref": "electronics/components/quartz-resonator",
            "title": "Кварцовий резонатор"
          },
          {
            "ref": "electronics/components/quartz-rlc-model",
            "title": "RLC-модель кварцу"
          },
          {
            "ref": "electronics/analog/pierce-oscillator",
            "title": "Генератор П'єрса"
          },
          {
            "ref": "electronics/components/frequency-accuracy-ppm",
            "title": "Точність ppm"
          },
          {
            "ref": "electronics/components/watch-crystal-rtc",
            "title": "Годинниковий кварц"
          },
          {
            "ref": "electronics/components/ceramic-mems-resonators",
            "title": "Керамічні резонатори"
          },
          {
            "ref": "electronics/components/tcxo-ocxo",
            "title": "TCXO та OCXO"
          }
        ]
      },
      {
        "title": "Силова комутація змінного струму",
        "steps": [
          {
            "ref": "electronics/power-electronics/ac-switch-need",
            "title": "Ключі для мережі"
          },
          {
            "ref": "electronics/power-electronics/thyristor-scr",
            "title": "Тиристор"
          },
          {
            "ref": "electronics/power-electronics/triac",
            "title": "Симістор"
          },
          {
            "ref": "electronics/power-electronics/phase-control-dimmer",
            "title": "Фазове керування"
          },
          {
            "ref": "electronics/power-electronics/zero-cross-switching",
            "title": "Перехід через нуль"
          },
          {
            "ref": "electronics/power-electronics/solid-state-relay",
            "title": "Твердотільне реле"
          },
          {
            "ref": "electronics/power-electronics/igbt",
            "title": "IGBT"
          },
          {
            "ref": "electronics/power-electronics/snubbers-dvdt",
            "title": "Снабери"
          },
          {
            "ref": "electronics/power-electronics/mains-safety",
            "title": "Безпека з мережею"
          }
        ]
      },
      {
        "title": "Легендарні аналогові ІМС",
        "steps": [
          {
            "ref": "electronics/analog/legendary-ics",
            "title": "Легендарні ІМС"
          },
          {
            "ref": "electronics/analog/555-internals",
            "title": "Таймер 555"
          },
          {
            "ref": "electronics/analog/555-astable",
            "title": "555 астабільний"
          },
          {
            "ref": "electronics/analog/555-monostable",
            "title": "555 моностабільний"
          },
          {
            "ref": "electronics/analog/voltage-reference",
            "title": "Опорна напруга"
          },
          {
            "ref": "electronics/analog/analog-switches-mux",
            "title": "Аналогові ключі"
          },
          {
            "ref": "electronics/analog/instrumentation-amp-2",
            "title": "Інструментальний підсилювач"
          }
        ]
      }
    ]
  },
  {
    "n": 3,
    "slug": "block-3-digital-processor",
    "title": "Цифрова електроніка й процесор",
    "chapters": [
      {
        "title": "Логічні рівні: від аналога до цифри",
        "steps": [
          {
            "ref": "electronics/digital/why-digital",
            "title": "Навіщо цифра"
          },
          {
            "ref": "electronics/digital/logic-levels-as-ranges",
            "title": "Рівні «0» і «1»"
          },
          {
            "ref": "electronics/digital/noise-margin",
            "title": "Запас завадостійкості"
          },
          {
            "ref": "electronics/digital/logic-families",
            "title": "Логічні сімейства"
          },
          {
            "ref": "electronics/digital/edges-rise-time",
            "title": "Фронти й час наростання"
          },
          {
            "ref": "electronics/digital/threshold-schmitt",
            "title": "Поріг і Шмітт"
          }
        ]
      },
      {
        "title": "Логічні вентилі й комбінаційні схеми",
        "steps": [
          {
            "ref": "math/logic-foundations/boolean-algebra",
            "title": "Булева алгебра"
          },
          {
            "ref": "electronics/digital/basic-gates",
            "title": "Базові вентилі"
          },
          {
            "ref": "electronics/digital/nand-nor",
            "title": "NAND і NOR"
          },
          {
            "ref": "electronics/digital/xor-comparison",
            "title": "XOR"
          },
          {
            "ref": "electronics/digital/cmos-gate",
            "title": "CMOS-вентиль"
          },
          {
            "ref": "electronics/digital/combinational-circuits",
            "title": "Комбінаційні схеми"
          },
          {
            "ref": "electronics/digital/gates-to-functions",
            "title": "Складні функції"
          }
        ]
      },
      {
        "title": "Тригери, регістри й тактування",
        "steps": [
          {
            "ref": "electronics/digital/state-memory",
            "title": "Пам'ять стану"
          },
          {
            "ref": "electronics/digital/sr-latch",
            "title": "SR-засувка"
          },
          {
            "ref": "electronics/digital/d-flip-flop",
            "title": "D-тригер"
          },
          {
            "ref": "electronics/digital/edge-vs-level",
            "title": "Фронт і рівень"
          },
          {
            "ref": "electronics/digital/register",
            "title": "Регістр"
          },
          {
            "ref": "electronics/digital/clock-signal",
            "title": "Тактовий сигнал"
          },
          {
            "ref": "electronics/digital/counters",
            "title": "Лічильники"
          },
          {
            "ref": "electronics/digital/metastability-timing",
            "title": "Метастабільність"
          },
          {
            "ref": "electronics/digital/finite-state-machines",
            "title": "Скінченні автомати"
          }
        ]
      },
      {
        "title": "Представлення чисел",
        "steps": [
          {
            "ref": "math/number-theory/why-binary",
            "title": "Чому двійкова"
          },
          {
            "ref": "math/number-theory/positional-systems",
            "title": "Позиційні системи"
          },
          {
            "ref": "math/number-theory/twos-complement",
            "title": "Доповняльний код"
          },
          {
            "ref": "programming/computer-architecture/overflow-wraparound",
            "title": "Переповнення"
          },
          {
            "ref": "programming/computer-architecture/fixed-point",
            "title": "Фіксована кома"
          },
          {
            "ref": "programming/computer-architecture/floating-point",
            "title": "Плаваюча кома"
          },
          {
            "ref": "programming/computer-architecture/bits-bytes-endianness",
            "title": "Біти й порядок байтів"
          },
          {
            "ref": "programming/computer-architecture/ascii-utf8",
            "title": "ASCII і UTF-8"
          }
        ]
      },
      {
        "title": "Архітектура процесора",
        "steps": [
          {
            "ref": "programming/computer-architecture/what-is-processor",
            "title": "Що таке процесор"
          },
          {
            "ref": "programming/computer-architecture/processor-parts",
            "title": "Складові процесора"
          },
          {
            "ref": "programming/computer-architecture/fetch-decode-execute",
            "title": "Цикл виконання"
          },
          {
            "ref": "programming/computer-architecture/isa",
            "title": "Набір інструкцій"
          },
          {
            "ref": "programming/computer-architecture/clock-frequency",
            "title": "Частота процесора"
          },
          {
            "ref": "programming/computer-architecture/pipeline",
            "title": "Конвеєр"
          },
          {
            "ref": "programming/computer-architecture/von-neumann-harvard",
            "title": "Фон Нейман і Гарвард"
          },
          {
            "ref": "programming/computer-architecture/risc-cisc",
            "title": "RISC і CISC"
          },
          {
            "ref": "programming/computer-architecture/cache",
            "title": "Кеш"
          }
        ]
      },
      {
        "title": "Пам'ять, адресація, стек і купа",
        "steps": [
          {
            "ref": "programming/systems/memory-as-array",
            "title": "Пам'ять як масив"
          },
          {
            "ref": "programming/systems/memory-map",
            "title": "Карта пам'яті"
          },
          {
            "ref": "programming/systems/flash-vs-ram",
            "title": "Flash і RAM"
          },
          {
            "ref": "programming/systems/addresses-pointers",
            "title": "Адреси й покажчики"
          },
          {
            "ref": "programming/systems/stack-lifo",
            "title": "Стек"
          },
          {
            "ref": "programming/systems/heap-dynamic-memory",
            "title": "Купа"
          },
          {
            "ref": "programming/systems/stack-overflow",
            "title": "Переповнення стека"
          },
          {
            "ref": "physics/condensed-matter-physics/memory-cell-physics",
            "title": "Фізика комірок"
          }
        ]
      },
      {
        "title": "Програмована логіка: ПЛІС/FPGA",
        "steps": [
          {
            "ref": "electronics/digital/programmable-logic",
            "title": "Програмована логіка"
          },
          {
            "ref": "electronics/digital/pal-to-fpga",
            "title": "Від PAL до FPGA"
          },
          {
            "ref": "electronics/digital/lut",
            "title": "LUT"
          },
          {
            "ref": "electronics/digital/inside-fpga",
            "title": "Усередині FPGA"
          },
          {
            "ref": "electronics/digital/hdl",
            "title": "HDL"
          },
          {
            "ref": "electronics/digital/fpga-flow",
            "title": "Потік розробки"
          },
          {
            "ref": "electronics/digital/fpga-timing",
            "title": "Таймінг FPGA"
          },
          {
            "ref": "electronics/digital/fpga-vs-mcu",
            "title": "FPGA чи МК"
          },
          {
            "ref": "electronics/digital/soft-core",
            "title": "М'яке ядро"
          }
        ]
      },
      {
        "title": "Зовнішня пам'ять",
        "steps": [
          {
            "ref": "electronics/digital/when-memory-runs-out",
            "title": "Коли пам'яті мало"
          },
          {
            "ref": "electronics/microelectronics/dram-cell",
            "title": "DRAM"
          },
          {
            "ref": "electronics/digital/sdram-ddr",
            "title": "SDRAM і DDR"
          },
          {
            "ref": "electronics/digital/memory-controller",
            "title": "Контролер пам'яті"
          },
          {
            "ref": "electronics/microelectronics/nor-vs-nand",
            "title": "NOR і NAND"
          },
          {
            "ref": "electronics/digital/sd-card",
            "title": "SD-картка"
          },
          {
            "ref": "electronics/digital/emmc-ssd",
            "title": "eMMC і SSD"
          },
          {
            "ref": "electronics/microelectronics/eeprom-fram",
            "title": "EEPROM і FRAM"
          },
          {
            "ref": "electronics/digital/choosing-memory",
            "title": "Вибір пам'яті"
          }
        ]
      },
      {
        "title": "Коди виявлення й корекції помилок",
        "steps": [
          {
            "ref": "algorithms/data-structures/bit-flips",
            "title": "Перевернуті біти"
          },
          {
            "ref": "communications/coding-theory/parity-bit",
            "title": "Біт парності"
          },
          {
            "ref": "communications/coding-theory/checksums",
            "title": "Контрольні суми"
          },
          {
            "ref": "communications/coding-theory/crc",
            "title": "CRC"
          },
          {
            "ref": "communications/coding-theory/hamming-distance",
            "title": "Відстань Геммінга"
          },
          {
            "ref": "communications/coding-theory/hamming-code",
            "title": "Код Геммінга"
          },
          {
            "ref": "communications/coding-theory/ecc-ram-flash",
            "title": "ECC у пам'яті"
          },
          {
            "ref": "communications/coding-theory/reed-solomon",
            "title": "Рід–Соломон"
          },
          {
            "ref": "communications/coding-theory/data-reliability",
            "title": "Надійність даних"
          }
        ]
      },
      {
        "title": "Як народжується чіп: від піску до корпуса",
        "steps": [
          {
            "ref": "electronics/microelectronics/silicon-monocrystal",
            "title": "Кремній і монокристал"
          },
          {
            "ref": "electronics/microelectronics/photolithography",
            "title": "Фотолітографія"
          },
          {
            "ref": "electronics/microelectronics/doping-etching-metal",
            "title": "Шар за шаром"
          },
          {
            "ref": "electronics/microelectronics/process-node",
            "title": "Техпроцес"
          },
          {
            "ref": "electronics/microelectronics/yield",
            "title": "Yield"
          },
          {
            "ref": "electronics/microelectronics/testing-binning",
            "title": "Тестування й binning"
          },
          {
            "ref": "electronics/pcb/packaging",
            "title": "Корпусування"
          },
          {
            "ref": "electronics/microelectronics/fabs-fabless",
            "title": "Фаби й fabless"
          }
        ]
      }
    ]
  },
  {
    "n": 4,
    "slug": "block-4-mcu-esp32",
    "title": "Мікроконтролер і прошивка: ESP32",
    "chapters": [
      {
        "title": "Анатомія мікроконтролера й архітектура ESP32",
        "steps": [
          {
            "ref": "programming/embedded-systems/microcontroller",
            "title": "Мікроконтролер"
          },
          {
            "ref": "programming/computer-architecture/mcu-blocks",
            "title": "Складові МК"
          },
          {
            "ref": "programming/embedded-systems/memory-mapped-io",
            "title": "Memory-mapped IO"
          },
          {
            "ref": "programming/embedded-systems/clock-power",
            "title": "Тактування й живлення"
          },
          {
            "ref": "programming/embedded-systems/esp32-architecture",
            "title": "Архітектура ESP32"
          },
          {
            "ref": "programming/embedded-systems/esp32-vs-8bit",
            "title": "ESP32 проти 8-біт"
          },
          {
            "ref": "programming/embedded-systems/esp32-family",
            "title": "Сімейство ESP32"
          },
          {
            "ref": "programming/embedded-systems/reset-causes",
            "title": "Причини reset"
          }
        ]
      },
      {
        "title": "Тулчейн: як код стає прошивкою",
        "steps": [
          {
            "ref": "programming/languages/compilation",
            "title": "Компіляція"
          },
          {
            "ref": "programming/languages/compiler-stages",
            "title": "Стадії компілятора"
          },
          {
            "ref": "programming/languages/linking",
            "title": "Лінкування"
          },
          {
            "ref": "programming/systems/firmware-image",
            "title": "Образ прошивки"
          },
          {
            "ref": "programming/embedded-systems/flashing",
            "title": "Прошивка у Flash"
          },
          {
            "ref": "programming/embedded-systems/bootloader",
            "title": "Bootloader"
          },
          {
            "ref": "programming/embedded-systems/baremetal-vs-framework",
            "title": "Голе залізо vs фреймворк"
          },
          {
            "ref": "programming/embedded-systems/jtag-swd-tools",
            "title": "Serial, JTAG/SWD"
          },
          {
            "ref": "programming/software-engineering/firmware-testing",
            "title": "Тестування прошивки"
          },
          {
            "ref": "programming/software-engineering/static-analysis",
            "title": "Статичний аналіз"
          },
          {
            "ref": "programming/systems/c-runtime",
            "title": "C-рантайм"
          }
        ]
      },
      {
        "title": "Постійні дані: Flash-розділи, NVS і файлові системи",
        "steps": [
          {
            "ref": "programming/embedded-systems/why-persist",
            "title": "Навіщо зберігати"
          },
          {
            "ref": "programming/embedded-systems/flash-internals",
            "title": "Flash зсередини"
          },
          {
            "ref": "programming/embedded-systems/wear-leveling",
            "title": "Wear leveling"
          },
          {
            "ref": "programming/embedded-systems/partition-table",
            "title": "Таблиця розділів"
          },
          {
            "ref": "programming/embedded-systems/nvs",
            "title": "NVS"
          },
          {
            "ref": "programming/systems/flash-filesystems",
            "title": "Файлові системи Flash"
          },
          {
            "ref": "programming/embedded-systems/write-integrity",
            "title": "Цілісність запису"
          },
          {
            "ref": "programming/embedded-systems/ota-slots",
            "title": "OTA-слоти"
          },
          {
            "ref": "programming/security/secure-boot",
            "title": "Secure boot"
          }
        ]
      },
      {
        "title": "GPIO глибоко",
        "steps": [
          {
            "ref": "electronics/digital/push-pull-output",
            "title": "Push-pull вихід"
          },
          {
            "ref": "electronics/digital/open-drain",
            "title": "Open-drain"
          },
          {
            "ref": "electronics/digital/logic-thresholds",
            "title": "Логічні пороги"
          },
          {
            "ref": "electronics/digital/floating-pullups",
            "title": "Підтяжки"
          },
          {
            "ref": "electronics/digital/contact-debounce",
            "title": "Дребезг контактів"
          },
          {
            "ref": "electronics/digital/pin-drive-limits",
            "title": "Навантажувальна здатність"
          },
          {
            "ref": "programming/embedded-systems/gpio-registers",
            "title": "GPIO-регістри"
          },
          {
            "ref": "programming/embedded-systems/module-model",
            "title": "Модель модуля"
          }
        ]
      },
      {
        "title": "Переривання",
        "steps": [
          {
            "ref": "programming/embedded-systems/interrupts",
            "title": "Переривання"
          },
          {
            "ref": "programming/computer-architecture/interrupt-vector",
            "title": "Контролер і вектор"
          },
          {
            "ref": "programming/embedded-systems/isr",
            "title": "ISR"
          },
          {
            "ref": "programming/embedded-systems/interrupt-priorities",
            "title": "Пріоритети переривань"
          },
          {
            "ref": "programming/languages/volatile",
            "title": "volatile"
          },
          {
            "ref": "programming/systems/atomicity-races",
            "title": "Атомарність і гонки"
          },
          {
            "ref": "programming/embedded-systems/polling-vs-interrupts",
            "title": "Polling vs переривання"
          }
        ]
      },
      {
        "title": "Таймери й керування часом",
        "steps": [
          {
            "ref": "programming/embedded-systems/timer-counter",
            "title": "Таймер-лічильник"
          },
          {
            "ref": "programming/embedded-systems/timer-overflow",
            "title": "Період і переповнення"
          },
          {
            "ref": "programming/embedded-systems/capture-compare",
            "title": "Захоплення й порівняння"
          },
          {
            "ref": "programming/embedded-systems/millis-micros",
            "title": "Точний час"
          },
          {
            "ref": "programming/embedded-systems/nonblocking-time",
            "title": "Неблокуючий час"
          },
          {
            "ref": "programming/embedded-systems/periodic-scheduling",
            "title": "Періодичні події"
          },
          {
            "ref": "programming/embedded-systems/watchdog",
            "title": "Watchdog"
          },
          {
            "ref": "programming/embedded-systems/rtc",
            "title": "RTC"
          }
        ]
      },
      {
        "title": "PWM і ЦАП",
        "steps": [
          {
            "ref": "programming/embedded-systems/pwm",
            "title": "ШІМ"
          },
          {
            "ref": "programming/embedded-systems/hardware-pwm",
            "title": "Апаратний PWM"
          },
          {
            "ref": "programming/embedded-systems/pwm-resolution",
            "title": "Шпаруватість і роздільність"
          },
          {
            "ref": "electronics/analog/rc-filter",
            "title": "RC-фільтр"
          },
          {
            "ref": "electronics/power-electronics/pwm-power-control",
            "title": "Керування потужністю"
          },
          {
            "ref": "electronics/digital/dac",
            "title": "ЦАП"
          },
          {
            "ref": "electronics/optoelectronics/addressable-leds",
            "title": "Адресні світлодіоди"
          }
        ]
      },
      {
        "title": "Аналого-цифрове перетворення (АЦП)",
        "steps": [
          {
            "ref": "electronics/digital/adc",
            "title": "АЦП"
          },
          {
            "ref": "electronics/digital/sampling-quantization",
            "title": "Дискретизація й квантування"
          },
          {
            "ref": "electronics/digital/adc-resolution",
            "title": "Роздільність АЦП"
          },
          {
            "ref": "electronics/metrology/voltage-reference",
            "title": "Опорна напруга"
          },
          {
            "ref": "communications/signal-processing/nyquist-aliasing",
            "title": "Найквіст і аліасинг"
          },
          {
            "ref": "electronics/metrology/adc-errors",
            "title": "Похибки АЦП"
          },
          {
            "ref": "communications/signal-processing/signal-acquisition",
            "title": "Зчитування сигналу"
          },
          {
            "ref": "electronics/digital/adc-types",
            "title": "Типи АЦП"
          }
        ]
      },
      {
        "title": "DMA: дані без участі ядра",
        "steps": [
          {
            "ref": "programming/computer-architecture/dma-problem",
            "title": "Проблема потоку даних"
          },
          {
            "ref": "programming/computer-architecture/dma-controller",
            "title": "DMA-контролер"
          },
          {
            "ref": "programming/computer-architecture/dma-channels",
            "title": "Канали й дескриптори"
          },
          {
            "ref": "programming/embedded-systems/double-buffering",
            "title": "Подвійна буферизація"
          },
          {
            "ref": "programming/embedded-systems/dma-adc",
            "title": "DMA + АЦП"
          },
          {
            "ref": "programming/embedded-systems/dma-spi-i2s",
            "title": "DMA + SPI/I2S"
          },
          {
            "ref": "programming/systems/dma-cache-races",
            "title": "Пастки DMA"
          }
        ]
      },
      {
        "title": "Модель виконання й RTOS",
        "steps": [
          {
            "ref": "programming/embedded-systems/super-loop",
            "title": "Super-loop"
          },
          {
            "ref": "programming/embedded-systems/super-loop-limits",
            "title": "Межі super-loop"
          },
          {
            "ref": "programming/systems/tasks",
            "title": "Задачі"
          },
          {
            "ref": "programming/systems/scheduler",
            "title": "Планувальник"
          },
          {
            "ref": "programming/embedded-systems/freertos",
            "title": "FreeRTOS"
          },
          {
            "ref": "programming/systems/task-ipc",
            "title": "Черги й семафори"
          },
          {
            "ref": "programming/systems/task-stacks",
            "title": "Стеки задач"
          },
          {
            "ref": "programming/embedded-systems/realtime-determinism",
            "title": "Детермінованість"
          },
          {
            "ref": "programming/software-engineering/profiling",
            "title": "Профілювання"
          }
        ]
      },
      {
        "title": "Пейзаж мікроконтролерів",
        "steps": [
          {
            "ref": "programming/embedded-systems/mcu-selection",
            "title": "Вибір МК"
          },
          {
            "ref": "programming/embedded-systems/avr",
            "title": "AVR-клас"
          },
          {
            "ref": "programming/embedded-systems/cortex-m",
            "title": "ARM Cortex-M"
          },
          {
            "ref": "programming/embedded-systems/stm32",
            "title": "STM32-клас"
          },
          {
            "ref": "programming/embedded-systems/rp2040-pio",
            "title": "RP2040 і PIO"
          },
          {
            "ref": "programming/embedded-systems/nrf-radio-mcu",
            "title": "nRF-клас"
          },
          {
            "ref": "programming/embedded-systems/mcu-ecosystem",
            "title": "Екосистема МК"
          },
          {
            "ref": "programming/embedded-systems/mcu-checklist",
            "title": "Чеклист вибору МК"
          }
        ]
      },
      {
        "title": "USB на мікроконтролері",
        "steps": [
          {
            "ref": "programming/peripherals/usb-overview",
            "title": "USB огляд"
          },
          {
            "ref": "programming/peripherals/usb-physical",
            "title": "USB фізично"
          },
          {
            "ref": "programming/peripherals/usb-enumeration",
            "title": "Енумерація USB"
          },
          {
            "ref": "programming/peripherals/usb-endpoints",
            "title": "Кінцеві точки USB"
          },
          {
            "ref": "programming/peripherals/usb-device-classes",
            "title": "Класи USB"
          },
          {
            "ref": "programming/peripherals/esp32-usb",
            "title": "USB в ESP32"
          },
          {
            "ref": "programming/peripherals/usb-power",
            "title": "Живлення з USB"
          },
          {
            "ref": "programming/peripherals/usb-host",
            "title": "МК як USB-host"
          }
        ]
      },
      {
        "title": "Енергоощадність глибоко",
        "steps": [
          {
            "ref": "programming/embedded-systems/battery-budget",
            "title": "Бюджет батареї"
          },
          {
            "ref": "programming/embedded-systems/current-paths",
            "title": "Куди тече струм"
          },
          {
            "ref": "programming/embedded-systems/sleep-modes",
            "title": "Режими сну"
          },
          {
            "ref": "programming/embedded-systems/wakeup-sources",
            "title": "Джерела пробудження"
          },
          {
            "ref": "programming/embedded-systems/ulp-coprocessor",
            "title": "ULP-співпроцесор"
          },
          {
            "ref": "programming/embedded-systems/duty-cycle-current",
            "title": "Цикл і середній струм"
          },
          {
            "ref": "electronics/metrology/measure-consumption",
            "title": "Виміряти споживання"
          },
          {
            "ref": "electronics/power-electronics/board-consumption",
            "title": "Споживання плати"
          },
          {
            "ref": "programming/embedded-systems/rtc-memory",
            "title": "RTC-память"
          }
        ]
      },
      {
        "title": "Налагодження глибоко: JTAG/SWD, GDB і посмертний аналіз",
        "steps": [
          {
            "ref": "programming/embedded-systems/why-debugger",
            "title": "Навіщо відлагоджувач"
          },
          {
            "ref": "programming/embedded-systems/swd-jtag-internals",
            "title": "SWD і JTAG зсередини"
          },
          {
            "ref": "programming/embedded-systems/breakpoints-watchpoints",
            "title": "Брейкпоінти й вотчпоінти"
          },
          {
            "ref": "programming/embedded-systems/openocd-gdb",
            "title": "OpenOCD і GDB"
          },
          {
            "ref": "programming/embedded-systems/step-debugging",
            "title": "Кроком по коду"
          },
          {
            "ref": "programming/embedded-systems/hardfault",
            "title": "Розбір HardFault"
          },
          {
            "ref": "programming/embedded-systems/core-dump",
            "title": "Посмертний аналіз"
          }
        ]
      },
      {
        "title": "Відмовостійка прошивка: помилки, паніка, відновлення",
        "steps": [
          {
            "ref": "programming/software-engineering/error-handling",
            "title": "Жодна помилка не мовчить"
          },
          {
            "ref": "programming/software-engineering/assert-panic",
            "title": "Assert і паніка"
          },
          {
            "ref": "programming/software-engineering/defensive-programming",
            "title": "Захисне програмування"
          },
          {
            "ref": "programming/embedded-systems/safe-mode",
            "title": "Безпечний стан"
          },
          {
            "ref": "programming/embedded-systems/reboot-strategy",
            "title": "Перезавантаження"
          },
          {
            "ref": "programming/embedded-systems/reboot-counter",
            "title": "Лічильник перезавантажень"
          },
          {
            "ref": "programming/embedded-systems/brownout",
            "title": "Brown-out"
          },
          {
            "ref": "programming/embedded-systems/graceful-degradation",
            "title": "Деградація з гідністю"
          }
        ]
      }
    ]
  },
  {
    "n": 5,
    "slug": "block-5-sensors-control",
    "title": "Давачі, сигнали й керування",
    "chapters": [
      {
        "title": "Фізика давачів",
        "steps": [
          {
            "ref": "electronics/sensors/what-is-a-sensor",
            "title": "Що таке давач"
          },
          {
            "ref": "electronics/sensors/transducer-classes",
            "title": "Класи перетворювачів"
          },
          {
            "ref": "electronics/sensors/piezo-optical-semiconductor",
            "title": "П'єзо й оптичні"
          },
          {
            "ref": "electronics/sensors/sensor-characteristics",
            "title": "Характеристики давача"
          },
          {
            "ref": "electronics/sensors/drift-hysteresis-noise",
            "title": "Дрейф і гістерезис"
          },
          {
            "ref": "electronics/metrology/calibration",
            "title": "Калібрування"
          },
          {
            "ref": "electronics/sensors/sensor-input-matching",
            "title": "Узгодження давача"
          },
          {
            "ref": "electronics/metrology/current-voltage-measurement",
            "title": "Вимірювання струму"
          },
          {
            "ref": "electronics/sensors/strain-gauges",
            "title": "Тензодавачі"
          },
          {
            "ref": "electronics/electromechanics/microphone-speaker",
            "title": "Мікрофон і динамік"
          }
        ]
      },
      {
        "title": "Вимірювання відстані й оточення",
        "steps": [
          {
            "ref": "electronics/sensors/contactless-distance",
            "title": "Безконтактна відстань"
          },
          {
            "ref": "electronics/sensors/tof-ultrasonic",
            "title": "ToF звук"
          },
          {
            "ref": "electronics/sensors/tof-laser",
            "title": "ToF лазер"
          },
          {
            "ref": "electronics/sensors/triangulation",
            "title": "Тріангуляція"
          },
          {
            "ref": "electronics/sensors/reflection-absorption",
            "title": "Відбиття IR"
          },
          {
            "ref": "electronics/sensors/distance-errors",
            "title": "Похибки відстані"
          },
          {
            "ref": "electronics/sensors/environment-sensors",
            "title": "Давачі оточення"
          }
        ]
      },
      {
        "title": "Давачі обертання й положення: енкодери",
        "steps": [
          {
            "ref": "electronics/sensors/angle-rotation-sensing",
            "title": "Вимір кута"
          },
          {
            "ref": "electronics/sensors/potentiometer-angle-sensor",
            "title": "Потенціометр кута"
          },
          {
            "ref": "electronics/sensors/optical-incremental-encoder",
            "title": "Оптичний енкодер"
          },
          {
            "ref": "electronics/sensors/quadrature",
            "title": "Квадратура"
          },
          {
            "ref": "electronics/sensors/hall-magnetic-encoders",
            "title": "Холл-енкодери"
          },
          {
            "ref": "electronics/sensors/absolute-encoder-gray-code",
            "title": "Абсолютний енкодер"
          },
          {
            "ref": "algorithms/signal-robotics/odometry",
            "title": "Одометрія"
          }
        ]
      },
      {
        "title": "Цифрова фільтрація сигналів",
        "steps": [
          {
            "ref": "algorithms/signal-robotics/signal-noise",
            "title": "Шум у сигналі"
          },
          {
            "ref": "algorithms/signal-robotics/moving-average",
            "title": "Ковзне середнє"
          },
          {
            "ref": "algorithms/signal-robotics/median-filter",
            "title": "Медіанний фільтр"
          },
          {
            "ref": "algorithms/signal-robotics/ema",
            "title": "EMA"
          },
          {
            "ref": "algorithms/signal-robotics/smoothing-vs-lag",
            "title": "Згладжування й затримка"
          },
          {
            "ref": "algorithms/signal-robotics/choosing-a-filter",
            "title": "Вибір фільтра"
          }
        ]
      },
      {
        "title": "Спектр і перетворення Фур'є",
        "steps": [
          {
            "ref": "math/real-analysis/time-and-frequency",
            "title": "Час і частота"
          },
          {
            "ref": "math/real-analysis/fourier-idea",
            "title": "Ідея Фур'є"
          },
          {
            "ref": "math/real-analysis/spectrum",
            "title": "Спектр"
          },
          {
            "ref": "math/real-analysis/dft",
            "title": "ДПФ"
          },
          {
            "ref": "algorithms/signal-robotics/fft",
            "title": "ШПФ"
          },
          {
            "ref": "math/real-analysis/windowing-leakage",
            "title": "Вікно й витік"
          },
          {
            "ref": "math/real-analysis/why-frequency-domain",
            "title": "Навіщо частота"
          }
        ]
      },
      {
        "title": "Цифрові фільтри в мікроконтролері",
        "steps": [
          {
            "ref": "algorithms/signal-robotics/filter-as-spectrum-shaper",
            "title": "Формувач спектра"
          },
          {
            "ref": "algorithms/signal-robotics/fir-filter",
            "title": "КІХ-фільтр"
          },
          {
            "ref": "algorithms/signal-robotics/iir-filter",
            "title": "БІХ-фільтр"
          },
          {
            "ref": "algorithms/signal-robotics/band-filters",
            "title": "Смугові фільтри"
          },
          {
            "ref": "algorithms/signal-robotics/fixed-point-implementation",
            "title": "Реалізація fixed-point"
          },
          {
            "ref": "algorithms/signal-robotics/fir-vs-iir",
            "title": "КІХ проти БІХ"
          }
        ]
      },
      {
        "title": "Інерціальні давачі: MEMS",
        "steps": [
          {
            "ref": "electronics/sensors/mems",
            "title": "MEMS"
          },
          {
            "ref": "electronics/sensors/accelerometer",
            "title": "Акселерометр"
          },
          {
            "ref": "electronics/sensors/gyroscope",
            "title": "Гіроскоп"
          },
          {
            "ref": "electronics/sensors/magnetometer",
            "title": "Магнітометр"
          },
          {
            "ref": "electronics/sensors/imu-noise-bias-drift",
            "title": "Шум і дрейф IMU"
          },
          {
            "ref": "algorithms/signal-robotics/sensor-fusion",
            "title": "Фьюжн"
          },
          {
            "ref": "electronics/sensors/reading-imu-fifo",
            "title": "Читання IMU"
          },
          {
            "ref": "electronics/sensors/imu-vibration-isolation",
            "title": "Розв'язка IMU"
          },
          {
            "ref": "electronics/sensors/imu-calibration",
            "title": "Калібрування IMU"
          }
        ]
      },
      {
        "title": "Орієнтація й керування зі зворотним зв'язком (ПІД)",
        "steps": [
          {
            "ref": "math/geometry/euler-angles",
            "title": "Кути Ейлера"
          },
          {
            "ref": "math/geometry/quaternions",
            "title": "Кватерніони"
          },
          {
            "ref": "algorithms/signal-robotics/complementary-filter",
            "title": "Комплементарний фільтр"
          },
          {
            "ref": "algorithms/signal-robotics/kalman-filter",
            "title": "Фільтр Калмана"
          },
          {
            "ref": "math/optimization/open-vs-closed-loop",
            "title": "Зворотний зв'язок"
          },
          {
            "ref": "math/optimization/proportional-control",
            "title": "П-регулятор"
          },
          {
            "ref": "math/optimization/integral-control",
            "title": "І-складова"
          },
          {
            "ref": "math/optimization/derivative-control",
            "title": "Д-складова"
          },
          {
            "ref": "algorithms/signal-robotics/discrete-pid",
            "title": "Дискретний ПІД"
          },
          {
            "ref": "math/optimization/pid-tuning-cascade",
            "title": "Налаштування ПІД"
          },
          {
            "ref": "math/optimization/loop-stability",
            "title": "Запас стійкості"
          },
          {
            "ref": "math/optimization/step-response",
            "title": "Крокова відповідь"
          },
          {
            "ref": "math/optimization/feedforward",
            "title": "Феєдфорвард"
          }
        ]
      },
      {
        "title": "Виконавчі механізми: мотори й рух",
        "steps": [
          {
            "ref": "electronics/electromechanics/brushed-dc-motor",
            "title": "DC-мотор"
          },
          {
            "ref": "electronics/power-electronics/h-bridge-2",
            "title": "H-міст"
          },
          {
            "ref": "electronics/electromechanics/stepper-motor",
            "title": "Кроковий мотор"
          },
          {
            "ref": "electronics/electromechanics/hobby-servo",
            "title": "Серво"
          },
          {
            "ref": "electronics/electromechanics/solenoid-piezo-actuators",
            "title": "Соленоїд і п'єзо"
          },
          {
            "ref": "electronics/electromechanics/motor-current-stall-heat",
            "title": "Заклинювання й нагрів"
          },
          {
            "ref": "electronics/electromechanics/gears-transmission",
            "title": "Редуктори"
          },
          {
            "ref": "electronics/electromechanics/actuator-selection",
            "title": "Вибір актуатора"
          },
          {
            "ref": "algorithms/signal-robotics/motion-profiles",
            "title": "Профілі руху"
          }
        ]
      },
      {
        "title": "Давачі середовища глибше",
        "steps": [
          {
            "ref": "electronics/sensors/mox-gas-sensor",
            "title": "MOX-давач"
          },
          {
            "ref": "electronics/sensors/ndir-co2",
            "title": "NDIR CO2"
          },
          {
            "ref": "electronics/sensors/electrochemical-cell",
            "title": "Електрохімічна комірка"
          },
          {
            "ref": "electronics/sensors/dust-aerosol-sensor",
            "title": "Давач пилу"
          },
          {
            "ref": "electronics/sensors/uv-light-sensor",
            "title": "УФ-давач"
          },
          {
            "ref": "electronics/sensors/geiger-muller-counter",
            "title": "Лічильник Гейгера"
          },
          {
            "ref": "electronics/sensors/barometric-altimeter",
            "title": "Барометр-альтиметр"
          },
          {
            "ref": "electronics/sensors/cross-sensitivity-compensation",
            "title": "Перехресна чутливість"
          }
        ]
      },
      {
        "title": "Час і синхронізація вимірювань",
        "steps": [
          {
            "ref": "communications/synchronization/measurement-time",
            "title": "Час вимірювання"
          },
          {
            "ref": "communications/synchronization/timestamps",
            "title": "Мітки часу"
          },
          {
            "ref": "communications/synchronization/sampling-jitter",
            "title": "Джиттер вибірки"
          },
          {
            "ref": "communications/synchronization/synchronous-multi-sensor-read",
            "title": "Синхронне зчитування"
          },
          {
            "ref": "communications/synchronization/pps-pulse",
            "title": "PPS-імпульс"
          },
          {
            "ref": "communications/synchronization/clock-offset-drift",
            "title": "Дрейф годинників"
          },
          {
            "ref": "communications/synchronization/sensor-latency-compensation",
            "title": "Затримка давача"
          }
        ]
      }
    ]
  },
  {
    "n": 6,
    "slug": "block-6-comms-radio",
    "title": "Зв'язок: дротовий і радіо",
    "chapters": [
      {
        "title": "UART і протоколи поверх нього",
        "steps": [
          {
            "ref": "communications/buses/async-serial",
            "title": "Асинхронна передача"
          },
          {
            "ref": "communications/buses/uart-frame",
            "title": "Кадр UART"
          },
          {
            "ref": "communications/synchronization/baud-rate",
            "title": "Швидкість baud"
          },
          {
            "ref": "electronics/digital/ttl-rs232",
            "title": "TTL і RS-232"
          },
          {
            "ref": "communications/protocols/flow-control",
            "title": "Керування потоком"
          },
          {
            "ref": "communications/protocols/packet-design",
            "title": "Проєктування пакета"
          },
          {
            "ref": "programming/embedded-systems/stream-parser",
            "title": "Розбір потоку"
          }
        ]
      },
      {
        "title": "Шина I2C",
        "steps": [
          {
            "ref": "communications/buses/i2c-bus",
            "title": "Шина I2C"
          },
          {
            "ref": "electronics/digital/open-collector",
            "title": "Відкритий колектор"
          },
          {
            "ref": "communications/buses/i2c-addressing",
            "title": "Адресація I2C"
          },
          {
            "ref": "communications/buses/start-stop-ack",
            "title": "Старт, стоп, ACK"
          },
          {
            "ref": "communications/buses/i2c-transaction",
            "title": "Транзакція I2C"
          },
          {
            "ref": "communications/multiple-access/clock-stretch-arbitration",
            "title": "Розтягування й арбітраж"
          },
          {
            "ref": "communications/buses/register-map",
            "title": "Регістрова карта"
          }
        ]
      },
      {
        "title": "Шина SPI",
        "steps": [
          {
            "ref": "communications/buses/spi-bus",
            "title": "Шина SPI"
          },
          {
            "ref": "communications/buses/spi-lines",
            "title": "Лінії SPI"
          },
          {
            "ref": "communications/buses/cpol-cpha",
            "title": "Режими CPOL/CPHA"
          },
          {
            "ref": "communications/buses/chip-select",
            "title": "Вибір кристала"
          },
          {
            "ref": "communications/buses/spi-speed",
            "title": "Швидкість SPI"
          },
          {
            "ref": "communications/buses/spi-vs-i2c",
            "title": "SPI проти I2C"
          }
        ]
      },
      {
        "title": "Диференційні шини: RS-485 і CAN",
        "steps": [
          {
            "ref": "communications/buses/single-ended-line-limits",
            "title": "Межі односторонніх ліній"
          },
          {
            "ref": "communications/buses/differential-pair",
            "title": "Диференційна пара"
          },
          {
            "ref": "communications/buses/rs-485",
            "title": "RS-485"
          },
          {
            "ref": "communications/buses/can-arbitration",
            "title": "Арбітраж CAN"
          },
          {
            "ref": "communications/buses/can-frame-errors",
            "title": "Кадр CAN"
          },
          {
            "ref": "communications/buses/dronecan",
            "title": "DroneCAN"
          },
          {
            "ref": "communications/buses/usb-ethernet-differential",
            "title": "USB та Ethernet пари"
          }
        ]
      },
      {
        "title": "Бездротовий зв'язок на чіпі: Wi-Fi і Bluetooth",
        "steps": [
          {
            "ref": "communications/networks/on-chip-radio",
            "title": "Радіо на чіпі"
          },
          {
            "ref": "communications/networks/channel-band-packet",
            "title": "Канал і пакет"
          },
          {
            "ref": "communications/networks/wifi",
            "title": "Wi-Fi"
          },
          {
            "ref": "communications/protocols/tcp-vs-udp",
            "title": "TCP проти UDP"
          },
          {
            "ref": "communications/networks/bluetooth-spp",
            "title": "Bluetooth SPP"
          },
          {
            "ref": "communications/protocols/ble-gatt",
            "title": "BLE GATT"
          },
          {
            "ref": "communications/protocols/reliable-link",
            "title": "Надійний обмін"
          },
          {
            "ref": "communications/networks/esp-now",
            "title": "ESP-NOW"
          },
          {
            "ref": "programming/embedded-systems/ota-update",
            "title": "OTA-оновлення"
          },
          {
            "ref": "communications/protocols/mqtt",
            "title": "MQTT"
          },
          {
            "ref": "programming/networking/web-server-mcu",
            "title": "Веб-сервер на МК"
          },
          {
            "ref": "programming/embedded-systems/ble-gatt-practice",
            "title": "BLE-практика"
          }
        ]
      },
      {
        "title": "Радіо: фізика електромагнітних хвиль",
        "steps": [
          {
            "ref": "physics/electromagnetism/em-wave",
            "title": "Електромагнітна хвиля"
          },
          {
            "ref": "physics/electromagnetism/frequency-wavelength",
            "title": "Частота й довжина"
          },
          {
            "ref": "communications/propagation/propagation-polarization",
            "title": "Поширення й поляризація"
          },
          {
            "ref": "communications/propagation/frequency-bands",
            "title": "Діапазони частот"
          },
          {
            "ref": "communications/propagation/power-decibels",
            "title": "Потужність і децибели"
          },
          {
            "ref": "communications/propagation/free-space-loss",
            "title": "Загасання у просторі"
          },
          {
            "ref": "communications/photonics/optical-fiber",
            "title": "Оптоволокно"
          }
        ]
      },
      {
        "title": "Радіо: модуляція й бюджет лінії",
        "steps": [
          {
            "ref": "communications/modulation/why-modulation",
            "title": "Навіщо модуляція"
          },
          {
            "ref": "communications/modulation/am-fm",
            "title": "AM і FM"
          },
          {
            "ref": "communications/modulation/fsk-psk",
            "title": "FSK і PSK"
          },
          {
            "ref": "communications/information-theory/bandwidth-capacity",
            "title": "Смуга і межа Шеннона"
          },
          {
            "ref": "communications/modulation/spread-spectrum",
            "title": "Розширений спектр"
          },
          {
            "ref": "communications/propagation/link-budget",
            "title": "Бюджет лінії"
          },
          {
            "ref": "communications/propagation/multipath-fading",
            "title": "Багатопроменевість"
          },
          {
            "ref": "communications/modulation/lora",
            "title": "LoRa"
          },
          {
            "ref": "communications/radio-engineering/superheterodyne",
            "title": "Супергетеродин"
          }
        ]
      },
      {
        "title": "Антени й лінії передачі",
        "steps": [
          {
            "ref": "communications/antennas/antenna",
            "title": "Антена"
          },
          {
            "ref": "communications/antennas/resonance-dipole",
            "title": "Резонанс і диполь"
          },
          {
            "ref": "communications/antennas/antenna-gain",
            "title": "Підсилення антени"
          },
          {
            "ref": "communications/antennas/antenna-polarization",
            "title": "Поляризація антени"
          },
          {
            "ref": "communications/radio-engineering/transmission-lines",
            "title": "Лінії передачі"
          },
          {
            "ref": "communications/radio-engineering/vswr",
            "title": "Відбиття і КСХ"
          },
          {
            "ref": "electronics/radio/rf-board-reading",
            "title": "Читання ВЧ-плати"
          },
          {
            "ref": "communications/propagation/ism-bands",
            "title": "ISM-діапазони"
          }
        ]
      },
      {
        "title": "Радіозв'язок системи: керування, телеметрія, MAVLink",
        "steps": [
          {
            "ref": "communications/protocols/control-telemetry",
            "title": "Керування й телеметрія"
          },
          {
            "ref": "communications/protocols/rc-link",
            "title": "RC-лінк"
          },
          {
            "ref": "communications/protocols/telemetry-stream",
            "title": "Телеметрія"
          },
          {
            "ref": "communications/networks/latency-reliability",
            "title": "Затримка й надійність"
          },
          {
            "ref": "communications/protocols/mavlink-packet",
            "title": "Пакет MAVLink"
          },
          {
            "ref": "programming/embedded-systems/mavlink-commands",
            "title": "Команди MAVLink"
          },
          {
            "ref": "programming/networking/pymavlink",
            "title": "pymavlink"
          },
          {
            "ref": "communications/cryptographic-comm/mavlink-security",
            "title": "Безпека MAVLink"
          },
          {
            "ref": "communications/modulation/jamming-fhss",
            "title": "Лінк під глушінням"
          }
        ]
      },
      {
        "title": "Мережі: Ethernet, IP і як пакет знаходить дорогу",
        "steps": [
          {
            "ref": "communications/networks/ethernet-frame",
            "title": "Кадр Ethernet"
          },
          {
            "ref": "communications/networks/ethernet-link-phy",
            "title": "Фізика лінка"
          },
          {
            "ref": "communications/networks/mac-ip-arp",
            "title": "MAC, IP і ARP"
          },
          {
            "ref": "communications/networks/ip-routing",
            "title": "Маршрутизація"
          },
          {
            "ref": "communications/networks/dhcp-dns",
            "title": "DHCP і DNS"
          },
          {
            "ref": "communications/networks/nat",
            "title": "NAT"
          },
          {
            "ref": "programming/networking/sockets-tcp-udp",
            "title": "Сокети TCP/UDP"
          },
          {
            "ref": "communications/photonics/fiber-in-network",
            "title": "Оптоволокно в мережі"
          },
          {
            "ref": "programming/embedded-systems/ethernet-on-mcu",
            "title": "Ethernet на МК"
          }
        ]
      },
      {
        "title": "MAVLink у роботі: словник даних і керування",
        "steps": [
          {
            "ref": "communications/protocols/mavlink-message-dictionary",
            "title": "Словник MAVLink"
          },
          {
            "ref": "communications/protocols/coordinate-frames-units",
            "title": "Координати й одиниці"
          },
          {
            "ref": "communications/protocols/stream-rates",
            "title": "Частоти потоків"
          },
          {
            "ref": "communications/protocols/param-protocol",
            "title": "Протокол параметрів"
          },
          {
            "ref": "communications/protocols/mission-protocol",
            "title": "Протокол місій"
          },
          {
            "ref": "communications/protocols/mavlink-commands",
            "title": "Команди MAVLink"
          },
          {
            "ref": "communications/protocols/motion-control-setpoints",
            "title": "Керування рухом"
          },
          {
            "ref": "programming/networking/mavlink-stream-processing",
            "title": "Обробка потоку"
          },
          {
            "ref": "communications/protocols/mavlink-pitfalls",
            "title": "Граблі MAVLink"
          }
        ]
      },
      {
        "title": "Приєднання модулів: розпіновки, рівні, конектори, надійність",
        "steps": [
          {
            "ref": "electronics/pcb/datasheet-pinout",
            "title": "Розпіновка й даташит"
          },
          {
            "ref": "electronics/pcb/common-ground",
            "title": "Спільна земля"
          },
          {
            "ref": "electronics/digital/level-shifting",
            "title": "Зсув рівнів"
          },
          {
            "ref": "electronics/power-electronics/module-power-supply",
            "title": "Живлення модуля"
          },
          {
            "ref": "communications/buses/bus-resource-conflicts",
            "title": "Конфлікти шин"
          },
          {
            "ref": "electronics/pcb/cables-connectors",
            "title": "Кабелі й конектори"
          },
          {
            "ref": "electronics/pcb/esd-hot-plug",
            "title": "ESD і гаряче підключення"
          },
          {
            "ref": "electronics/metrology/first-power-up-check",
            "title": "Перша перевірка"
          },
          {
            "ref": "electronics/pcb/basic-soldering",
            "title": "Мінімальна пайка"
          },
          {
            "ref": "electronics/metrology/fault-finding",
            "title": "Пошук несправності"
          }
        ]
      }
    ]
  },
  {
    "n": 7,
    "slug": "block-7-systems",
    "title": "Системи: ArduPilot, відео, машинне бачення",
    "chapters": [
      {
        "title": "Архітектура автономної системи й політний контролер",
        "steps": [
          {
            "ref": "programming/embedded-systems/autonomous-system",
            "title": "Автономна система"
          },
          {
            "ref": "programming/embedded-systems/flight-controller",
            "title": "Політний контролер"
          },
          {
            "ref": "programming/embedded-systems/ardupilot-layers",
            "title": "Шари ArduPilot"
          },
          {
            "ref": "programming/embedded-systems/params-gcs",
            "title": "Параметри й GCS"
          },
          {
            "ref": "programming/embedded-systems/fc-vs-companion",
            "title": "Контролер vs комп'ютер"
          }
        ]
      },
      {
        "title": "Як літає мультиротор",
        "steps": [
          {
            "ref": "physics/mechanics/thrust-vs-weight",
            "title": "Тяга проти ваги"
          },
          {
            "ref": "physics/mechanics/reaction-torque",
            "title": "Реактивний момент"
          },
          {
            "ref": "algorithms/signal-robotics/roll-pitch-yaw-control",
            "title": "Керування roll/pitch/yaw"
          },
          {
            "ref": "algorithms/signal-robotics/motor-mixer",
            "title": "Мікшер"
          },
          {
            "ref": "algorithms/signal-robotics/instability-stabilization",
            "title": "Потреба стабілізації"
          },
          {
            "ref": "physics/mechanics/frame-configurations",
            "title": "Рами й конфігурації"
          },
          {
            "ref": "physics/mechanics/propeller-geometry",
            "title": "Гвинт"
          },
          {
            "ref": "algorithms/signal-robotics/stabilization-cascade",
            "title": "Каскад стабілізації"
          }
        ]
      },
      {
        "title": "Компоненти польотної системи",
        "steps": [
          {
            "ref": "electronics/sensors/onboard-sensors",
            "title": "Давачі апарата"
          },
          {
            "ref": "electronics/sensors/imu-barometer",
            "title": "IMU й барометр"
          },
          {
            "ref": "communications/propagation/gnss",
            "title": "GNSS"
          },
          {
            "ref": "electronics/electromechanics/bldc-motor",
            "title": "BLDC-мотор"
          },
          {
            "ref": "electronics/power-electronics/esc",
            "title": "ESC-регулятор"
          },
          {
            "ref": "electronics/electromechanics/servo-2",
            "title": "Серво"
          },
          {
            "ref": "programming/embedded-systems/redundancy",
            "title": "Надлишковість"
          }
        ]
      },
      {
        "title": "Живлення складних систем",
        "steps": [
          {
            "ref": "electronics/power-electronics/linear-vs-switching",
            "title": "Лінійний vs імпульсний"
          },
          {
            "ref": "electronics/power-electronics/switching-converter",
            "title": "Імпульсний перетворювач"
          },
          {
            "ref": "electronics/power-electronics/power-rails",
            "title": "Шини живлення"
          },
          {
            "ref": "electronics/power-electronics/batteries",
            "title": "Акумулятори"
          },
          {
            "ref": "electronics/power-electronics/c-rate",
            "title": "C-rate й опір"
          },
          {
            "ref": "electronics/power-electronics/cc-cv-bms",
            "title": "Заряд і BMS"
          },
          {
            "ref": "electronics/power-electronics/energy-budget",
            "title": "Бюджет енергії"
          }
        ]
      },
      {
        "title": "Оцінювання стану й сенсорний фьюжн",
        "steps": [
          {
            "ref": "algorithms/signal-robotics/sensor-insufficiency",
            "title": "Недостатність давача"
          },
          {
            "ref": "algorithms/signal-robotics/motion-model",
            "title": "Модель руху"
          },
          {
            "ref": "algorithms/signal-robotics/predict-vs-measure",
            "title": "Передбачення vs вимір"
          },
          {
            "ref": "algorithms/signal-robotics/kalman-ekf",
            "title": "Фільтр Калмана"
          },
          {
            "ref": "algorithms/signal-robotics/sensor-fusion-2",
            "title": "Сенсорний фьюжн"
          },
          {
            "ref": "algorithms/signal-robotics/latency-sync",
            "title": "Затримки й синхро"
          }
        ]
      },
      {
        "title": "Польотні режими, місії та failsafe",
        "steps": [
          {
            "ref": "programming/embedded-systems/manual-stabilized-modes",
            "title": "Ручні режими"
          },
          {
            "ref": "programming/embedded-systems/position-modes",
            "title": "Режими з позицією"
          },
          {
            "ref": "programming/embedded-systems/arming-checks",
            "title": "Arming-перевірки"
          },
          {
            "ref": "algorithms/signal-robotics/missions-waypoints",
            "title": "Місії й точки"
          },
          {
            "ref": "programming/embedded-systems/failsafe",
            "title": "Failsafe"
          },
          {
            "ref": "programming/embedded-systems/failure-priorities",
            "title": "Пріоритети відмов"
          },
          {
            "ref": "programming/embedded-systems/mode-state-machine",
            "title": "Автомат режимів"
          },
          {
            "ref": "programming/embedded-systems/first-bringup",
            "title": "Перший запуск"
          }
        ]
      },
      {
        "title": "Відеосигнали I: від світла до кадру",
        "steps": [
          {
            "ref": "electronics/optoelectronics/image-sensor",
            "title": "Сенсор зображення"
          },
          {
            "ref": "electronics/optoelectronics/cmos-matrix",
            "title": "CMOS-матриця"
          },
          {
            "ref": "algorithms/computer-vision/bayer-demosaic",
            "title": "Демозаїка"
          },
          {
            "ref": "electronics/optoelectronics/dynamic-range-noise",
            "title": "Динамічний діапазон"
          },
          {
            "ref": "communications/signal-processing/resolution-framerate",
            "title": "Роздільність і кадри"
          },
          {
            "ref": "communications/modulation/analog-video",
            "title": "Аналогове відео"
          },
          {
            "ref": "programming/embedded-systems/video-latency",
            "title": "Затримка відео"
          }
        ]
      },
      {
        "title": "Відеосигнали II: стиснення й передача",
        "steps": [
          {
            "ref": "algorithms/data-compression/why-compress",
            "title": "Навіщо стискати"
          },
          {
            "ref": "algorithms/data-compression/jpeg-intra",
            "title": "JPEG"
          },
          {
            "ref": "algorithms/data-compression/inter-frame",
            "title": "Міжкадрове стиснення"
          },
          {
            "ref": "algorithms/data-compression/mjpeg-vs-h264",
            "title": "MJPEG vs H.264"
          },
          {
            "ref": "algorithms/data-compression/quality-bitrate",
            "title": "Якість і бітрейт"
          },
          {
            "ref": "communications/networks/video-transmission",
            "title": "Передача відео"
          },
          {
            "ref": "communications/networks/bandwidth-loss",
            "title": "Пропускна й втрати"
          },
          {
            "ref": "algorithms/data-compression/lossless-huffman-lz",
            "title": "Стиснення без втрат"
          }
        ]
      },
      {
        "title": "Машинне бачення: основи",
        "steps": [
          {
            "ref": "algorithms/computer-vision/image-as-data",
            "title": "Зображення як дані"
          },
          {
            "ref": "algorithms/computer-vision/histogram",
            "title": "Гістограма"
          },
          {
            "ref": "algorithms/computer-vision/convolution-filters",
            "title": "Згортки й фільтри"
          },
          {
            "ref": "algorithms/computer-vision/edge-detection",
            "title": "Виділення меж"
          },
          {
            "ref": "algorithms/computer-vision/threshold-morphology",
            "title": "Пороги й морфологія"
          },
          {
            "ref": "algorithms/computer-vision/object-detection",
            "title": "Виявлення об'єктів"
          },
          {
            "ref": "algorithms/computer-vision/nn-detectors",
            "title": "Нейродетектори"
          },
          {
            "ref": "algorithms/computer-vision/tracking",
            "title": "Трекінг"
          },
          {
            "ref": "algorithms/computer-vision/compute-cost",
            "title": "Вартість обчислень"
          }
        ]
      },
      {
        "title": "Машинне навчання й нейромережі на пристрої",
        "steps": [
          {
            "ref": "algorithms/machine-learning/what-is-ml",
            "title": "Що таке ML"
          },
          {
            "ref": "algorithms/machine-learning/train-vs-inference",
            "title": "Навчання vs вивід"
          },
          {
            "ref": "algorithms/machine-learning/neuron-layer",
            "title": "Нейрон і шар"
          },
          {
            "ref": "algorithms/machine-learning/gradient-descent",
            "title": "Градієнтний спуск"
          },
          {
            "ref": "algorithms/machine-learning/cnn",
            "title": "Згорткові мережі"
          },
          {
            "ref": "algorithms/machine-learning/overfitting",
            "title": "Перенавчання"
          },
          {
            "ref": "algorithms/machine-learning/tinyml",
            "title": "TinyML"
          },
          {
            "ref": "algorithms/machine-learning/where-to-compute",
            "title": "Де рахувати"
          },
          {
            "ref": "algorithms/machine-learning/ml-limits-ethics",
            "title": "Межі й етика"
          }
        ]
      },
      {
        "title": "Бортовий комп'ютер: «політ» + «розум» разом",
        "steps": [
          {
            "ref": "programming/embedded-systems/realtime-vs-compute",
            "title": "Дві ролі на борту"
          },
          {
            "ref": "programming/networking/mavlink-channel",
            "title": "Канал MAVLink"
          },
          {
            "ref": "programming/networking/mavlink-routing",
            "title": "Роутинг MAVLink"
          },
          {
            "ref": "algorithms/signal-robotics/sense-decide-act-loop",
            "title": "Контур offboard"
          },
          {
            "ref": "programming/embedded-systems/trust-boundaries-failsafe",
            "title": "Межі довіри"
          },
          {
            "ref": "programming/software-engineering/sitl-simulation",
            "title": "SITL"
          },
          {
            "ref": "electronics/power-electronics/companion-power-thermal",
            "title": "Енергія й тепло"
          }
        ]
      },
      {
        "title": "Інші автономні платформи: ровер, човен, літак",
        "steps": [
          {
            "ref": "algorithms/signal-robotics/one-stack-many-bodies",
            "title": "Один стек"
          },
          {
            "ref": "algorithms/signal-robotics/rover-steering",
            "title": "Ровер"
          },
          {
            "ref": "physics/mechanics/fixed-wing-lift",
            "title": "Літак"
          },
          {
            "ref": "physics/mechanics/vtol-transition",
            "title": "VTOL-гібриди"
          },
          {
            "ref": "algorithms/signal-robotics/boat-underwater",
            "title": "Човен і підводний"
          },
          {
            "ref": "programming/embedded-systems/dynamics-dependent-failsafe",
            "title": "Failsafe за динамікою"
          },
          {
            "ref": "algorithms/signal-robotics/pure-pursuit-navigation",
            "title": "Навігація pure pursuit"
          },
          {
            "ref": "algorithms/signal-robotics/platform-selection",
            "title": "Вибір платформи"
          }
        ]
      },
      {
        "title": "Наземна станція й оператор",
        "steps": [
          {
            "ref": "programming/software-engineering/gcs-as-system",
            "title": "GCS як система"
          },
          {
            "ref": "communications/radio-engineering/telemetry-link",
            "title": "Канал земля-борт"
          },
          {
            "ref": "communications/protocols/mavlink-from-ground",
            "title": "MAVLink із землі"
          },
          {
            "ref": "algorithms/signal-robotics/mission-planning-map",
            "title": "Планування на карті"
          },
          {
            "ref": "programming/graphics/operator-ergonomics",
            "title": "Ергономіка оператора"
          },
          {
            "ref": "programming/software-engineering/preflight-checklists",
            "title": "Передпольотні чеклисти"
          },
          {
            "ref": "programming/networking/multi-vehicle-one-station",
            "title": "Кілька апаратів"
          },
          {
            "ref": "programming/software-engineering/ground-station-logs",
            "title": "Записи станції"
          }
        ]
      },
      {
        "title": "Зібрати систему від батареї до місії",
        "steps": [
          {
            "ref": "programming/embedded-systems/capstone-task",
            "title": "Капстоун"
          },
          {
            "ref": "electronics/power-electronics/battery-to-controller",
            "title": "Батарея до контролера"
          },
          {
            "ref": "electronics/pcb/components-buses-on-frame",
            "title": "Компоненти й шини"
          },
          {
            "ref": "programming/embedded-systems/firmware-realtime-loop",
            "title": "Прошивка реального часу"
          },
          {
            "ref": "algorithms/signal-robotics/closing-the-loop",
            "title": "Замкнути контур"
          },
          {
            "ref": "programming/embedded-systems/preflight-safety",
            "title": "Безпека до польоту"
          },
          {
            "ref": "programming/embedded-systems/end-to-end-mission",
            "title": "Місія від початку до кінця"
          },
          {
            "ref": "algorithms/signal-robotics/where-next",
            "title": "Куди далі"
          }
        ]
      }
    ]
  }
]
});
