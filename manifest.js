/* ──────────────────────────────────────────────────────────────────────────
   manifest.js — структура книги (повна мапа курсу: 7 модулів · 60 розділів)
   Єдине джерело правди для навігації. Редагується вручну.

   Нумерація — М.Р.Т (модуль.розділ.тема): «4.3.2» = модуль 4, розділ 3,
   тема 2. n у розділі — номер РОЗДІЛУ ВСЕРЕДИНІ модуля (Р).

   Як додати новий готовий розділ:
     1) знайди його в потрібному модулі нижче;
     2) додай йому поля: dir, main, histories і постав status:'done'.
        • dir       — шлях до папки розділу ВІД embedded/ (тобто з block-…);
                      префікс embedded/ додає basePath нижче.
                      Старі папки звуться chNN-… (історичні наскрізні номери),
                      нові розділи — rРР-… (внутрімодульний номер Р)
        • main      — головний .md розділу (теми)
        • histories — історичні вставки В ПОРЯДКУ ЧИТАННЯ (спершу історія
                      до розділу, далі — історії до тем). Заголовки тягнуться
                      з самих файлів автоматично, тож тут лише імена.
     Усе інше (сайдбар, якорі, перехресні лінки) збереться саме.
   ────────────────────────────────────────────────────────────────────────── */
