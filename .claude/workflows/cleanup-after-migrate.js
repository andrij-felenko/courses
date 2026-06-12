export const meta = {
  name: 'cleanup-after-migrate',
  description: 'git rm дублів з embedded/ + оновлення extras у manifest.js на нові шляхи',
  phases: [
    { title: 'Remove dupes', detail: 'git rm кожного файлу що вже є в math/ або components/' },
    { title: 'Update manifest', detail: 'Замінюємо extras у manifest.js на нові відносні шляхи' },
    { title: 'Verify', detail: 'Перевірка: чи немає битих extras, чи нові файли існують' },
  ]
}

// ─────────────────────────────────────────────────────────────────────────────
// ТА САМА ТАБЛИЦЯ ЩО В migrate-inserts.js
// src  — відносно embedded/
// book — "math" або "comp"
// sector, slug — ціль
// ─────────────────────────────────────────────────────────────────────────────
const MIGRATIONS = [
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

  { book:"math", sector:"trigonometry-phasors", slug:"sine-cosine",      src:"block-1-circuits-physics/ac-signals/math-trigonometry.md" },
  { book:"math", sector:"trigonometry-phasors", slug:"phasors",          src:"block-1-circuits-physics/ac-signals/math-phasor.md" },
  { book:"math", sector:"trigonometry-phasors", slug:"complex-phasors",  src:"block-2-components-analog/reactance-resonance/math-complex-phasors.md" },
  { book:"math", sector:"trigonometry-phasors", slug:"impedance",        src:"block-2-components-analog/reactance-resonance/math-impedance.md" },
  { book:"math", sector:"trigonometry-phasors", slug:"power-triangle",   src:"block-2-components-analog/reactance-resonance/math-power-triangle.md" },
  { book:"math", sector:"trigonometry-phasors", slug:"damping",          src:"block-2-components-analog/reactance-resonance/math-damping.md" },
  { book:"math", sector:"trigonometry-phasors", slug:"q-factor",         src:"block-2-components-analog/reactance-resonance/math-q-factor.md" },

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

  { book:"math", sector:"linear-algebra", slug:"gauss-elimination",    src:"block-1-circuits-physics/kirchhoff-circuit-analysis/math-gauss.md" },
  { book:"math", sector:"linear-algebra", slug:"matrices-as-operations",src:"block-1-circuits-physics/kirchhoff-circuit-analysis/math-matrix-machine.md" },
  { book:"math", sector:"linear-algebra", slug:"hamming-distance",     src:"block-3-digital-processor/error-correction/math-hamming-distance.md" },
  { book:"math", sector:"linear-algebra", slug:"crc-cyclic-redundancy",src:"block-3-digital-processor/error-correction/math-gf2-polynomials.md" },

  { book:"math", sector:"vector-analysis", slug:"vector-components", src:"block-1-circuits-physics/charge-field-potential/math-vectors.md" },
  { book:"math", sector:"vector-analysis", slug:"gradient",          src:"block-1-circuits-physics/charge-field-potential/math-gradient.md" },
  { book:"math", sector:"vector-analysis", slug:"cross-product",     src:"block-1-circuits-physics/magnetism/math-cross-product.md" },

  { book:"math", sector:"discrete-logic", slug:"boolean-algebra",  src:"block-3-digital-processor/logic-gates/math-boolean-algebra.md" },
  { book:"math", sector:"discrete-logic", slug:"karnaugh-maps",    src:"block-3-digital-processor/logic-gates/math-karnaugh-maps.md" },
  { book:"math", sector:"discrete-logic", slug:"fsm-formal",       src:"block-3-digital-processor/flip-flops-registers/math-fsm-formal.md" },
  { book:"math", sector:"discrete-logic", slug:"superposition",    src:"block-1-circuits-physics/equivalent-circuits/math-linearity.md" },
  { book:"math", sector:"discrete-logic", slug:"graph-theory",     src:"block-1-circuits-physics/kirchhoff-circuit-analysis/math-graphs.md" },

  { book:"math", sector:"number-systems", slug:"modular-arithmetic",   src:"block-3-digital-processor/number-representation/math-modular-arithmetic.md" },
  { book:"math", sector:"number-systems", slug:"ieee754",              src:"block-3-digital-processor/number-representation/math-ieee754-details.md" },
  { book:"math", sector:"number-systems", slug:"address-space",        src:"block-3-digital-processor/memory-stack-heap/math-address-space.md" },
  { book:"math", sector:"number-systems", slug:"si-prefixes",          src:"block-1-circuits-physics/charge-field-potential/math-si-prefixes.md" },
  { book:"math", sector:"number-systems", slug:"dimensional-analysis", src:"block-1-circuits-physics/charge-field-potential/math-dimensional-analysis.md" },
  { book:"math", sector:"number-systems", slug:"e-series",             src:"block-1-circuits-physics/resistance-power-heat/math-e-series.md" },
  { book:"math", sector:"number-systems", slug:"energy-units",         src:"block-1-circuits-physics/resistance-power-heat/math-energy-units.md" },

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

  { book:"comp", sector:"protection", slug:"gas-discharge-tube",   src:"block-1-circuits-physics/esd-static/comp-spark-gap-gdt.md" },
  { book:"comp", sector:"protection", slug:"battery-protection-ic",src:"block-10-power-energy/batteries-charging/comp-dw01-protection.md" },
  { book:"comp", sector:"protection", slug:"mov-varistor",         src:"block-2-components-analog/ac-power-switching/comp-mov-fuse.md" },
  { book:"comp", sector:"protection", slug:"inrush-ntc",           src:"block-1-circuits-physics/resistance-power-heat/comp-inrush-ntc.md" },
  { book:"comp", sector:"protection", slug:"fuse-types",           src:"block-1-circuits-physics/resistance-power-heat/comp-fuse-types.md" },
  { book:"comp", sector:"protection", slug:"crowbar",              src:"block-2-components-analog/ac-power-switching/comp-crowbar.md" },

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

  { book:"comp", sector:"displays", slug:"ssd1306-oled",    src:"block-13-ui-hmi/displays-touch/comp-ssd1306.md" },
  { book:"comp", sector:"displays", slug:"spi-tft",         src:"block-13-ui-hmi/displays-touch/comp-spi-tft.md" },
  { book:"comp", sector:"displays", slug:"backlight-driver",src:"block-13-ui-hmi/displays-touch/comp-backlight-drivers.md" },
  { book:"comp", sector:"displays", slug:"eink-module",     src:"block-13-ui-hmi/displays-touch/comp-eink-modules.md" },
  { book:"comp", sector:"displays", slug:"touch-controller",src:"block-13-ui-hmi/displays-touch/comp-touch-controllers.md" },

  { book:"comp", sector:"comms", slug:"nfc-rfid",        src:"block-2-components-analog/reactance-resonance/comp-nfc-rfid.md" },
  { book:"comp", sector:"comms", slug:"utp-cable",       src:"block-1-circuits-physics/noise-interference/comp-utp-cables.md" },
  { book:"comp", sector:"comms", slug:"shielded-cable",  src:"block-1-circuits-physics/noise-interference/comp-shielded-cables.md" },
  { book:"comp", sector:"comms", slug:"wroom-module",    src:"block-4-mcu-esp32/mcu-esp32/comp-wroom-module.md" },
  { book:"comp", sector:"comms", slug:"esp32-antenna",   src:"block-4-mcu-esp32/mcu-esp32/comp-antenna.md" },

  { book:"comp", sector:"interfaces", slug:"usb-c-connector",  src:"block-4-mcu-esp32/usb-mcu/comp-usb-c.md" },
  { book:"comp", sector:"interfaces", slug:"solenoid-relay",   src:"block-1-circuits-physics/magnetism/comp-solenoid-relay.md" },
  { book:"comp", sector:"interfaces", slug:"74hc165-piso",     src:"block-3-digital-processor/flip-flops-registers/comp-74hc165.md" },
  { book:"comp", sector:"interfaces", slug:"74hc595-sipo",     src:"block-3-digital-processor/flip-flops-registers/comp-74hc595.md" },
  { book:"comp", sector:"interfaces", slug:"74hc138-decoder",  src:"block-3-digital-processor/logic-gates/comp-74hc138-chip-select.md" },
  { book:"comp", sector:"interfaces", slug:"gpio-expander",    src:"block-4-mcu-esp32/gpio/comp-gpio-expander.md" },
  { book:"comp", sector:"interfaces", slug:"usb-uart-bridge",  src:"block-4-mcu-esp32/usb-mcu/comp-usb-uart.md" },
  { book:"comp", sector:"interfaces", slug:"rtc-module",       src:"block-4-mcu-esp32/execution-rtos/comp-rtc-module.md" },

  { book:"comp", sector:"memory", slug:"psram",          src:"block-3-digital-processor/memory-stack-heap/comp-psram.md" },
  { book:"comp", sector:"memory", slug:"sd-card-module", src:"block-4-mcu-esp32/storage/comp-sd-module.md" },
  { book:"comp", sector:"memory", slug:"fram",           src:"block-4-mcu-esp32/storage/comp-fram.md" },

  { book:"comp", sector:"sensors", slug:"clamp-meter",   src:"block-1-circuits-physics/magnetism/comp-clamp-meter.md" },
]

