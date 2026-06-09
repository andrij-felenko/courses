/* ──────────────────────────────────────────────────────────────────────────
   manifest.js — структура книги (повна мапа курсу)
   Єдине джерело правди для навігації. Редагується вручну.

   Як додати новий готовий розділ:
     1) знайди його в потрібному модулі нижче;
     2) додай йому поля: dir, main, histories і постав status:'done'.
        • dir       — шлях до папки розділу ВІД embedded/ (тобто з block-…);
                      префікс embedded/ додає basePath нижче
        • main      — головний .md розділу (теми)
        • histories — історичні вставки В ПОРЯДКУ ЧИТАННЯ (спершу історія
                      до розділу, далі — історії до тем). Заголовки тягнуться
                      з самих файлів автоматично, тож тут лише імена.
     Усе інше (сайдбар, якорі, перехресні лінки) збереться саме.
   ────────────────────────────────────────────────────────────────────────── */
window.BOOK = {
  title: "Вбудована електроніка й автономні системи",
  subtitle: "Глибокий курс — від заряду в атомі до машинного бачення на борту. " +
            "Сім модулів, п'ятдесят розділів, побудованих від першопричин.",
  // короткий підпис у шапці сайдбару
  shortTitle: "Вбудована електроніка",

  // Префікс до контенту відносно index.html. Обгортка лежить у корені репо,
  // а самі .md/.svg — у embedded/. Так Pages «from root» і локальний сервер
  // у корені працюють однаково. Хочеш покласти обгортку в /docs поряд із
  // контентом — постав "" і перемісти embedded/ туди.
  basePath: "embedded/",

  modules: [
    {
      n: 1,
      title: "Фізика електрики й кіл",
      slug: "block-1-circuits-physics",
      chapters: [
        {
          n: 1, status: "done",
          title: "Заряд, електричне поле й потенціал",
          dir: "block-1-circuits-physics/ch01-charge-field-potential",
          main: "ch01-charge-field-potential.md",
          histories: [
            "history-electricity.md",
            "ch01-s2-history-coulomb.md",
            "ch01-s3-history-faraday.md",
            "ch01-s5-history-volta.md"
          ]
        },
        {
          n: 2, status: "done",
          title: "Напруга, струм і провідність",
          dir: "block-1-circuits-physics/ch02-voltage-current-conduction",
          main: "ch02-voltage-current-conduction.md",
          histories: [
            "ch02-history-conduction.md",
            "ch02-s11-history-arrhenius.md",
            "ch02-s12-history-war-of-currents.md"
          ]
        },
        {
          n: 3, status: "done",
          title: "Опір, потужність і тепло",
          dir: "block-1-circuits-physics/ch03-resistance-power-heat",
          main: "ch03-resistance-power-heat.md",
          histories: [
            "ch03-history-ohm-joule.md",
            "ch03-s4-history-superconductivity.md",
            "ch03-s5-history-watt.md"
          ]
        },
        {
          n: 4, status: "done",
          title: "Закони Кірхгофа й аналіз кіл",
          dir: "block-1-circuits-physics/ch04-kirchhoff-circuit-analysis",
          main: "ch04-kirchhoff-circuit-analysis.md",
          histories: [
            "ch04-history-kirchhoff.md",
            "ch04-s1-history-euler-graphs.md"
          ]
        },
        {
          n: 5, status: "done",
          title: "Еквівалентні схеми: Тевенін, Нортон, суперпозиція",
          dir: "block-1-circuits-physics/ch05-equivalent-circuits",
          main: "ch05-equivalent-circuits.md",
          histories: [
            "ch05-history-thevenin-norton.md"
          ]
        },
        {
          n: 6, status: "done",
          title: "Мова схем і вимірювання",
          dir: "block-1-circuits-physics/ch06-schematics-measurement",
          main: "ch06-schematics-measurement.md",
          histories: [
            "ch06-history-instruments.md",
            "ch06-s6-history-weston.md",
            "ch06-s7-history-crt.md"
          ]
        }
      ]
    },
    {
      n: 2,
      title: "Компоненти й аналогова електроніка",
      slug: "block-2-components-analog",
      chapters: [
        { n: 7, status: "done", title: "Конденсатор",
          dir: "block-2-components-analog/ch07-capacitor", main: "ch07-capacitor.md",
          histories: ["ch07-history-leyden-jar.md"] },
        { n: 8, status: "done", title: "Котушка та індуктивність",
          dir: "block-2-components-analog/ch08-inductor", main: "ch08-inductor.md",
          histories: ["ch08-history-induction.md", "ch08-s6-history-transformer.md"] },
        { n: 9, status: "done", title: "Реактивність, фази й резонанс",
          dir: "block-2-components-analog/ch09-reactance-resonance", main: "ch09-reactance-resonance.md",
          histories: ["ch09-history-tuned-circuit.md"] },
        { n: 10, status: "done", title: "Діод і PN-перехід",
          dir: "block-2-components-analog/ch10-diode-pn-junction", main: "ch10-diode-pn-junction.md",
          histories: ["ch10-history-diode.md", "ch10-s7-history-led.md", "ch10-s8-history-zener.md"] },
        { n: 11, status: "done", title: "Біполярний транзистор (BJT)",
          dir: "block-2-components-analog/ch11-bjt", main: "ch11-bjt.md",
          histories: ["ch11-history-transistor.md"] },
        { n: 12, status: "done", title: "Польовий транзистор (MOSFET)",
          dir: "block-2-components-analog/ch12-mosfet", main: "ch12-mosfet.md",
          histories: ["ch12-history-mosfet.md", "ch12-s9-history-cmos.md"] },
        { n: 13, status: "done", title: "Операційний підсилювач і компаратор",
          dir: "block-2-components-analog/ch13-opamp-comparator", main: "ch13-opamp-comparator.md",
          histories: ["ch13-history-opamp.md"] }
      ]
    },
    {
      n: 3,
      title: "Цифрова електроніка й процесор",
      slug: "block-3-digital-processor",
      chapters: [
        { n: 14, status: "done", title: "Логічні рівні: від аналога до цифри",
          dir: "block-3-digital-processor/ch14-logic-levels", main: "ch14-logic-levels.md",
          histories: ["ch14-history-shannon.md"] },
        { n: 15, status: "done", title: "Логічні вентилі й комбінаційні схеми",
          dir: "block-3-digital-processor/ch15-logic-gates", main: "ch15-logic-gates.md",
          histories: ["ch15-history-boole.md"] },
        { n: 16, status: "done", title: "Тригери, регістри й тактування",
          dir: "block-3-digital-processor/ch16-flip-flops-registers", main: "ch16-flip-flops-registers.md",
          histories: ["ch16-history-flip-flop.md"] },
        { n: 17, status: "done", title: "Представлення чисел",
          dir: "block-3-digital-processor/ch17-number-representation", main: "ch17-number-representation.md",
          histories: ["ch17-history-leibniz.md", "ch17-s6-history-ieee754.md"] },
        { n: 18, status: "done", title: "Архітектура процесора",
          dir: "block-3-digital-processor/ch18-processor-architecture", main: "ch18-processor-architecture.md",
          histories: ["ch18-history-von-neumann.md", "ch18-s1-history-babbage-lovelace.md"] },
        { n: 19, status: "done", title: "Пам'ять, адресація, стек і купа",
          dir: "block-3-digital-processor/ch19-memory-stack-heap", main: "ch19-memory-stack-heap.md",
          histories: ["ch19-history-core-memory.md"] }
      ]
    },
    {
      n: 4,
      title: "Мікроконтролер і прошивка: ESP32",
      slug: "block-4-mcu-esp32",
      chapters: [
        { n: 20, status: "done", title: "Анатомія мікроконтролера й архітектура ESP32",
          dir: "block-4-mcu-esp32/ch20-mcu-esp32", main: "ch20-mcu-esp32.md",
          histories: ["ch20-history-first-mcu.md", "ch20-s5-history-esp.md"] },
        { n: 21, status: "done", title: "Тулчейн: як код стає прошивкою",
          dir: "block-4-mcu-esp32/ch21-toolchain", main: "ch21-toolchain.md",
          histories: ["ch21-history-grace-hopper.md"] },
        { n: 22, status: "done", title: "GPIO глибоко",
          dir: "block-4-mcu-esp32/ch22-gpio", main: "ch22-gpio.md",
          histories: [] },
        { n: 23, status: "done", title: "Переривання",
          dir: "block-4-mcu-esp32/ch23-interrupts", main: "ch23-interrupts.md",
          histories: ["ch23-history-interrupt.md"] },
        { n: 24, status: "done", title: "Таймери й керування часом",
          dir: "block-4-mcu-esp32/ch24-timers", main: "ch24-timers.md",
          histories: ["ch24-history-quartz.md"] },
        { n: 25, status: "done", title: "PWM і ЦАП",
          dir: "block-4-mcu-esp32/ch25-pwm-dac", main: "ch25-pwm-dac.md",
          histories: [] },
        { n: 26, status: "done", title: "Аналого-цифрове перетворення (АЦП)",
          dir: "block-4-mcu-esp32/ch26-adc", main: "ch26-adc.md",
          histories: ["ch26-history-sampling.md"] },
        { n: 27, status: "done", title: "Модель виконання й RTOS",
          dir: "block-4-mcu-esp32/ch27-execution-rtos", main: "ch27-execution-rtos.md",
          histories: ["ch27-history-time-sharing.md"] }
      ]
    },
    {
      n: 5,
      title: "Давачі, сигнали й керування",
      slug: "block-5-sensors-control",
      chapters: [
        { n: 28, status: "pending", title: "Фізика давачів" },
        { n: 29, status: "pending", title: "Вимірювання відстані й оточення" },
        { n: 30, status: "pending", title: "Цифрова фільтрація сигналів" },
        { n: 31, status: "pending", title: "Спектр і перетворення Фур'є" },
        { n: 32, status: "pending", title: "Цифрові фільтри в мікроконтролері" },
        { n: 33, status: "pending", title: "Інерціальні давачі: MEMS" },
        { n: 34, status: "pending", title: "Орієнтація й керування зі зворотним зв'язком (ПІД)" }
      ]
    },
    {
      n: 6,
      title: "Зв'язок: дротовий і радіо",
      slug: "block-6-comms-radio",
      chapters: [
        { n: 35, status: "pending", title: "UART і протоколи поверх нього" },
        { n: 36, status: "pending", title: "Шина I2C" },
        { n: 37, status: "pending", title: "Шина SPI" },
        { n: 38, status: "pending", title: "Бездротовий зв'язок на чіпі: Wi-Fi і Bluetooth" },
        { n: 39, status: "pending", title: "Радіо: фізика електромагнітних хвиль" },
        { n: 40, status: "pending", title: "Радіо: модуляція й бюджет лінії" },
        { n: 41, status: "pending", title: "Антени й лінії передачі" },
        { n: 42, status: "pending", title: "Радіозв'язок системи: керування, телеметрія, MAVLink" }
      ]
    },
    {
      n: 7,
      title: "Системи: ArduPilot, відео, машинне бачення",
      slug: "block-7-systems",
      chapters: [
        { n: 43, status: "done", title: "Архітектура автономної системи й політний контролер",
          dir: "block-7-systems/ch43-architecture-flight-controller", main: "ch43-architecture-flight-controller.md",
          histories: ["ch43-history-ardupilot.md"] },
        { n: 44, status: "done", title: "Компоненти польотної системи",
          dir: "block-7-systems/ch44-flight-components", main: "ch44-flight-components.md",
          histories: ["ch44-history-gps.md"] },
        { n: 45, status: "done", title: "Живлення складних систем",
          dir: "block-7-systems/ch45-power-systems", main: "ch45-power-systems.md",
          histories: ["ch45-history-lithium.md"] },
        { n: 46, status: "done", title: "Оцінювання стану й сенсорний фьюжн",
          dir: "block-7-systems/ch46-state-estimation-fusion", main: "ch46-state-estimation-fusion.md",
          histories: ["ch46-history-draper.md"] },
        { n: 47, status: "done", title: "Відеосигнали I: від світла до кадру",
          dir: "block-7-systems/ch47-video-signals-1", main: "ch47-video-signals-1.md",
          histories: ["ch47-history-farnsworth.md", "ch47-s2-history-ccd.md"] },
        { n: 48, status: "done", title: "Відеосигнали II: стиснення й передача",
          dir: "block-7-systems/ch48-video-signals-2", main: "ch48-video-signals-2.md",
          histories: ["ch48-history-dct.md"] },
        { n: 49, status: "done", title: "Машинне бачення: основи",
          dir: "block-7-systems/ch49-computer-vision", main: "ch49-computer-vision.md",
          histories: ["ch49-history-summer-vision.md", "ch49-s7-history-neural-nets.md"] },
        { n: 50, status: "done", title: "Машинне навчання й нейромережі на пристрої",
          dir: "block-7-systems/ch50-machine-learning", main: "ch50-machine-learning.md",
          histories: ["ch50-history-ai-winters.md", "ch50-s5-history-lecun-cnn.md"] }
      ]
    }
  ]
};
