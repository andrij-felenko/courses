export const meta = {
  name: 'migrate-inserts-to-refbooks',
  description: 'Копіювання math-*/comp-* вставок у довідкові книги math/ і components/ + аудит глибини',
  phases: [
    { title: 'Sectors', detail: 'Нові сектори: discrete-logic, number-systems, passive, active, displays' },
    { title: 'Copy math', detail: 'Копіювання math-*.md → math/<sector>/<slug>.md' },
    { title: 'Copy comp', detail: 'Копіювання comp-*.md → components/<sector>/<slug>.md' },
    { title: 'Manifests', detail: 'Оновлення manifest-math.js і manifest-comp.js + _status.md' },
    { title: 'Audit', detail: 'Аудит глибини: Feynman / formula-list / stub-needed' },
  ]
}

// ─────────────────────────────────────────────────────────────────────────────
// КЛАСИФІКАЦІЙНА ТАБЛИЦЯ
// src — відносно embedded/
// sector — папка в math/ або components/
// slug — ім'я теки і головного файлу (без .md)
// book — "math" або "comp"
// ─────────────────────────────────────────────────────────────────────────────
const MIGRATIONS = [
  // ── math / calculus ─────────────────────────────────────────────────────
  { book:"math", sector:"calculus", slug:"derivative",          src:"block-1-circuits-physics/voltage-current-conduction/math-derivative.md" },
  { book:"math", sector:"calculus", slug:"derivative-max",      src:"block-1-circuits-physics/equivalent-circuits/math-derivative-max.md" },
  { book:"math", sector:"calculus", slug:"derivative-cap",      src:"block-2-components-analog/capacitor/math-derivative-current.md" },
  { book:"math", sector:"calculus", slug:"exponential-ode",     src:"block-2-components-analog/capacitor/math-exponential-ode.md" },
  { book:"math", sector:"calculus", slug:"rl-ode",              src:"block-2-components-analog/inductor/math-rl-ode.md" },
  { book:"math", sector:"calculus", slug:"rms-derivation",      src:"block-1-circuits-physics/ac-signals/math-rms-derivation.md" },
  { book:"math", sector:"calculus", slug:"sine-derivative",     src:"block-2-components-analog/reactance-resonance/math-sine-derivative.md" },
  { book:"math", sector:"calculus", slug:"work-integral",       src:"block-1-circuits-physics/charge-field-potential/math-work-integral.md" },
  { book:"math", sector:"calculus", slug:"half-power",          src:"block-2-components-analog/frequency-response/math-half-power.md" },
  { book:"math", sector:"calculus", slug:"logarithms",          src:"block-2-components-analog/frequency-response/math-logarithms.md" },
  { book:"math", sector:"calculus", slug:"transfer-function",   src:"block-2-components-analog/frequency-response/math-transfer-function.md" },
  { book:"math", sector:"calculus", slug:"cascading",           src:"block-2-components-analog/frequency-response/math-cascading.md" },
  { book:"math", sector:"calculus", slug:"thomson-formula",     src:"block-2-components-analog/reactance-resonance/math-thomson-formula.md" },

  // ── math / trigonometry-phasors ─────────────────────────────────────────
  { book:"math", sector:"trigonometry-phasors", slug:"sine-cosine",      src:"block-1-circuits-physics/ac-signals/math-trigonometry.md" },
  { book:"math", sector:"trigonometry-phasors", slug:"phasors",          src:"block-1-circuits-physics/ac-signals/math-phasor.md" },
  { book:"math", sector:"trigonometry-phasors", slug:"complex-phasors",  src:"block-2-components-analog/reactance-resonance/math-complex-phasors.md" },
  { book:"math", sector:"trigonometry-phasors", slug:"impedance",        src:"block-2-components-analog/reactance-resonance/math-impedance.md" },
  { book:"math", sector:"trigonometry-phasors", slug:"power-triangle",   src:"block-2-components-analog/reactance-resonance/math-power-triangle.md" },
  { book:"math", sector:"trigonometry-phasors", slug:"damping",          src:"block-2-components-analog/reactance-resonance/math-damping.md" },
  { book:"math", sector:"trigonometry-phasors", slug:"q-factor",         src:"block-2-components-analog/reactance-resonance/math-q-factor.md" },

  // ── math / statistics-errors ────────────────────────────────────────────
  { book:"math", sector:"statistics-errors", slug:"random-variables", src:"block-1-circuits-physics/noise-interference/math-random-variables.md" },
  { book:"math", sector:"statistics-errors", slug:"central-limit",    src:"block-1-circuits-physics/noise-interference/math-clt.md" },
  { book:"math", sector:"statistics-errors", slug:"averaging",        src:"block-1-circuits-physics/noise-interference/math-averaging.md" },
  { book:"math", sector:"statistics-errors", slug:"kt-thermal",       src:"block-1-circuits-physics/noise-interference/math-kt-scale.md" },
  { book:"math", sector:"statistics-errors", slug:"noise-density",    src:"block-1-circuits-physics/noise-interference/math-noise-density.md" },
  { book:"math", sector:"statistics-errors", slug:"accuracy",         src:"block-1-circuits-physics/schematics-measurement/math-accuracy.md" },
  { book:"math", sector:"statistics-errors", slug:"tolerance",        src:"block-1-circuits-physics/kirchhoff-circuit-analysis/math-tolerance.md" },
  { book:"math", sector:"statistics-errors", slug:"ppm-math",         src:"block-2-components-analog/resonators-references/math-ppm-math.md" },
  { book:"math", sector:"statistics-errors", slug:"q-stability",      src:"block-2-components-analog/resonators-references/math-q-stability.md" },
  { book:"math", sector:"statistics-errors", slug:"derating",         src:"block-2-components-analog/reading-datasheets/math-derating.md" },
  { book:"math", sector:"statistics-errors", slug:"thermal-resistance",src:"block-2-components-analog/reading-datasheets/math-thermal-resistance.md" },

  // ── math / linear-algebra ───────────────────────────────────────────────
  { book:"math", sector:"linear-algebra", slug:"gauss-elimination",   src:"block-1-circuits-physics/kirchhoff-circuit-analysis/math-gauss.md" },
  { book:"math", sector:"linear-algebra", slug:"matrices-as-operations",src:"block-1-circuits-physics/kirchhoff-circuit-analysis/math-matrix-machine.md" },
  { book:"math", sector:"linear-algebra", slug:"hamming-distance",    src:"block-3-digital-processor/error-correction/math-hamming-distance.md" },
  { book:"math", sector:"linear-algebra", slug:"crc-cyclic-redundancy",src:"block-3-digital-processor/error-correction/math-gf2-polynomials.md" },

  // ── math / vector-analysis ──────────────────────────────────────────────
  { book:"math", sector:"vector-analysis", slug:"vector-components", src:"block-1-circuits-physics/charge-field-potential/math-vectors.md" },
  { book:"math", sector:"vector-analysis", slug:"gradient",          src:"block-1-circuits-physics/charge-field-potential/math-gradient.md" },
  { book:"math", sector:"vector-analysis", slug:"cross-product",     src:"block-1-circuits-physics/magnetism/math-cross-product.md" },

  // ── math / discrete-logic (НОВИЙ СЕКТОР) ────────────────────────────────
  { book:"math", sector:"discrete-logic", slug:"boolean-algebra",  src:"block-3-digital-processor/logic-gates/math-boolean-algebra.md" },
  { book:"math", sector:"discrete-logic", slug:"karnaugh-maps",    src:"block-3-digital-processor/logic-gates/math-karnaugh-maps.md" },
  { book:"math", sector:"discrete-logic", slug:"fsm-formal",       src:"block-3-digital-processor/flip-flops-registers/math-fsm-formal.md" },
  { book:"math", sector:"discrete-logic", slug:"superposition",    src:"block-1-circuits-physics/equivalent-circuits/math-linearity.md" },
  { book:"math", sector:"discrete-logic", slug:"graph-theory",     src:"block-1-circuits-physics/kirchhoff-circuit-analysis/math-graphs.md" },

  // ── math / number-systems (НОВИЙ СЕКТОР) ────────────────────────────────
  { book:"math", sector:"number-systems", slug:"modular-arithmetic",   src:"block-3-digital-processor/number-representation/math-modular-arithmetic.md" },
  { book:"math", sector:"number-systems", slug:"ieee754",              src:"block-3-digital-processor/number-representation/math-ieee754-details.md" },
  { book:"math", sector:"number-systems", slug:"address-space",        src:"block-3-digital-processor/memory-stack-heap/math-address-space.md" },
  { book:"math", sector:"number-systems", slug:"si-prefixes",          src:"block-1-circuits-physics/charge-field-potential/math-si-prefixes.md" },
  { book:"math", sector:"number-systems", slug:"dimensional-analysis", src:"block-1-circuits-physics/charge-field-potential/math-dimensional-analysis.md" },
  { book:"math", sector:"number-systems", slug:"e-series",             src:"block-1-circuits-physics/resistance-power-heat/math-e-series.md" },
  { book:"math", sector:"number-systems", slug:"energy-units",         src:"block-1-circuits-physics/resistance-power-heat/math-energy-units.md" },

  // ── components / passive (НОВИЙ СЕКТОР) ─────────────────────────────────
  { book:"comp", sector:"passive", slug:"mlcc",               src:"block-2-components-analog/capacitor/comp-mlcc.md" },
  { book:"comp", sector:"passive", slug:"electrolytic",       src:"block-2-components-analog/capacitor/comp-electrolytic-tantalum.md" },
  { book:"comp", sector:"passive", slug:"capacitor-marking",  src:"block-2-components-analog/capacitor/comp-marking-sizes.md" },
  { book:"comp", sector:"passive", slug:"bleeder",            src:"block-2-components-analog/capacitor/comp-bleeder.md" },
  { book:"comp", sector:"passive", slug:"decoupling",         src:"block-2-components-analog/capacitor/comp-decoupling.md" },
  { book:"comp", sector:"passive", slug:"supercap",           src:"block-2-components-analog/capacitor/comp-supercap-backup.md" },
  { book:"comp", sector:"passive", slug:"power-inductor",     src:"block-2-components-analog/inductor/comp-power-inductors.md" },
  { book:"comp", sector:"passive", slug:"transformer",        src:"block-2-components-analog/inductor/comp-transformers.md" },
  { book:"comp", sector:"passive", slug:"ferrite-clamp",      src:"block-2-components-analog/inductor/comp-ferrite-clamp.md" },
  { book:"comp", sector:"passive", slug:"resistor-marking",   src:"block-1-circuits-physics/resistance-power-heat/comp-resistor-marking.md" },
  { book:"comp", sector:"passive", slug:"wire-gauge",         src:"block-1-circuits-physics/resistance-power-heat/comp-wires.md" },
  { book:"comp", sector:"passive", slug:"kelvin-shunt",       src:"block-1-circuits-physics/resistance-power-heat/comp-shunt-kelvin.md" },
  { book:"comp", sector:"passive", slug:"heatsink",           src:"block-1-circuits-physics/resistance-power-heat/comp-heatsinks.md" },
  { book:"comp", sector:"passive", slug:"peltier",            src:"block-1-circuits-physics/resistance-power-heat/comp-peltier.md" },
  { book:"comp", sector:"passive", slug:"magnet-grades",      src:"block-1-circuits-physics/magnetism/comp-magnet-grades.md" },
  { book:"comp", sector:"passive", slug:"ferrite-bead",       src:"block-1-circuits-physics/magnetism/comp-ferrites.md" },
  { book:"comp", sector:"passive", slug:"watch-crystal",      src:"block-2-components-analog/resonators-references/comp-watch-crystal.md" },
  { book:"comp", sector:"passive", slug:"potentiometer",      src:"block-1-circuits-physics/kirchhoff-circuit-analysis/comp-potentiometer.md" },
  { book:"comp", sector:"passive", slug:"packages",           src:"block-2-components-analog/reading-datasheets/comp-packages.md" },
  { book:"comp", sector:"passive", slug:"smd-marking",        src:"block-2-components-analog/reading-datasheets/comp-smd-marking.md" },

  // ── components / active (НОВИЙ СЕКТОР) ──────────────────────────────────
  { book:"comp", sector:"active", slug:"diode-families",      src:"block-2-components-analog/diode-pn-junction/comp-diode-families.md" },
  { book:"comp", sector:"active", slug:"bjt-families",        src:"block-2-components-analog/bjt/comp-bjt-families.md" },
  { book:"comp", sector:"active", slug:"darlington-uln",      src:"block-2-components-analog/bjt/comp-darlington-uln.md" },
  { book:"comp", sector:"active", slug:"mosfet-body-diode",   src:"block-2-components-analog/mosfet/comp-body-diode.md" },
  { book:"comp", sector:"active", slug:"gate-driver",         src:"block-2-components-analog/mosfet/comp-gate-driver.md" },
  { book:"comp", sector:"active", slug:"logic-level-mosfet",  src:"block-2-components-analog/mosfet/comp-logic-level.md" },
  { book:"comp", sector:"active", slug:"pmos-load-switch",    src:"block-2-components-analog/mosfet/comp-pmos-load-switch.md" },
  { book:"comp", sector:"active", slug:"ideal-diode-ic",      src:"block-2-components-analog/mosfet/comp-ideal-diode.md" },
  { book:"comp", sector:"active", slug:"comparator-ics",      src:"block-2-components-analog/opamp-comparator/comp-comparator-ics.md" },
  { book:"comp", sector:"active", slug:"rail-to-rail-opamp",  src:"block-2-components-analog/opamp-comparator/comp-rail-to-rail.md" },
  { book:"comp", sector:"active", slug:"ldo-module",          src:"block-2-components-analog/opamp-comparator/comp-regulator-module.md" },
  { book:"comp", sector:"active", slug:"optocoupler",         src:"block-2-components-analog/diode-pn-junction/comp-optocoupler.md" },
  { book:"comp", sector:"active", slug:"bridge-rectifier",    src:"block-2-components-analog/diode-pn-junction/comp-bridge-rectifier.md" },
  { book:"comp", sector:"active", slug:"led-practice",        src:"block-2-components-analog/diode-pn-junction/comp-leds-practice.md" },
  { book:"comp", sector:"active", slug:"tvs-diode",           src:"block-2-components-analog/diode-pn-junction/comp-tvs-esd.md" },
  { book:"comp", sector:"active", slug:"logic-74-families",   src:"block-3-digital-processor/logic-levels/comp-74-families.md" },
  { book:"comp", sector:"active", slug:"schmitt-74hc14",      src:"block-3-digital-processor/logic-levels/comp-74hc14.md" },
  { book:"comp", sector:"active", slug:"tl431",               src:"block-2-components-analog/legendary-analog-ics/comp-tl431.md" },
  { book:"comp", sector:"active", slug:"analog-mux",          src:"block-2-components-analog/legendary-analog-ics/comp-analog-mux.md" },
  { book:"comp", sector:"active", slug:"ssr",                 src:"block-2-components-analog/ac-power-switching/comp-ssr.md" },

  // ── components / protection ──────────────────────────────────────────────
  { book:"comp", sector:"protection", slug:"gas-discharge-tube",   src:"block-1-circuits-physics/esd-static/comp-spark-gap-gdt.md" },
  { book:"comp", sector:"protection", slug:"battery-protection-ic",src:"block-10-power-energy/batteries-charging/comp-dw01-protection.md" },
  { book:"comp", sector:"protection", slug:"mov-varistor",         src:"block-2-components-analog/ac-power-switching/comp-mov-fuse.md" },
  { book:"comp", sector:"protection", slug:"inrush-ntc",           src:"block-1-circuits-physics/resistance-power-heat/comp-inrush-ntc.md" },
  { book:"comp", sector:"protection", slug:"fuse-types",           src:"block-1-circuits-physics/resistance-power-heat/comp-fuse-types.md" },
  { book:"comp", sector:"protection", slug:"crowbar",              src:"block-2-components-analog/ac-power-switching/comp-crowbar.md" },

  // ── components / power ───────────────────────────────────────────────────
  { book:"comp", sector:"power", slug:"tp4056-charger",  src:"block-10-power-energy/batteries-charging/comp-tp4056.md" },
  { book:"comp", sector:"power", slug:"fuel-gauge",      src:"block-10-power-energy/batteries-charging/comp-fuel-gauge.md" },
  { book:"comp", sector:"power", slug:"usb-cc-resistors",src:"block-10-power-energy/usb-power/comp-cc-resistors.md" },
  { book:"comp", sector:"power", slug:"usb-pd-sink",     src:"block-10-power-energy/usb-power/comp-pd-sink.md" },
  { book:"comp", sector:"power", slug:"power-path",      src:"block-10-power-energy/usb-power/comp-power-path.md" },
  { book:"comp", sector:"power", slug:"sync-rectifier",  src:"block-10-power-energy/converter-topologies/comp-sync-vs-async.md" },
  { book:"comp", sector:"power", slug:"charge-pump",     src:"block-10-power-energy/converter-topologies/comp-charge-pumps.md" },
  { book:"comp", sector:"power", slug:"wall-adapter",    src:"block-10-power-energy/converter-topologies/comp-wall-adapter.md" },
  { book:"comp", sector:"power", slug:"dc-dc-module",    src:"block-10-power-energy/converter-design/comp-power-modules.md" },
  { book:"comp", sector:"power", slug:"electronic-load", src:"block-10-power-energy/converter-design/comp-electronic-load.md" },

  // ── components / displays (НОВИЙ СЕКТОР) ────────────────────────────────
  { book:"comp", sector:"displays", slug:"ssd1306-oled",    src:"block-13-ui-hmi/displays-touch/comp-ssd1306.md" },
  { book:"comp", sector:"displays", slug:"spi-tft",         src:"block-13-ui-hmi/displays-touch/comp-spi-tft.md" },
  { book:"comp", sector:"displays", slug:"backlight-driver",src:"block-13-ui-hmi/displays-touch/comp-backlight-drivers.md" },
  { book:"comp", sector:"displays", slug:"eink-module",     src:"block-13-ui-hmi/displays-touch/comp-eink-modules.md" },
  { book:"comp", sector:"displays", slug:"touch-controller",src:"block-13-ui-hmi/displays-touch/comp-touch-controllers.md" },

  // ── components / comms ───────────────────────────────────────────────────
  { book:"comp", sector:"comms", slug:"nfc-rfid",        src:"block-2-components-analog/reactance-resonance/comp-nfc-rfid.md" },
  { book:"comp", sector:"comms", slug:"utp-cable",       src:"block-1-circuits-physics/noise-interference/comp-utp-cables.md" },
  { book:"comp", sector:"comms", slug:"shielded-cable",  src:"block-1-circuits-physics/noise-interference/comp-shielded-cables.md" },
  { book:"comp", sector:"comms", slug:"wroom-module",    src:"block-4-mcu-esp32/mcu-esp32/comp-wroom-module.md" },
  { book:"comp", sector:"comms", slug:"esp32-antenna",   src:"block-4-mcu-esp32/mcu-esp32/comp-antenna.md" },

  // ── components / interfaces ──────────────────────────────────────────────
  { book:"comp", sector:"interfaces", slug:"usb-c-connector",  src:"block-4-mcu-esp32/usb-mcu/comp-usb-c.md" },
  { book:"comp", sector:"interfaces", slug:"solenoid-relay",   src:"block-1-circuits-physics/magnetism/comp-solenoid-relay.md" },
  { book:"comp", sector:"interfaces", slug:"74hc165-piso",     src:"block-3-digital-processor/flip-flops-registers/comp-74hc165.md" },
  { book:"comp", sector:"interfaces", slug:"74hc595-sipo",     src:"block-3-digital-processor/flip-flops-registers/comp-74hc595.md" },
  { book:"comp", sector:"interfaces", slug:"74hc138-decoder",  src:"block-3-digital-processor/logic-gates/comp-74hc138-chip-select.md" },
  { book:"comp", sector:"interfaces", slug:"gpio-expander",    src:"block-4-mcu-esp32/gpio/comp-gpio-expander.md" },
  { book:"comp", sector:"interfaces", slug:"usb-uart-bridge",  src:"block-4-mcu-esp32/usb-mcu/comp-usb-uart.md" },
  { book:"comp", sector:"interfaces", slug:"rtc-module",       src:"block-4-mcu-esp32/execution-rtos/comp-rtc-module.md" },

  // ── components / memory (існуючий сектор) ───────────────────────────────
  { book:"comp", sector:"memory", slug:"psram",          src:"block-3-digital-processor/memory-stack-heap/comp-psram.md" },
  { book:"comp", sector:"memory", slug:"sd-card-module", src:"block-4-mcu-esp32/storage/comp-sd-module.md" },
  { book:"comp", sector:"memory", slug:"fram",           src:"block-4-mcu-esp32/storage/comp-fram.md" },

  // ── components / sensors (існуючий сектор) ──────────────────────────────
  { book:"comp", sector:"sensors", slug:"clamp-meter",   src:"block-1-circuits-physics/magnetism/comp-clamp-meter.md" },
]

