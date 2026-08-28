// RFC 9111 §3
bool may_store(const Request& rq, const Response& rs, const CacheControl& cc, bool shared) {
    if (rq.method != "GET" && rq.method != "HEAD")            return false;
    if (cc.no_store)                                          return false;
    if (parse_cache_control(value_of(rq.headers, "cache-control")).no_store) return false;
    if (shared && cc.is_private)                              return false;

    // §3.5: відповідь на запит з Authorization спільний кеш зберігає лише
    // з явного дозволу — public, s-maxage або must-revalidate
    if (shared && rq.headers.find("authorization") &&
        !(cc.is_public || cc.s_maxage || cc.must_revalidate)) return false;

    const std::string vary = value_of(rs.headers, "vary");
    if (vary.find('*') != std::string::npos)                  return false;  // ніколи не збіжиться

    const bool has_explicit = cc.is_public || cc.max_age || (shared && cc.s_maxage) ||
                              rs.headers.find("expires");
    return has_explicit || heuristically_cacheable(rs.status);
}