// ─────────────────────────────────────────────────────────────────────────────
// БУДУЄМО LOOKUP: старе ім'я файлу → новий відносний шлях
// Усі embedded-розділи на глибині 2 → 3× "../" виходимо до кореня
// ─────────────────────────────────────────────────────────────────────────────
const OLD_TO_NEW = {}
for (const m of MIGRATIONS) {
  const oldFileName = m.src.split('/').pop()          // напр. "math-boolean-algebra.md"
  const root = m.book === "math" ? "math" : "components"
  const newRelPath = `../../../${root}/${m.sector}/${m.slug}/${m.slug}.md`
  OLD_TO_NEW[oldFileName] = { newRelPath, m }
}

// ─────────────────────────────────────────────────────────────────────────────
// ФАЗА 1: git rm старих файлів (паралельно батчами по 20)
// ─────────────────────────────────────────────────────────────────────────────
phase('Remove dupes')
log(`Видаляємо ${MIGRATIONS.length} оригінальних файлів з embedded/ через git rm`)

// Перевіряємо які з нових файлів реально існують перед git rm
const existCheck = await agent(
  `Run this command in E:/develop/courses and return the output:\n` +
  `git ls-files embedded/ | grep -E "(math-|comp-)" | head -200\n\n` +
  `Return the raw list of tracked files.`,
  { label: 'check-tracked' }
)
log(`Tracked inserts у embedded/: ${(existCheck || '').split('\n').filter(Boolean).length} файлів`)

