enum class Outcome { Refreshed, Replaced, StaleOnError, PassThrough };

// RFC 9111 §3.2: оновлення заголовків збереженої відповіді
void update_stored_headers(Entry& e, const Fields& fresh) {
    for (const auto& [name, value] : fresh.all()) {
        if (name == "content-length") continue;   // §3.2 називає його прямим винятком
        if (is_hop_by_hop(name))       continue;  // Connection, TE, Upgrade, Keep-Alive…
        e.headers.set(name, value);
    }
}

Outcome absorb(Entry& e, const Response& up,
               Steady::time_point sent, Steady::time_point got, Wall::time_point got_wall) {
    if (up.status == 304) {
        const std::string* fresh_tag  = up.headers.find("etag");
        const std::string* stored_tag = e.headers.find("etag");
        if (fresh_tag && stored_tag && !weak_equal(*fresh_tag, *stored_tag))
            return Outcome::PassThrough;          // 304 не про НАШ варіант — не чіпаємо

        update_stored_headers(e, up.headers);
        e.date_value         = parse_http_date(value_of(up.headers, "date")).value_or(got_wall);
        e.response_time_wall = got_wall;
        e.response_time_mono = got;
        e.response_delay     = std::chrono::duration_cast<Secs>(got - sent);
        e.age_value          = Secs(delta_seconds(value_of(up.headers, "age")).value_or(0));
        e.cc                 = parse_cache_control(value_of(e.headers, "cache-control"));
        return Outcome::Refreshed;                // вік із нуля, тіло нікуди не їхало
    }

    if (up.status >= 500) {
        if (!e.cc.must_revalidate && e.cc.sie && staleness(e) <= Secs(*e.cc.sie))
            return Outcome::StaleOnError;
        return Outcome::PassThrough;              // запис лишається цілим і незайманим
    }

    return Outcome::Replaced;                     // 200 та інші — новий запис поверх старого
}