// ─────────────────────────────────────────────────────────────────────────────
// НОВІ СЕКТОРИ (файли _status.md, що треба створити)
// ─────────────────────────────────────────────────────────────────────────────
const NEW_SECTORS = [
  {
    book: "math", sector: "discrete-logic",
    title: "Дискретна логіка і теорія графів",
    desc: "Булева алгебра (аксіоми, Де Морган, доведення), мапи Карно, формалізм скінченних автоматів, принцип суперпозиції, теорія графів для аналізу кіл.",
    entries: [
      "## Розділ 6.1 — Булева алгебра: аксіоми і доведення законів · `discrete-logic/boolean-algebra/`",
      "## Розділ 6.2 — Мапи Карно: мінімізація без перебору · `discrete-logic/karnaugh-maps/`",
      "## Розділ 6.3 — Формалізм ДКА: скінченний автомат як математична структура · `discrete-logic/fsm-formal/`",
      "## Розділ 6.4 — Принцип суперпозиції: чому лінійна система розкладається · `discrete-logic/superposition/`",
      "## Розділ 6.5 — Теорія графів: орієнтований граф кола · `discrete-logic/graph-theory/`",
    ]
  },
  {
    book: "math", sector: "number-systems",
    title: "Системи числення і одиниці",
    desc: "IEEE 754 з плаваючою точкою, модульна арифметика (доповняльний код, wrap), адресний простір (2^N), СІ-префікси, розмірний аналіз, ряди Е.",
    entries: [
      "## Розділ 7.1 — IEEE 754: як комп'ютер зберігає 3.14 · `number-systems/ieee754/`",
      "## Розділ 7.2 — Модульна арифметика: переповнення без аварії · `number-systems/modular-arithmetic/`",
      "## Розділ 7.3 — Адресний простір: звідки 2^N і чому байт-адресація · `number-systems/address-space/`",
      "## Розділ 7.4 — Префікси СІ: масштаб від піко до тера · `number-systems/si-prefixes/`",
      "## Розділ 7.5 — Розмірний аналіз: як перевірити формулу без рахунку · `number-systems/dimensional-analysis/`",
      "## Розділ 7.6 — Ряди Е і допуски: чому резисторів рівно 96 значень · `number-systems/e-series/`",
      "## Розділ 7.7 — Одиниці енергії: джоуль, ват-година, еВ і їх зв'язки · `number-systems/energy-units/`",
    ]
  },
  {
    book: "comp", sector: "passive",
    title: "Пасивні компоненти",
    desc: "Конденсатори (MLCC, електролітичні, суперконденсатори), котушки, трансформатори, резистори, дроти, кристали, радіатори. Реальні класи деталей із типовими характеристиками.",
    entries: [
      "## Розділ 8.1 — MLCC: класи X7R/C0G/Y5V і DC bias · `passive/mlcc/`",
      "## Розділ 8.2 — Електролітичні і танталові конденсатори · `passive/electrolytic/`",
      "## Розділ 8.3 — Маркування конденсаторів і типорозміри · `passive/capacitor-marking/`",
      "## Розділ 8.4 — Розрядний резистор (bleeder) · `passive/bleeder/`",
      "## Розділ 8.5 — Розв'язуючий конденсатор: вибір і розташування · `passive/decoupling/`",
      "## Розділ 8.6 — Суперконденсатор як backup-джерело · `passive/supercap/`",
      "## Розділ 8.7 — Силові котушки: вибір і паразити · `passive/power-inductor/`",
      "## Розділ 8.8 — Трансформатори в схемах · `passive/transformer/`",
      "## Розділ 8.9 — Феритовий затискач (ferrite clamp) · `passive/ferrite-clamp/`",
      "## Розділ 8.10 — Маркування резисторів (E-ряд, SMD) · `passive/resistor-marking/`",
      "## Розділ 8.11 — Перерізи дротів і AWG · `passive/wire-gauge/`",
      "## Розділ 8.12 — Шунт Кельвіна: 4-провідний вимір · `passive/kelvin-shunt/`",
      "## Розділ 8.13 — Радіатори і монтажна термопаста · `passive/heatsink/`",
      "## Розділ 8.14 — Елемент Пельтьє · `passive/peltier/`",
      "## Розділ 8.15 — Марки постійних магнітів · `passive/magnet-grades/`",
      "## Розділ 8.16 — Феритова намистина (ferrite bead) · `passive/ferrite-bead/`",
      "## Розділ 8.17 — Годинниковий кварц · `passive/watch-crystal/`",
      "## Розділ 8.18 — Потенціометр і триммер · `passive/potentiometer/`",
      "## Розділ 8.19 — Корпуси SMD/THT і типорозміри · `passive/packages/`",
      "## Розділ 8.20 — Маркування SMD-компонентів · `passive/smd-marking/`",
    ]
  },
  {
    book: "comp", sector: "active",
    title: "Активні компоненти",
    desc: "Транзистори (BJT, MOSFET, Дарлінгтон), діоди (сімейства, TVS, оптрон), операційні підсилювачі і компаратори, логічні мікросхеми (74xx), регулятори, симістори.",
    entries: [
      "## Розділ 9.1 — Сімейства діодів: від p–n до шоттківського · `active/diode-families/`",
      "## Розділ 9.2 — Сімейства BJT: NPN/PNP, пакети, параметри · `active/bjt-families/`",
      "## Розділ 9.3 — Дарлінгтон і ULN2003: «підсилення струму» для реле · `active/darlington-uln/`",
      "## Розділ 9.4 — Захисний діод MOSFET (body diode) · `active/mosfet-body-diode/`",
      "## Розділ 9.5 — Драйвер затвора MOSFET · `active/gate-driver/`",
      "## Розділ 9.6 — Logic-level MOSFET: ключ від 3.3 В · `active/logic-level-mosfet/`",
      "## Розділ 9.7 — P-MOSFET як ключ верхнього плеча · `active/pmos-load-switch/`",
      "## Розділ 9.8 — Ідеальний діод на MOSFET · `active/ideal-diode-ic/`",
      "## Розділ 9.9 — Мікросхеми компараторів · `active/comparator-ics/`",
      "## Розділ 9.10 — Rail-to-rail операційні підсилювачі · `active/rail-to-rail-opamp/`",
      "## Розділ 9.11 — LDO-модулі і мікросхеми стабілізаторів · `active/ldo-module/`",
      "## Розділ 9.12 — Оптрон (optocoupler) · `active/optocoupler/`",
      "## Розділ 9.13 — Діодний міст · `active/bridge-rectifier/`",
      "## Розділ 9.14 — Світлодіоди на практиці · `active/led-practice/`",
      "## Розділ 9.15 — TVS-діод (захист від ESD і перенапруги) · `active/tvs-diode/`",
      "## Розділ 9.16 — Логічні сімейства 74xx · `active/logic-74-families/`",
      "## Розділ 9.17 — Тригер Шмітта 74HC14 · `active/schmitt-74hc14/`",
      "## Розділ 9.18 — TL431: програмований ЗЗ-стабілізатор · `active/tl431/`",
      "## Розділ 9.19 — Аналоговий мультиплексор · `active/analog-mux/`",
      "## Розділ 9.20 — Твердотільне реле (SSR) · `active/ssr/`",
    ]
  },
  {
    book: "comp", sector: "displays",
    title: "Дисплеї",
    desc: "OLED-модулі (SSD1306), кольорові TFT (SPI), електронне чорнило, підсвітка, ємнісні контролери дотику. Тип, інтерфейс, типові схеми підключення.",
    entries: [
      "## Розділ 10.1 — SSD1306 OLED 128×64 · `displays/ssd1306-oled/`",
      "## Розділ 10.2 — SPI TFT-дисплей (ILI9341-клас) · `displays/spi-tft/`",
      "## Розділ 10.3 — Драйвер підсвітки LCD/TFT · `displays/backlight-driver/`",
      "## Розділ 10.4 — E-ink модулі (Waveshare-клас) · `displays/eink-module/`",
      "## Розділ 10.5 — Ємнісний контролер дотику · `displays/touch-controller/`",
    ]
  },
]

