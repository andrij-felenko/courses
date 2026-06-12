/* ──────────────────────────────────────────────────────────────────────────
   manifest-math.js — структура книги «Математика»
   Книга-довідник: пояснює математику курсу Фейнман-глибоко (ЧОМУ від першо-
   причини), а не констатує формули. Теми наповнюються ЗА ПЕРШИМ крос-лінком
   з інших книг (book:math/<slug>) — доти стоять стабами status:"pending"
   («в розробці»). Прозу математики пишемо Opus (див. embedded/AUTHORING.md).

   Модулі = великі розділи математики; «розділи» (chapters) = окремі теми,
   кожна у власній теці <slug>/ з головним <slug>.md. Коли тему написано —
   додай їй dir/main і постав status:"done" (як у manifest.js / manifest-chem.js).
   ────────────────────────────────────────────────────────────────────────── */
window.BOOK = {
  title: "Математика",
  subtitle: "Математика курсу — пояснена від першопричини: чому вектор розкладається " +
            "на незалежні складові, звідки |R|=√(Rx²+Ry²), чому інтеграл — це сума. " +
            "Наповнюється за посиланнями з інших книг.",
  shortTitle: "Математика",
  libraryHref: "index.html",
  basePath: "math/",

  modules: [
    {
      n: 1, title: "Лінійна алгебра", slug: "linear-algebra",
      chapters: [
        { n: "1", status: "pending", title: "Системи лінійних рівнянь: що означає «розв'язати»" },
        { n: "2", slug: "gauss-elimination", status: "done", dir: "gauss-elimination/", main: "gauss-elimination.md", title: "Метод Гаусса: виключення крок за кроком" },
        { n: "3", slug: "matrices-as-operations", status: "done", dir: "matrices-as-operations/", main: "matrices-as-operations.md", title: "Матриці як дії над векторами" },
        { n: "4", status: "pending", title: "Матриці повороту й звідки береться gimbal lock" },
        { n: "5", slug: "hamming-distance", status: "done", dir: "hamming-distance/", main: "hamming-distance.md", title: "Відстань Гемінга і коди з виправленням помилок" },
        { n: "6", slug: "crc-cyclic-redundancy", status: "done", dir: "crc-cyclic-redundancy/", main: "crc-cyclic-redundancy.md", title: "Циклічна надмірність: поліноми над GF(2)" }
      ]
    },
    {
      n: 2, title: "Вектор-аналіз і потік", slug: "vector-analysis",
      chapters: [
        { n: "1", slug: "vector-components", status: "done", dir: "vector-components/", main: "vector-components.md", title: "Вектор: чому величина розкладається на незалежні складові" },
        { n: "2", status: "pending", title: "Додавання векторів: правило паралелограма й |R|=√(Rx²+Ry²)" },
        { n: "3", slug: "gradient", status: "done", dir: "gradient/", main: "gradient.md", title: "Скалярний добуток як проєкція та «схожість»" },
        { n: "4", slug: "cross-product", status: "done", dir: "cross-product/", main: "cross-product.md", title: "Векторний добуток: момент сили і магнітна сила" },
        { n: "5", status: "pending", title: "Потік і дивергенція: скільки витікає з точки" },
        { n: "6", status: "pending", title: "Теорема Гаусса про потік: чому потік = заряд усередині" }
      ]
    },
    {
      n: 3, title: "Тригонометрія й фазори", slug: "trigonometry-phasors",
      chapters: [
        { n: "1", slug: "sine-cosine", status: "done", dir: "sine-cosine/", main: "sine-cosine.md", title: "Синус і косинус як проєкції обертання" },
        { n: "2", slug: "phasors", status: "done", dir: "phasors/", main: "phasors.md", title: "Фаза й зсув: дві синусоїди як один обертовий вектор" },
        { n: "3", slug: "complex-phasors", status: "done", dir: "complex-phasors/", main: "complex-phasors.md", title: "Фазори: чому комплексне число замінює тригонометрію" },
        { n: "4", status: "pending", title: "e^jωt і формула Ейлера: звідки береться обертання" },
        { n: "5", slug: "impedance", status: "done", dir: "impedance/", main: "impedance.md", title: "Імпеданс: узагальнений опір у комплексній площині" },
        { n: "6", slug: "power-triangle", status: "done", dir: "power-triangle/", main: "power-triangle.md", title: "Трикутник потужності: активна, реактивна, повна" },
        { n: "7", slug: "damping", status: "done", dir: "damping/", main: "damping.md", title: "Загасання коливань: від диференціального рівняння до Q" },
        { n: "8", slug: "q-factor", status: "done", dir: "q-factor/", main: "q-factor.md", title: "Добротність Q: енергія, вибірковість, смуга пропускання" }
      ]
    },
    {
      n: 4, title: "Похідні та інтеграли", slug: "calculus",
      chapters: [
        { n: "1", slug: "derivative", status: "done", dir: "derivative/", main: "derivative.md", title: "Похідна як миттєва швидкість зміни" },
        { n: "2", status: "pending", title: "Інтеграл як неперервна сума" },
        { n: "3", status: "pending", title: "Похідна й інтеграл для ПІД-регулятора" },
        { n: "4", status: "pending", title: "Згортка: математика FIR-фільтра" },
        { n: "5", slug: "derivative-max", status: "done", dir: "derivative-max/", main: "derivative-max.md", title: "Похідна для пошуку максимуму: екстремуми функцій" },
        { n: "6", slug: "derivative-cap", status: "done", dir: "derivative-cap/", main: "derivative-cap.md", title: "Похідна струму конденсатора: i = C·dV/dt" },
        { n: "7", slug: "exponential-ode", status: "done", dir: "exponential-ode/", main: "exponential-ode.md", title: "Експоненційний ОДУ: заряд конденсатора" },
        { n: "8", slug: "rl-ode", status: "done", dir: "rl-ode/", main: "rl-ode.md", title: "ОДУ RL-кола: наростання струму в індукторі" },
        { n: "9", slug: "rms-derivation", status: "done", dir: "rms-derivation/", main: "rms-derivation.md", title: "Виведення RMS: середньоквадратичне значення синусоїди" },
        { n: "10", slug: "sine-derivative", status: "done", dir: "sine-derivative/", main: "sine-derivative.md", title: "Похідна синуса: чому d/dt sin(ωt) = ω·cos(ωt)" },
        { n: "11", slug: "work-integral", status: "done", dir: "work-integral/", main: "work-integral.md", title: "Інтеграл роботи: робота у полі як лінійний інтеграл" },
        { n: "12", slug: "half-power", status: "done", dir: "half-power/", main: "half-power.md", title: "Точка -3 дБ: частота напівпотужності" },
        { n: "13", slug: "logarithms", status: "done", dir: "logarithms/", main: "logarithms.md", title: "Логарифми й децибели: шкала для широкого діапазону" },
        { n: "14", slug: "transfer-function", status: "done", dir: "transfer-function/", main: "transfer-function.md", title: "Передавальна функція: від ОДУ до H(jω)" },
        { n: "15", slug: "cascading", status: "done", dir: "cascading/", main: "cascading.md", title: "Каскадування фільтрів: множення передавальних функцій" },
        { n: "16", slug: "thomson-formula", status: "done", dir: "thomson-formula/", main: "thomson-formula.md", title: "Формула Томсона: резонансна частота LC-контуру" }
      ]
    },
    {
      n: 5, title: "Статистика й похибки", slug: "statistics-errors",
      chapters: [
        { n: "1", slug: "random-variables", status: "done", dir: "random-variables/", main: "random-variables.md", title: "Середнє й дисперсія: де живе «правда» в шумі" },
        { n: "2", slug: "central-limit", status: "done", dir: "central-limit/", main: "central-limit.md", title: "Центральна гранична теорема: чому шум гаусівський" },
        { n: "3", slug: "averaging", status: "done", dir: "averaging/", main: "averaging.md", title: "Чому усереднення дає виграш σ/√N" },
        { n: "4", slug: "kt-thermal", status: "done", dir: "kt-thermal/", main: "kt-thermal.md", title: "Теплові флуктуації: шкала kT і теплові шуми" },
        { n: "5", slug: "noise-density", status: "done", dir: "noise-density/", main: "noise-density.md", title: "Спектральна густина шуму: В/√Гц і А/√Гц" },
        { n: "6", slug: "accuracy", status: "done", dir: "accuracy/", main: "accuracy.md", title: "Точність і похибка: систематична, випадкова, повна" },
        { n: "7", slug: "tolerance", status: "done", dir: "tolerance/", main: "tolerance.md", title: "Допуски компонентів: від ±% до бюджету похибки" },
        { n: "8", status: "pending", title: "Метод найменших квадратів: калібрувальна пряма" },
        { n: "9", status: "pending", title: "Додавання похибок: RSS і бюджет похибки" },
        { n: "10", status: "pending", title: "Статистика Пуассона: чому рідкісні відліки «стрибають»" },
        { n: "11", slug: "ppm-math", status: "done", dir: "ppm-math/", main: "ppm-math.md", title: "PPM-математика: частини на мільйон і стабільність" },
        { n: "12", slug: "q-stability", status: "done", dir: "q-stability/", main: "q-stability.md", title: "Стабільність Q: температурна залежність резонатора" },
        { n: "13", slug: "derating", status: "done", dir: "derating/", main: "derating.md", title: "Деретинг: зниження навантаження для надійності" },
        { n: "14", slug: "thermal-resistance", status: "done", dir: "thermal-resistance/", main: "thermal-resistance.md", title: "Тепловий опір: від кристала до навколишнього середовища" }
      ]
    },
    {
      n: 6, title: "Дискретна математика й логіка", slug: "discrete-logic",
      chapters: [
        { n: "1", slug: "boolean-algebra", status: "done", dir: "boolean-algebra/", main: "boolean-algebra.md", title: "Булева алгебра: аксіоми, теореми, закони де Моргана" },
        { n: "2", slug: "karnaugh-maps", status: "done", dir: "karnaugh-maps/", main: "karnaugh-maps.md", title: "Карти Карно: мінімізація булевих функцій" },
        { n: "3", slug: "fsm-formal", status: "done", dir: "fsm-formal/", main: "fsm-formal.md", title: "Формальні автомати: стани, переходи, Мілі і Мур" },
        { n: "4", slug: "superposition", status: "done", dir: "superposition/", main: "superposition.md", title: "Суперпозиція і лінійність: принцип незалежності" },
        { n: "5", slug: "graph-theory", status: "done", dir: "graph-theory/", main: "graph-theory.md", title: "Теорія графів: вузли, ребра, обходи" }
      ]
    },
    {
      n: 7, title: "Системи числення", slug: "number-systems",
      chapters: [
        { n: "1", slug: "modular-arithmetic", status: "done", dir: "modular-arithmetic/", main: "modular-arithmetic.md", title: "Модульна арифметика: переповнення і двійковий доповнюючий код" },
        { n: "2", slug: "ieee754", status: "done", dir: "ieee754/", main: "ieee754.md", title: "IEEE 754: деталі формату числа з плаваючою комою" },
        { n: "3", slug: "address-space", status: "done", dir: "address-space/", main: "address-space.md", title: "Адресний простір: від байта до сегментів пам'яті" },
        { n: "4", slug: "si-prefixes", status: "done", dir: "si-prefixes/", main: "si-prefixes.md", title: "Префікси СІ: від пікo до гіга і далі" },
        { n: "5", slug: "dimensional-analysis", status: "done", dir: "dimensional-analysis/", main: "dimensional-analysis.md", title: "Розмірний аналіз: перевірка формул через одиниці" },
        { n: "6", slug: "e-series", status: "done", dir: "e-series/", main: "e-series.md", title: "Ряди E: стандартні номінали резисторів і конденсаторів" },
        { n: "7", slug: "energy-units", status: "done", dir: "energy-units/", main: "energy-units.md", title: "Одиниці енергії: джоулі, кіловат-години, електронвольти" }
      ]
    }
  ]
};
