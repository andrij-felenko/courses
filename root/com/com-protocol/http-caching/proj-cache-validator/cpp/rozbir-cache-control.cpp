#include <algorithm>
#include <chrono>
#include <optional>
#include <string>
#include <string_view>

using Wall   = std::chrono::system_clock;   // стінний час: лише для Date / Expires
using Steady = std::chrono::steady_clock;   // монотонний: лише для тривалостей
using Secs   = std::chrono::seconds;

struct CacheControl {
    bool no_store = false, no_cache = false, must_revalidate = false;
    bool proxy_revalidate = false, is_private = false, is_public = false;
    bool only_if_cached = false, max_stale_any = false;
    std::optional<long> max_age, s_maxage, min_fresh, max_stale, swr, sie;
};

// delta-seconds: самі цифри. Переповнення — не помилка розбору, а 2³¹ (RFC 9111 §1.2.2)
static std::optional<long> delta_seconds(std::string_view s) {
    if (s.empty()) return std::nullopt;
    long n = 0;
    for (char c : s) {
        if (c < '0' || c > '9') return std::nullopt;
        if (n > (2147483648L - (c - '0')) / 10) return 2147483648L;
        n = n * 10 + (c - '0');
    }
    return n;
}

static std::string_view trim(std::string_view s) {
    while (!s.empty() && (s.front() == ' ' || s.front() == '\t')) s.remove_prefix(1);
    while (!s.empty() && (s.back()  == ' ' || s.back()  == '\t')) s.remove_suffix(1);
    return s;
}

static bool ieq(std::string_view a, std::string_view b) {      // без огляду на регістр
    return a.size() == b.size() &&
           std::equal(a.begin(), a.end(), b.begin(),
                      [](char x, char y) { return (x | 0x20) == (y | 0x20); });
}

CacheControl parse_cache_control(std::string_view v) {
    CacheControl cc;
    size_t i = 0;
    while (i < v.size()) {
        while (i < v.size() && (v[i] == ',' || v[i] == ' ' || v[i] == '\t')) ++i;

        size_t nb = i;
        while (i < v.size() && v[i] != '=' && v[i] != ',') ++i;
        const std::string_view name = trim(v.substr(nb, i - nb));

        std::string_view val;
        if (i < v.size() && v[i] == '=') {
            ++i;
            if (i < v.size() && v[i] == '"') {                 // quoted-string
                const size_t vb = ++i;
                while (i < v.size() && v[i] != '"') i += (v[i] == '\\' ? 2 : 1);
                val = v.substr(vb, i - vb);
                if (i < v.size()) ++i;                         // закривальна лапка
            } else {
                const size_t vb = i;
                while (i < v.size() && v[i] != ',') ++i;
                val = trim(v.substr(vb, i - vb));
            }
        }
        if (name.empty()) continue;

        if      (ieq(name, "no-store"))         cc.no_store         = true;
        // кваліфіковану форму no-cache="…" трактуємо як звичайний no-cache:
        // суворіше за дозволене, а суворіше кешу завжди можна
        else if (ieq(name, "no-cache"))         cc.no_cache         = true;
        else if (ieq(name, "must-revalidate"))  cc.must_revalidate  = true;
        else if (ieq(name, "proxy-revalidate")) cc.proxy_revalidate = true;
        else if (ieq(name, "private"))          cc.is_private       = true;
        else if (ieq(name, "public"))           cc.is_public        = true;
        else if (ieq(name, "only-if-cached"))   cc.only_if_cached   = true;
        else if (ieq(name, "max-age"))          cc.max_age   = delta_seconds(val);
        else if (ieq(name, "s-maxage"))         cc.s_maxage  = delta_seconds(val);
        else if (ieq(name, "min-fresh"))        cc.min_fresh = delta_seconds(val);
        else if (ieq(name, "stale-while-revalidate")) cc.swr = delta_seconds(val);
        else if (ieq(name, "stale-if-error"))         cc.sie = delta_seconds(val);
        else if (ieq(name, "max-stale")) {
            if (val.empty()) cc.max_stale_any = true;
            else             cc.max_stale     = delta_seconds(val);
        }
        // невідомі директиви мовчки минаємо — розширення протоколу законні
    }
    return cc;
}