// ─────────────────────────────────────────────────────────────────────────────
// СХЕМИ ГЛИБИНИ — критерії для аудиту
// ─────────────────────────────────────────────────────────────────────────────
const DEPTH_RUBRIC = `
Оціни файл за трьома критеріями (відповідай лише JSON):
1. depth: "feynman" | "formula-list" | "stub-needed"
   - feynman = пояснює ЧОМУ від першопричини, не просто констатує формули
   - formula-list = наводить формули/факти без пояснення звідки і чому
   - stub-needed = майже порожній або template
2. issues: короткий список конкретних проблем (до 3 пунктів) або []
3. action: "ok" | "deepen" | "rewrite" | "create-stub"

Критерії "feynman":
- Є відповідь на "чому саме так, а не інакше"
- Є фізична або математична інтуїція (не просто формула)
- Є хоча б один приклад застосування в контексті курсу
- Текст ~800+ слів (не враховуючи код і формули)
`

// ─────────────────────────────────────────────────────────────────────────────
// ДОПОМІЖНА ФУНКЦІЯ: читає файл через Bash (cat)
// ─────────────────────────────────────────────────────────────────────────────
async function readEmbeddedFile(srcRelative) {
  const fullPath = `E:/develop/courses/embedded/${srcRelative}`
  const result = await agent(
    `Read the file at path: "${fullPath}" and return its FULL content verbatim. ` +
    `If the file does not exist, return the string "FILE_NOT_FOUND". ` +
    `Do not summarize, do not add comments. Return only the raw file content.`,
    { label: `read:${srcRelative.split('/').pop()}`, model: "haiku" }
  )
  return result || "FILE_NOT_FOUND"
}

