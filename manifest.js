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
        { n: 7,  status: "pending", title: "Конденсатор" },
        { n: 8,  status: "pending", title: "Котушка та індуктивність" },
        { n: 9,  status: "pending", title: "Реактивність, фази й резонанс" },
        { n: 10, status: "pending", title: "Діод і PN-перехід" },
        { n: 11, status: "pending", title: "Біполярний транзистор (BJT)" },
        { n: 12, status: "pending", title: "Польовий транзистор (MOSFET)" },
        { n: 13, status: "pending", title: "Операційний підсилювач і компаратор" }
      ]
    },
    {
      n: 3,
      title: "Цифрова електроніка й процесор",
      slug: "block-3-digital-processor",
      chapters: [
        { n: 14, status: "pending", title: "Логічні рівні: від аналога до цифри" },
        { n: 15, status: "pending", title: "Логічні вентилі й комбінаційні схеми" },
        { n: 16, status: "pending", title: "Тригери, регістри й тактування" },
        { n: 17, status: "pending", title: "Представлення чисел" },
        { n: 18, status: "pending", title: "Архітектура процесора" },
        { n: 19, status: "pending", title: "Пам'ять, адресація, стек і купа" }
      ]
    },
    {
      n: 4,
      title: "Мікроконтролер і прошивка: ESP32",
      slug: "block-4-mcu-esp32",
      chapters: [
        { n: 20, status: "pending", title: "Анатомія мікроконтролера й архітектура ESP32" },
        { n: 21, status: "pending", title: "Тулчейн: як код стає прошивкою" },
        { n: 22, status: "pending", title: "GPIO глибоко" },
        { n: 23, status: "pending", title: "Переривання" },
        { n: 24, status: "pending", title: "Таймери й керування часом" },
        { n: 25, status: "pending", title: "PWM і ЦАП" },
        { n: 26, status: "pending", title: "Аналого-цифрове перетворення (АЦП)" },
        { n: 27, status: "pending", title: "Модель виконання й RTOS" }
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
        { n: 43, status: "pending", title: "Архітектура автономної системи й політний контролер" },
        { n: 44, status: "pending", title: "Компоненти польотної системи" },
        { n: 45, status: "pending", title: "Живлення складних систем" },
        { n: 46, status: "pending", title: "Оцінювання стану й сенсорний фьюжн" },
        { n: 47, status: "pending", title: "Відеосигнали I: від світла до кадру" },
        { n: 48, status: "pending", title: "Відеосигнали II: стиснення й передача" },
        { n: 49, status: "pending", title: "Машинне бачення: основи" },
        { n: 50, status: "pending", title: "Машинне навчання й нейромережі на пристрої" }
      ]
    }
  ]
};
