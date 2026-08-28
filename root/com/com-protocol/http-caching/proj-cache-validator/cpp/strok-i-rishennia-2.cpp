enum class Act {
    Serve,            // віддати збережене; мережі не буде взагалі
    ServeStaleAsync,  // віддати збережене, валідацію запустити у фоні
    Validate,         // умовний запит; його результат вирішить долю запису
    Fetch             // придатної копії немає — повний запит
};

Act decide(const Entry& e, const CacheControl& req, Steady::time_point now, bool shared) {
    // ПЕРЕД строком: no-cache вимикає свіжість цілком, хоч би що казав max-age
    if (e.cc.no_cache || req.no_cache) return Act::Validate;

    const Secs age  = current_age(e, now);
    const auto expl = explicit_lifetime(e, shared);
    const Secs life = expl ? *expl : heuristic_lifetime(e);

    // клієнт має право звузити свіжість: саме це шле браузер після «оновити»
    if (req.max_age && age >= Secs(*req.max_age)) return Act::Validate;

    if (age < life) {
        if (req.min_fresh && (life - age) < Secs(*req.min_fresh)) return Act::Validate;
        return Act::Serve;
    }

    const Secs over = age - life;                   // на скільки прострочено
    // must-revalidate забороняє прострочене беззастережно — і клієнтський дозвіл,
    // і серверний stale-while-revalidate після нього вже не діють
    if (e.cc.must_revalidate || (shared && e.cc.proxy_revalidate)) return Act::Validate;

    if (req.max_stale_any || (req.max_stale && over <= Secs(*req.max_stale)))
        return Act::Serve;                          // прострочене дозволив КЛІЄНТ
    if (e.cc.swr && over <= Secs(*e.cc.swr))
        return Act::ServeStaleAsync;                // прострочене дозволив СЕРВЕР

    return Act::Validate;
}