// git rm батчами
const batches = []
for (let i = 0; i < MIGRATIONS.length; i += 20) {
  batches.push(MIGRATIONS.slice(i, i + 20))
}

const rmResults = await parallel(batches.map((batch, bi) => async () => {
  const paths = batch.map(m => `embedded/${m.src}`).join(' ')
  const result = await agent(
    `Run the following git command in directory E:/develop/courses:\n` +
    `git rm --force --ignore-unmatch ${paths}\n\n` +
    `Report how many files were removed (look for "rm 'path'" lines in output). ` +
    `If a file was already untracked/missing, --ignore-unmatch skips it silently — that's fine.`,
    { label: `git-rm-batch-${bi + 1}` , phase: 'Remove dupes' }
  )
  return result
}))

log(`git rm завершено для всіх батчів`)

// ─────────────────────────────────────────────────────────────────────────────
// ФАЗА 2: ОНОВЛЕННЯ manifest.js EXTRAS
// ─────────────────────────────────────────────────────────────────────────────
phase('Update manifest')
log(`Оновлюємо extras у manifest.js: замінюємо ${Object.keys(OLD_TO_NEW).length} записів`)

// Будуємо список замін для агента
const replacements = Object.entries(OLD_TO_NEW).map(([old, {newRelPath}]) =>
  `  "${old}" → "${newRelPath}"`
).join('\n')

await agent(
  `Read the file "E:/develop/courses/manifest.js".\n\n` +
  `In the extras arrays, replace ONLY the following old filenames with the new relative paths.\n` +
  `Do NOT change anything else — preserve all formatting, indentation, and other entries.\n\n` +
  `Replacements (old → new):\n${replacements}\n\n` +
  `After making ALL replacements, write the updated content back to "E:/develop/courses/manifest.js".\n` +
  `Important: the replacements are inside string arrays like extras: ["file.md", "other.md"]. ` +
  `Match the exact filename string (with quotes and .md) and replace just that string.`,
  { label: 'update-manifest-js', phase: 'Update manifest' }
)
log('✅ manifest.js оновлено')

// ─────────────────────────────────────────────────────────────────────────────
// ФАЗА 3: ВЕРИФІКАЦІЯ
// ─────────────────────────────────────────────────────────────────────────────
phase('Verify')

const [verifyNew, verifyOld, verifyManifest] = await parallel([
  // Чи всі нові файли існують?
  async () => agent(
    `Run in E:/develop/courses:\n` +
    `git ls-files math/ components/ | grep -E "\\.(md)$" | wc -l\n\n` +
    `Return just the number.`,
    { label: 'count-new-files', phase: 'Verify' }
  ),
  // Чи залишились старі дублі?
  async () => agent(
    `Run in E:/develop/courses:\n` +
    `git ls-files embedded/ | grep -cE "(math-boolean|math-gauss|math-clt|comp-mlcc|comp-tvs|comp-tp4056)" || echo "0"\n\n` +
    `Return the count. Should be 0 if cleanup succeeded.`,
    { label: 'check-old-dupes', phase: 'Verify' }
  ),
  // Чи немає в manifest.js старих math-X.md / comp-X.md що перенесені?
  async () => agent(
    `Run in E:/develop/courses:\n` +
    `grep -cE '"math-boolean-algebra\\.md"|"math-gauss\\.md"|"comp-mlcc\\.md"|"comp-tvs-esd\\.md"' manifest.js || echo "0"\n\n` +
    `Return count. Should be 0 after update.`,
    { label: 'check-manifest-stale', phase: 'Verify' }
  ),
])

log(`Нові файли у math/+components/ (git ls-files): ${verifyNew}`)
log(`Старі дублі що лишились у embedded/ (зразок): ${verifyOld}`)
log(`Застарілих записів у manifest.js (зразок): ${verifyManifest}`)

return {
  gitRmBatches: rmResults.filter(Boolean).length,
  manifestUpdated: true,
  newFilesCount: verifyNew,
  oldDupesRemaining: verifyOld,
  staleManifestEntries: verifyManifest,
}
