Response Proxy::handle(const Request& rq) {
    const CacheControl rcc = parse_cache_control(value_of(rq.headers, "cache-control"));

    if (rq.method != "GET" && rq.method != "HEAD") {          // небезпечний метод
        Response up = origin_.send(rq);
        if (up.status < 400) store_.invalidate(rq.url);       // RFC 9111 §4.4
        return up;
    }

    const auto now = Steady::now();
    std::shared_ptr<const Entry> e = store_.lookup(rq.method, rq.url, rq.headers);

    if (!e) {
        if (rcc.only_if_cached) return Response::of(504);     // клієнт заборонив мережу
        return fetch_and_store(rq);
    }

    switch (decide(*e, rcc, now, shared_)) {
        case Act::Serve:
            return serve(*e, current_age(*e, now));
        case Act::ServeStaleAsync:
            pool_.post([this, rq] { revalidate(rq); });       // одна фонова спроба на ключ
            return serve(*e, current_age(*e, now));
        default:
            if (rcc.only_if_cached) return Response::of(504);
            return revalidate_now(rq, e);
    }
}

Response Proxy::serve(const Entry& e, Secs age) {
    Response r = Response::from(e);
    // §5.1: віддаючи збережене без валідації, кеш ЗОБОВ'ЯЗАНИЙ виставити Age,
    // замінивши той, що прийшов від upstream
    r.headers.set("age", std::to_string(age.count()));
    return r;
}