// ─────────────────────────────────────────────────────────────────────────────
// ФАЗА 1: НОВІ СЕКТОРИ (_status.md)
// ─────────────────────────────────────────────────────────────────────────────
phase('Sectors')
log(`Створюємо ${NEW_SECTORS.length} нових секторів у math/ і components/`)

await parallel(NEW_SECTORS.map(s => async () => {
  const root = s.book === "math" ? "math" : "components"
  const statusPath = `E:/develop/courses/${root}/${s.sector}/_status.md`
  const bookLabel = s.book === "math" ? "Книга-довідник: математику пояснюємо Фейнман-глибоко" : "Каталог реальних компонентів"

  const body = [
    `# ${s.book === "math" ? "Математика" : "Компоненти"} · ${s.title} — черга`,
    "",
    `> ${bookLabel}`,
    `> Статуси: ⬜ стаб · 🟡 в роботі · 🔄 чернетка · 🟢 готово.`,
    "",
    ...s.entries.map(e => e + "  ⬜"),
  ].join("\n")

  await agent(
    `Create a file at path "${statusPath}" with exactly this content:\n\n${body}\n\n` +
    `Use the Write tool. Create the directory if it doesn't exist (use Bash: mkdir -p <dir>).`,
    { label: `sector:${s.sector}`, phase: 'Sectors' }
  )
  log(`✅ Створено: ${root}/${s.sector}/_status.md`)
}))

