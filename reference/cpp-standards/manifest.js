/* reference/cpp-standards/manifest.js — ДОВІДНИК «Стандарти C++» (тип "reference").
   Довідник — 4-й вид книги (AUTHORING §1): рукотворна система з версіями й релізами.
   Схема — як у book (§2 v6): sections[] → topics[], статус на КОЖНУ версію.

   МЕЖА З book/programming (§1): сюди йде те, до чого доречне питання «а в якій версії?» —
   механіка мови й стандартної бібліотеки. Загальні принципи (RAII як ідея, UB, ABI,
   порядок пам'яті, constexpr як поняття, корутини як модель) уже живуть у
   book/programming/languages та book/programming/systems — тут їх НЕ дублюємо, а лінкуємо.

   69 тем у 7 розділах. Усі заведено як detailed:pending (basic — за потреби, §3). */
(window.__BOOKS__ = window.__BOOKS__ || []).push({
  type: "reference", slug: "cpp-standards", title: "Стандарти C++",
  sections: [
    { slug: "language", title: "Механіка мови", scope: "Правила, за якими компілятор розуміє код: категорії значень, посилання, винятки, зв'язування.",
      topics: [
        { slug: "value-categories", title: "Категорії значень: lvalue, prvalue, xvalue", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "move-semantics", title: "Семантика переміщення і rvalue-посилання", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "rule-of-five-zero", title: "Правило п'яти й правило нуля", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "copy-elision", title: "Усунення копій і гарантований RVO", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "references-binding", title: "Посилання і правила зв'язування", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "perfect-forwarding", title: "Ідеальне передавання й універсальні посилання", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "const-correctness", title: "Коректність за const", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "auto-type-deduction", title: "auto й виведення типу", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "initialization-forms", title: "Форми ініціалізації та найприкріший розбір", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "lambdas-and-captures", title: "Лямбди й захоплення: що живе скільки", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "exceptions-mechanism", title: "Винятки: кидання, розкрутка стека, перехоплення", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "exception-safety-guarantees", title: "Гарантії безпеки винятків: базова, сильна, nothrow", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "noexcept", title: "noexcept: обіцянка й наслідки", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "odr-and-linkage", title: "Правило одного визначення й зв'язування імен", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "namespaces-and-adl", title: "Простори імен і пошук, залежний від аргументів", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "lifetime", title: "Об'єкти, володіння, пам'ять", scope: "Хто чим володіє, коли об'єкт живий і звідки береться пам'ять.",
      topics: [
        { slug: "object-lifetime", title: "Час життя об'єкта", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "unique-ptr", title: "unique_ptr: одноосібне володіння", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "shared-weak-ptr", title: "shared_ptr і weak_ptr: спільне володіння й розрив циклів", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "ownership-semantics", title: "Володіння в сигнатурі: що означає тип параметра", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "dangling-references", title: "Висячі посилання й звернення після звільнення", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "new-delete-allocation", title: "new, delete й шляхи виділення пам'яті", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "custom-allocators", title: "Власні алокатори й пам'ять під контролем", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "pimpl", title: "PIMPL: сховати реалізацію за вказівником", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "alignment-placement-new", title: "Вирівнювання й розміщувальний new", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "templates", title: "Шаблони й узагальнений код", scope: "Як з одного тексту постає багато типів — і скільки це коштує.",
      topics: [
        { slug: "templates-basics", title: "Шаблони: параметризація типом", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "template-argument-deduction", title: "Виведення аргументів шаблону", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "specialization-overload", title: "Спеціалізація й перевантаження шаблонів", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "variadic-and-folds", title: "Шаблони змінної арності й вирази згортки", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "sfinae-and-enable-if", title: "SFINAE й enable_if: відбір перевантажень", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "concepts-constraints", title: "Концепти й обмеження шаблонів", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "constexpr-if", title: "if constexpr: гілка, якої не існує", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "type-traits", title: "Риси типів (type traits)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "crtp", title: "CRTP: статичний поліморфізм", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "instantiation-cost", title: "Ціна інстанціювання: час компіляції й розмір бінарника", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "library", title: "Стандартна бібліотека", scope: "Що дає стандартна бібліотека і як вибір її засобу впливає на швидкодію.",
      topics: [
        { slug: "stl-containers-choice", title: "Контейнери STL: вибір під задачу і ціна операцій", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "iterators-model", title: "Ітератори: категорії й модель обходу", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "stl-algorithms", title: "Алгоритми STL замість ручних циклів", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "string-and-string-view", title: "string і string_view: володіти чи дивитися", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "span-contiguous", title: "span: невласницький вид на суцільні дані", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "optional", title: "optional: значення, якого може не бути", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "variant-and-visit", title: "variant і visit: одне з кількох", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "expected-error-handling", title: "expected: помилка як значення", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "std-function-type-erasure", title: "std::function і стирання типу: ціна колбека", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "chrono", title: "chrono: годинники, точки часу й тривалості", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "std-filesystem", title: "filesystem: шляхи й дії з файлами переносно", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "ranges-pipelines", title: "Ranges: конвеєри перетворень і ліниві види", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "format-and-print", title: "format і print: типобезпечне форматування", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "std-random", title: "random: рушії, розподіли й відтворюваність", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "concurrency", title: "Багатопотоковість у C++", scope: "Стандартні засоби паралельності: потоки, синхронізація, асинхронний результат.",
      topics: [
        { slug: "std-thread-jthread", title: "thread і jthread: запуск, приєднання, скасування", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "mutex-and-raii-locks", title: "М'ютекс і RAII-замки: lock_guard, unique_lock, scoped_lock", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "condition-variable", title: "Умовна змінна: чекати подію, а не крутитися", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "shared-mutex", title: "shared_mutex: багато читачів, один письменник", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "future-promise", title: "future й promise: результат з іншого потоку", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "async-and-packaged-task", title: "async і packaged_task: запуск із результатом", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "thread-local", title: "thread_local: стан, приватний для потоку", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "latch-barrier-semaphore", title: "latch, barrier і counting_semaphore", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "stop-token", title: "stop_token: кооперативне скасування", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "parallel-algorithms", title: "Політики виконання й паралельні алгоритми", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "releases", title: "Випуски стандарту", scope: "Що приніс кожен реліз мови й на що можна спиратися в конкретному проєкті.",
      topics: [
        { slug: "standardization-process", title: "Як робиться стандарт C++: комітет, папери, цикл", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "cpp11-cpp14", title: "C++11 і C++14: перелом", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "cpp17-features", title: "Що приніс C++17", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "cpp20-features", title: "Що приніс C++20", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "cpp23-features", title: "Що приніс C++23", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "compiler-support", title: "Підтримка стандартів компіляторами й прапорці", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "migrating-standards", title: "Перехід проєкту на новіший стандарт", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "practice", title: "Ремесло великого проєкту", scope: "Те, що болить саме у великій C++-базі: межі бінарників, заголовки, час збірки.",
      topics: [
        { slug: "abi-stability-cpp", title: "Стабільність ABI у C++ і що її ламає", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "header-hygiene", title: "Гігієна заголовків і час перезбірки", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "extern-c-interop", title: "extern \"C\" і сумісність із C-інтерфейсами", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "core-guidelines", title: "Core Guidelines: узгоджені правила стилю й безпеки", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
  ]
});