window.BOOK = {
  title: "Вбудована електроніка й автономні системи",
  subtitle: "Глибокий курс — від заряду в атомі до машинного бачення на борту. " +
            "Сім модулів, шістдесят розділів, побудованих від першопричин.",
  // короткий підпис у шапці сайдбару
  shortTitle: "Вбудована електроніка",

  // посилання «← Бібліотека» у сайдбарі (стартова сторінка зі списком книг)
  libraryHref: "index.html",

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
        },
        { n: 7, status: "pending", title: "Змінний струм: синусоїда, фаза й RMS" },
        { n: 8, status: "pending", title: "Магнетизм і електромагніти" },
        { n: 9, status: "pending", title: "Шум і завади: фізичні джерела" },
        { n: 10, status: "pending", title: "Електростатика на практиці: іскри, блискавка й ESD" }
      ]
    },
    {
      n: 2,
      title: "Компоненти й аналогова електроніка",
      slug: "block-2-components-analog",
      chapters: [
        { n: 1, status: "done", title: "Конденсатор",
          dir: "block-2-components-analog/ch07-capacitor", main: "ch07-capacitor.md",
          histories: ["ch07-history-leyden-jar.md"] },
        { n: 2, status: "done", title: "Котушка та індуктивність",
          dir: "block-2-components-analog/ch08-inductor", main: "ch08-inductor.md",
          histories: ["ch08-history-induction.md", "ch08-s6-history-transformer.md"] },
        { n: 3, status: "done", title: "Реактивність, фази й резонанс",
          dir: "block-2-components-analog/ch09-reactance-resonance", main: "ch09-reactance-resonance.md",
          histories: ["ch09-history-tuned-circuit.md"] },
        { n: 4, status: "pending", title: "АЧХ, децибели й фільтри" },
        { n: 5, status: "done", title: "Діод і PN-перехід",
          dir: "block-2-components-analog/ch10-diode-pn-junction", main: "ch10-diode-pn-junction.md",
          histories: ["ch10-history-diode.md", "ch10-s7-history-led.md", "ch10-s8-history-zener.md"] },
        { n: 6, status: "done", title: "Біполярний транзистор (BJT)",
          dir: "block-2-components-analog/ch11-bjt", main: "ch11-bjt.md",
          histories: ["ch11-history-transistor.md"] },
        { n: 7, status: "done", title: "Польовий транзистор (MOSFET)",
          dir: "block-2-components-analog/ch12-mosfet", main: "ch12-mosfet.md",
          histories: ["ch12-history-mosfet.md", "ch12-s9-history-cmos.md"] },
        { n: 8, status: "done", title: "Операційний підсилювач і компаратор",
          dir: "block-2-components-analog/ch13-opamp-comparator", main: "ch13-opamp-comparator.md",
          histories: ["ch13-history-opamp.md"] },
        { n: 9, status: "pending", title: "Як читати даташит" },
        { n: 10, status: "pending", title: "Резонатори й опорні частоти" },
        { n: 11, status: "pending", title: "Силова комутація змінного струму" },
        { n: 12, status: "pending", title: "Легендарні аналогові ІМС" }
      ]
    },
    {
      n: 3,
      title: "Цифрова електроніка й процесор",
      slug: "block-3-digital-processor",
      chapters: [
        { n: 1, status: "done", title: "Логічні рівні: від аналога до цифри",
          dir: "block-3-digital-processor/ch14-logic-levels", main: "ch14-logic-levels.md",
          histories: ["ch14-history-shannon.md"] },
        { n: 2, status: "done", title: "Логічні вентилі й комбінаційні схеми",
          dir: "block-3-digital-processor/ch15-logic-gates", main: "ch15-logic-gates.md",
          histories: ["ch15-history-boole.md"] },
        { n: 3, status: "done", title: "Тригери, регістри й тактування",
          dir: "block-3-digital-processor/ch16-flip-flops-registers", main: "ch16-flip-flops-registers.md",
          histories: ["ch16-history-flip-flop.md"] },
        { n: 4, status: "done", title: "Представлення чисел",
          dir: "block-3-digital-processor/ch17-number-representation", main: "ch17-number-representation.md",
          histories: ["ch17-history-leibniz.md", "ch17-s6-history-ieee754.md"] },
        { n: 5, status: "done", title: "Архітектура процесора",
          dir: "block-3-digital-processor/ch18-processor-architecture", main: "ch18-processor-architecture.md",
          histories: ["ch18-history-von-neumann.md", "ch18-s1-history-babbage-lovelace.md"] },
        { n: 6, status: "done", title: "Пам'ять, адресація, стек і купа",
          dir: "block-3-digital-processor/ch19-memory-stack-heap", main: "ch19-memory-stack-heap.md",
          histories: ["ch19-history-core-memory.md"] },
        { n: 7, status: "pending", title: "Програмована логіка: ПЛІС/FPGA" },
        { n: 8, status: "pending", title: "Зовнішня пам'ять" },
        { n: 9, status: "pending", title: "Коди виявлення й корекції помилок" },
        { n: 10, status: "pending", title: "Як народжується чіп: від піску до корпуса" }
      ]
    },
    {
      n: 4,
      title: "Мікроконтролер і прошивка: ESP32",
      slug: "block-4-mcu-esp32",
      chapters: [
        { n: 1, status: "done", title: "Анатомія мікроконтролера й архітектура ESP32",
          dir: "block-4-mcu-esp32/ch20-mcu-esp32", main: "ch20-mcu-esp32.md",
          histories: ["ch20-history-first-mcu.md", "ch20-s5-history-esp.md"] },
        { n: 2, status: "done", title: "Тулчейн: як код стає прошивкою",
          dir: "block-4-mcu-esp32/ch21-toolchain", main: "ch21-toolchain.md",
          histories: ["ch21-history-grace-hopper.md"] },
        { n: 3, status: "pending", title: "Постійні дані: Flash-розділи, NVS і файлові системи" },
        { n: 4, status: "done", title: "GPIO глибоко",
          dir: "block-4-mcu-esp32/ch22-gpio", main: "ch22-gpio.md",
          histories: [] },
        { n: 5, status: "done", title: "Переривання",
          dir: "block-4-mcu-esp32/ch23-interrupts", main: "ch23-interrupts.md",
          histories: ["ch23-history-interrupt.md"] },
        { n: 6, status: "done", title: "Таймери й керування часом",
          dir: "block-4-mcu-esp32/ch24-timers", main: "ch24-timers.md",
          histories: ["ch24-history-quartz.md"] },
        { n: 7, status: "done", title: "PWM і ЦАП",
          dir: "block-4-mcu-esp32/ch25-pwm-dac", main: "ch25-pwm-dac.md",
          histories: [] },
        { n: 8, status: "done", title: "Аналого-цифрове перетворення (АЦП)",
          dir: "block-4-mcu-esp32/ch26-adc", main: "ch26-adc.md",
          histories: ["ch26-history-sampling.md"] },
        { n: 9, status: "pending", title: "DMA: дані без участі ядра" },
        { n: 10, status: "done", title: "Модель виконання й RTOS",
          dir: "block-4-mcu-esp32/ch27-execution-rtos", main: "ch27-execution-rtos.md",
          histories: ["ch27-history-time-sharing.md"] },
        { n: 11, status: "pending", title: "Пейзаж мікроконтролерів" },
        { n: 12, status: "pending", title: "USB на мікроконтролері" },
        { n: 13, status: "pending", title: "Енергоощадність глибоко" }
      ]
    },
    {
      n: 5,
      title: "Давачі, сигнали й керування",
      slug: "block-5-sensors-control",
      chapters: [
        { n: 1, status: "done", title: "Фізика давачів",
          dir: "block-5-sensors-control/ch28-sensor-physics", main: "ch28-sensor-physics.md",
          histories: ["ch28-history-seebeck.md"] },
        { n: 2, status: "done", title: "Вимірювання відстані й оточення",
          dir: "block-5-sensors-control/ch29-distance-environment", main: "ch29-distance-environment.md",
          histories: ["ch29-history-sonar.md"] },
        { n: 3, status: "pending", title: "Давачі обертання й положення: енкодери" },
        { n: 4, status: "done", title: "Цифрова фільтрація сигналів",
          dir: "block-5-sensors-control/ch30-digital-filtering", main: "ch30-digital-filtering.md",
          histories: [] },
        { n: 5, status: "done", title: "Спектр і перетворення Фур'є",
          dir: "block-5-sensors-control/ch31-spectrum-fourier", main: "ch31-spectrum-fourier.md",
          histories: ["ch31-history-fourier.md", "ch31-s5-history-fft.md"] },
        { n: 6, status: "done", title: "Цифрові фільтри в мікроконтролері",
          dir: "block-5-sensors-control/ch32-digital-filters-mcu", main: "ch32-digital-filters-mcu.md",
          histories: [] },
        { n: 7, status: "done", title: "Інерціальні давачі: MEMS",
          dir: "block-5-sensors-control/ch33-imu-mems", main: "ch33-imu-mems.md",
          histories: ["ch33-history-mems-airbag.md"] },
        { n: 8, status: "done", title: "Орієнтація й керування зі зворотним зв'язком (ПІД)",
          dir: "block-5-sensors-control/ch34-orientation-pid", main: "ch34-orientation-pid.md",
          histories: ["ch34-history-governor-pid.md", "ch34-s4-history-kalman.md"] },
        { n: 9, status: "pending", title: "Виконавчі механізми: мотори й рух" },
        { n: 10, status: "pending", title: "Давачі середовища глибше" },
        { n: 11, status: "pending", title: "Час і синхронізація вимірювань" }
      ]
    },
    {
      n: 6,
      title: "Зв'язок: дротовий і радіо",
      slug: "block-6-comms-radio",
      chapters: [
        { n: 1, status: "done", title: "UART і протоколи поверх нього",
          dir: "block-6-comms-radio/ch35-uart", main: "ch35-uart.md",
          histories: ["ch35-history-baudot.md"] },
        { n: 2, status: "done", title: "Шина I2C",
          dir: "block-6-comms-radio/ch36-i2c", main: "ch36-i2c.md",
          histories: ["ch36-history-i2c.md"] },
        { n: 3, status: "done", title: "Шина SPI",
          dir: "block-6-comms-radio/ch37-spi", main: "ch37-spi.md",
          histories: [] },
        { n: 4, status: "pending", title: "Диференційні шини: RS-485 і CAN" },
        { n: 5, status: "done", title: "Бездротовий зв'язок на чіпі: Wi-Fi і Bluetooth",
          dir: "block-6-comms-radio/ch38-wifi-bluetooth", main: "ch38-wifi-bluetooth.md",
          histories: ["ch38-history-bluetooth-name.md"] },
        { n: 6, status: "done", title: "Радіо: фізика електромагнітних хвиль",
          dir: "block-6-comms-radio/ch39-radio-em-waves", main: "ch39-radio-em-waves.md",
          histories: ["ch39-history-hertz.md"] },
        { n: 7, status: "done", title: "Радіо: модуляція й бюджет лінії",
          dir: "block-6-comms-radio/ch40-modulation-link-budget", main: "ch40-modulation-link-budget.md",
          histories: ["ch40-history-armstrong.md", "ch40-s5-history-hedy-lamarr.md"] },
        { n: 8, status: "done", title: "Антени й лінії передачі",
          dir: "block-6-comms-radio/ch41-antennas", main: "ch41-antennas.md",
          histories: ["ch41-history-marconi.md"] },
        { n: 9, status: "done", title: "Радіозв'язок системи: керування, телеметрія, MAVLink",
          dir: "block-6-comms-radio/ch42-telemetry-mavlink", main: "ch42-telemetry-mavlink.md",
          histories: ["ch42-history-mavlink.md"] },
        { n: 10, status: "pending", title: "Мережі: Ethernet, IP і як пакет знаходить дорогу" },
        { n: 11, status: "pending", title: "MAVLink у роботі: словник даних і керування" },
        { n: 12, status: "pending", title: "Приєднання модулів: розпіновки, рівні, конектори, надійність" }
      ]
    },
    {
      n: 7,
      title: "Системи: ArduPilot, відео, машинне бачення",
      slug: "block-7-systems",
      chapters: [
        { n: 1, status: "done", title: "Архітектура автономної системи й політний контролер",
          dir: "block-7-systems/ch43-architecture-flight-controller", main: "ch43-architecture-flight-controller.md",
          histories: ["ch43-history-ardupilot.md"] },
        { n: 2, status: "pending", title: "Як літає мультиротор" },
        { n: 3, status: "done", title: "Компоненти польотної системи",
          dir: "block-7-systems/ch44-flight-components", main: "ch44-flight-components.md",
          histories: ["ch44-history-gps.md"] },
        { n: 4, status: "done", title: "Живлення складних систем",
          dir: "block-7-systems/ch45-power-systems", main: "ch45-power-systems.md",
          histories: ["ch45-history-lithium.md"] },
        { n: 5, status: "done", title: "Оцінювання стану й сенсорний фьюжн",
          dir: "block-7-systems/ch46-state-estimation-fusion", main: "ch46-state-estimation-fusion.md",
          histories: ["ch46-history-draper.md"] },
        { n: 6, status: "pending", title: "Польотні режими, місії та failsafe" },
        { n: 7, status: "done", title: "Відеосигнали I: від світла до кадру",
          dir: "block-7-systems/ch47-video-signals-1", main: "ch47-video-signals-1.md",
          histories: ["ch47-history-farnsworth.md", "ch47-s2-history-ccd.md"] },
        { n: 8, status: "done", title: "Відеосигнали II: стиснення й передача",
          dir: "block-7-systems/ch48-video-signals-2", main: "ch48-video-signals-2.md",
          histories: ["ch48-history-dct.md"] },
        { n: 9, status: "done", title: "Машинне бачення: основи",
          dir: "block-7-systems/ch49-computer-vision", main: "ch49-computer-vision.md",
          histories: ["ch49-history-summer-vision.md", "ch49-s7-history-neural-nets.md"] },
        { n: 10, status: "done", title: "Машинне навчання й нейромережі на пристрої",
          dir: "block-7-systems/ch50-machine-learning", main: "ch50-machine-learning.md",
          histories: ["ch50-history-ai-winters.md", "ch50-s5-history-lecun-cnn.md"] },
        { n: 11, status: "pending", title: "Бортовий комп'ютер: «політ» + «розум» разом" },
        { n: 12, status: "pending", title: "Інші автономні платформи: ровер, човен, літак" },
        { n: 13, status: "pending", title: "Наземна станція й оператор" }
      ]
    },
    {
      n: 8,
      title: "Схемотехніка власних плат",
      slug: "block-8-circuit-design",
      chapters: [
        { n: 1, status: "pending", title: "Від ідеї до структурної схеми" },
        { n: 2, status: "pending", title: "Вибір компонентів і розрахунок обв'язки" },
        { n: 3, status: "pending", title: "Вузол живлення на схемі" },
        { n: 4, status: "pending", title: "Скидання, тактування, прошивання: обв'язка мікроконтролера" },
        { n: 5, status: "pending", title: "Інтерфейси назовні й захист виводів" },
        { n: 6, status: "pending", title: "SPICE: схема в симуляторі" },
        { n: 7, status: "pending", title: "САПР: бібліотеки, символи, нетліст" },
        { n: 8, status: "pending", title: "Рев'ю схеми і підготовка до розведення" }
      ]
    },
    {
      n: 9,
      title: "Плати фізично: розведення, виготовлення, монтаж",
      slug: "block-9-pcb-layout-assembly",
      chapters: [
        { n: 1, status: "pending", title: "Плата зсередини: шари, стек, матеріали" },
        { n: 2, status: "pending", title: "Трасування сигналів" },
        { n: 3, status: "pending", title: "Земля, полігони і EMI плати" },
        { n: 4, status: "pending", title: "DFM і DFT: спроєктовано для фабрики" },
        { n: 5, status: "pending", title: "Замовлення: файли, фабрика, компоненти" },
        { n: 6, status: "pending", title: "Паяння і монтаж" },
        { n: 7, status: "pending", title: "Бріг-ап нової плати" },
        { n: 8, status: "pending", title: "Ревізії і життя плати" }
      ]
    },
    {
      n: 10,
      title: "Живлення і енергія",
      slug: "block-10-power-energy",
      chapters: [
        { n: 1, status: "pending", title: "Топології перетворювачів" },
        { n: 2, status: "pending", title: "Спроєктувати і виміряти перетворювач" },
        { n: 3, status: "pending", title: "USB-живлення і розумна зарядка" },
        { n: 4, status: "pending", title: "Батареї і заряд" },
        { n: 5, status: "pending", title: "Сонячна енергія і MPPT" },
        { n: 6, status: "pending", title: "Енергоощадна архітектура" },
        { n: 7, status: "pending", title: "Захисти живлення" }
      ]
    },
    {
      n: 11,
      title: "Автономія і робототехніка",
      slug: "block-11-autonomy-robotics",
      chapters: [
        { n: 1, status: "pending", title: "Бортовий Linux і одноплатники" },
        { n: 2, status: "pending", title: "ROS2: нервова система робота" },
        { n: 3, status: "pending", title: "Сприйняття: лідар, камера, карта" },
        { n: 4, status: "pending", title: "Локалізація і ймовірність" },
        { n: 5, status: "pending", title: "Планування шляху" },
        { n: 6, status: "pending", title: "Локальне керування і обхід перешкод" },
        { n: 7, status: "pending", title: "Платформи: ровер, маніпулятор, коптер" },
        { n: 8, status: "pending", title: "Симуляція робота" }
      ]
    },
    {
      n: 12,
      title: "Глибокий ШІ на краю",
      slug: "block-12-edge-ai",
      chapters: [
        { n: 1, status: "pending", title: "Навчання по-справжньому: бекпроп і оптимізатори" },
        { n: 2, status: "pending", title: "Від CNN до трансформерів" },
        { n: 3, status: "pending", title: "Дані і розмітка" },
        { n: 4, status: "pending", title: "Стиснення моделей: квантування, прунінг, дистиляція" },
        { n: 5, status: "pending", title: "NPU і акселератори" },
        { n: 6, status: "pending", title: "MLOps парку пристроїв" },
        { n: 7, status: "pending", title: "Надійність ML на краю" }
      ]
    },
    {
      n: 13,
      title: "UI та HMI на залізі",
      slug: "block-13-ui-hmi",
      chapters: [
        { n: 1, status: "pending", title: "Дисплеї і дотик як компоненти" },
        { n: 2, status: "pending", title: "Графічний конвеєр" },
        { n: 3, status: "pending", title: "Архітектура UI-застосунку" },
        { n: 4, status: "pending", title: "Qt: від десктопа до MCU" },
        { n: 5, status: "pending", title: "LVGL і TouchGFX" },
        { n: 6, status: "pending", title: "Slint, Embedded Wizard і вибір фреймворку" },
        { n: 7, status: "pending", title: "Практичні патерни UI на залізі" }
      ]
    },
    {
      n: 14,
      title: "Продукт: від прототипа до серії",
      slug: "block-14-product",
      chapters: [
        { n: 1, status: "pending", title: "Вимоги і архітектура виробу" },
        { n: 2, status: "pending", title: "DFM і вартість BOM" },
        { n: 3, status: "pending", title: "EMC і сертифікація" },
        { n: 4, status: "pending", title: "Тестування: від юнітів до HIL і фабрики" },
        { n: 5, status: "pending", title: "Надійність і аналіз відмов" },
        { n: 6, status: "pending", title: "OTA-флот і версіонування" },
        { n: 7, status: "pending", title: "Безпека продукту" },
        { n: 8, status: "pending", title: "Документація, постачання, підтримка" },
        { n: 9, status: "pending", title: "Пристрій в екосистемі: стільниковий IoT, Matter і хмара" }
      ]
    }
  ]
};