// ─────────────────────────────────────────────────────────────────────────────
// ФАЗА 2+3: КОПІЮВАННЯ ФАЙЛІВ
// ─────────────────────────────────────────────────────────────────────────────
phase('Copy math')
const mathMigrations = MIGRATIONS.filter(m => m.book === "math")
const compMigrations = MIGRATIONS.filter(m => m.book === "comp")

log(`Копіюємо ${mathMigrations.length} math-файлів → math/<sector>/<slug>/`)

const mathResults = await pipeline(
  mathMigrations,
  // Stage 1: Read source
  async (m) => {
    const content = await readEmbeddedFile(m.src)
    if (content === "FILE_NOT_FOUND") {
      log(`⚠ Не знайдено: embedded/${m.src}`)
      return null
    }
    return { ...m, content }
  },
  // Stage 2: Write to math book
  async (r, m) => {
    if (!r) return null
    const destDir = `E:/develop/courses/math/${m.sector}/${m.slug}`
    const destFile = `${destDir}/${m.slug}.md`

    // Update header in content: replace "вставка до теми X" with math-book intro
    const updatedContent = r.content.replace(
      /^(# 🧮[^\n]*)\n\n> Це математична вставка до теми[^\n]*/,
      `$1\n\n> Довідник «Математика» · сектор \`${m.sector}\`.`
    )

    await agent(
      `Create directory "${destDir}" if it doesn't exist (Bash: mkdir -p "${destDir}"), ` +
      `then write the following content to "${destFile}" using the Write tool:\n\n${updatedContent}`,
      { label: `copy-math:${m.slug}`, phase: 'Copy math' }
    )
    log(`✅ math/${m.sector}/${m.slug}/${m.slug}.md`)
    return { ...m, destFile, wordCount: updatedContent.split(/\s+/).length }
  }
)

phase('Copy comp')
log(`Копіюємо ${compMigrations.length} comp-файлів → components/<sector>/<slug>/`)

const compResults = await pipeline(
  compMigrations,
  async (m) => {
    const content = await readEmbeddedFile(m.src)
    if (content === "FILE_NOT_FOUND") {
      log(`⚠ Не знайдено: embedded/${m.src}`)
      return null
    }
    return { ...m, content }
  },
  async (r, m) => {
    if (!r) return null
    const destDir = `E:/develop/courses/components/${m.sector}/${m.slug}`
    const destFile = `${destDir}/${m.slug}.md`

    const updatedContent = r.content.replace(
      /^(# 🔌[^\n]*)\n\n> Це компонентна вставка до теми[^\n]*/,
      `$1\n\n> Каталог «Компоненти» · сектор \`${m.sector}\`.`
    )

    await agent(
      `Create directory "${destDir}" if it doesn't exist (Bash: mkdir -p "${destDir}"), ` +
      `then write this content to "${destFile}" using Write tool:\n\n${updatedContent}`,
      { label: `copy-comp:${m.slug}`, phase: 'Copy comp' }
    )
    log(`✅ components/${m.sector}/${m.slug}/${m.slug}.md`)
    return { ...m, destFile, wordCount: updatedContent.split(/\s+/).length }
  }
)

// ─────────────────────────────────────────────────────────────────────────────
// ФАЗА 4: ОНОВЛЕННЯ MANIFEST-MATH.JS і MANIFEST-COMP.JS
// ─────────────────────────────────────────────────────────────────────────────
phase('Manifests')
const donemath = mathResults.filter(Boolean)
const donecomp = compResults.filter(Boolean)

log(`Оновлюємо manifest-math.js (${donemath.length} нових тем) і manifest-comp.js (${donecomp.length} нових тем)`)

await parallel([
  async () => {
    if (donemath.length === 0) return
    // Групуємо по sector
    const bySector = {}
    for (const r of donemath) {
      if (!bySector[r.sector]) bySector[r.sector] = []
      bySector[r.sector].push(r)
    }
    const sectorList = JSON.stringify(bySector, null, 2)
    await agent(
      `Read the file "E:/develop/courses/manifest-math.js". ` +
      `Then, for each module/sector listed below, find the matching module by slug in the manifest. ` +
      `If a chapter entry with that slug is already present, update its status to "done" and add: dir: "<slug>/", main: "<slug>.md". ` +
      `If a chapter entry is missing, add it to the correct module. ` +
      `For NEW modules (discrete-logic → module 6, number-systems → module 7) that don't exist yet, ` +
      `add them at the end of the modules array with the new chapters. ` +
      `Save the result back to "E:/develop/courses/manifest-math.js". ` +
      `Sectors and chapters to add/update:\n${sectorList}`,
      { label: 'manifest-math', phase: 'Manifests' }
    )
    log('✅ manifest-math.js оновлено')
  },
  async () => {
    if (donecomp.length === 0) return
    const bySector = {}
    for (const r of donecomp) {
      if (!bySector[r.sector]) bySector[r.sector] = []
      bySector[r.sector].push(r)
    }
    const sectorList = JSON.stringify(bySector, null, 2)
    await agent(
      `Read the file "E:/develop/courses/manifest-comp.js". ` +
      `For each sector and slug listed below, find or create the matching module/chapter. ` +
      `NEW sectors: passive (module 8), active (module 9), displays (module 10). ` +
      `Existing: sensors(1), power(2), comms(3), actuators(4), protection(5), interfaces(6), memory(7). ` +
      `For each new chapter: status:"done", dir:"<slug>/", main:"<slug>.md". ` +
      `Save back to "E:/develop/courses/manifest-comp.js". ` +
      `Data:\n${sectorList}`,
      { label: 'manifest-comp', phase: 'Manifests' }
    )
    log('✅ manifest-comp.js оновлено')
  }
])

// ─────────────────────────────────────────────────────────────────────────────
// ФАЗА 5: АУДИТ ГЛИБИНИ
// ─────────────────────────────────────────────────────────────────────────────
phase('Audit')
const allMigrated = [...donemath, ...donecomp].filter(Boolean)
log(`Аудит глибини: ${allMigrated.length} файлів`)

const AUDIT_SCHEMA = {
  type: "object",
  properties: {
    slug: { type: "string" },
    depth: { type: "string", enum: ["feynman", "formula-list", "stub-needed"] },
    wordCount: { type: "number" },
    issues: { type: "array", items: { type: "string" } },
    action: { type: "string", enum: ["ok", "deepen", "rewrite", "create-stub"] }
  },
  required: ["slug", "depth", "action"]
}

const auditResults = await pipeline(
  allMigrated,
  async (r) => {
    const result = await agent(
      `Read the file "${r.destFile}". Then assess its depth using this rubric:\n${DEPTH_RUBRIC}\n\n` +
      `Return JSON only. The slug is "${r.slug}". The approximate word count is ${r.wordCount || 0}.`,
      { label: `audit:${r.slug}`, schema: AUDIT_SCHEMA, phase: 'Audit' }
    )
    return result ? { ...r, ...result } : null
  }
)

// ─────────────────────────────────────────────────────────────────────────────
// ПІДСУМКОВИЙ ЗВІТ
// ─────────────────────────────────────────────────────────────────────────────
const valid = auditResults.filter(Boolean)
const needDeepen  = valid.filter(r => r.action === 'deepen')
const needRewrite = valid.filter(r => r.action === 'rewrite')
const needStub    = valid.filter(r => r.action === 'create-stub')
const isOk        = valid.filter(r => r.action === 'ok')

log(`\n═══ ПІДСУМОК МІГРАЦІЇ ═══`)
log(`Скопійовано в math/: ${donemath.length} файлів`)
log(`Скопійовано в comp/: ${donecomp.length} файлів`)
log(`\n═══ АУДИТ ГЛИБИНИ ═══`)
log(`✅ Feynman-deep (ok): ${isOk.length}`)
log(`🔧 Треба заглибити: ${needDeepen.length}`)
log(`🔴 Треба переписати: ${needRewrite.length}`)
log(`⬜ Потрібен стаб: ${needStub.length}`)
log(`\n--- Треба заглибити ---`)
for (const r of needDeepen) log(`  ${r.book}/${r.sector}/${r.slug}: ${(r.issues||[]).join('; ')}`)
log(`\n--- Треба переписати ---`)
for (const r of needRewrite) log(`  ${r.book}/${r.sector}/${r.slug}: ${(r.issues||[]).join('; ')}`)

return {
  copied: { math: donemath.length, comp: donecomp.length },
  audit: { ok: isOk.length, deepen: needDeepen.length, rewrite: needRewrite.length, stub: needStub.length },
  needDeepen: needDeepen.map(r => `${r.book}/${r.sector}/${r.slug}`),
  needRewrite: needRewrite.map(r => `${r.book}/${r.sector}/${r.slug}`),
}
