bool heuristically_cacheable(int status) {          // RFC 9110 §9.1
    switch (status) {
        case 200: case 203: case 204: case 206: case 300:
        case 301: case 404: case 405: case 410: case 414: case 501: return true;
        default: return false;
    }
}

std::optional<Secs> explicit_lifetime(const Entry& e, bool shared) {
    if (shared && e.cc.s_maxage) return Secs(*e.cc.s_maxage);
    if (e.cc.max_age)            return Secs(*e.cc.max_age);
    if (const std::string* exp = e.headers.find("expires")) {
        const auto t = parse_http_date(*exp);
        // «0» і будь-яка нерозбірна дата означають «вже прострочено» (RFC 9111 §5.3)
        if (!t) return Secs(0);
        return std::max(Secs(0), std::chrono::duration_cast<Secs>(*t - e.date_value));
    }
    return std::nullopt;                            // явного строку немає
}

Secs heuristic_lifetime(const Entry& e) {
    if (!heuristically_cacheable(e.status)) return Secs(0);
    if (const std::string* lm = e.headers.find("last-modified")) {
        if (const auto t = parse_http_date(*lm)) {
            const Secs since = std::chrono::duration_cast<Secs>(e.date_value - *t);
            // 10 % від часу, що минув від зміни, — частка, яку RFC 9111 §4.2.2 називає
            // типовою; стеля в добу — уже наш власний запобіжник
            return std::clamp(since / 10, Secs(0), Secs(24 * 3600));
        }
    }
    return Secs(0);
}
