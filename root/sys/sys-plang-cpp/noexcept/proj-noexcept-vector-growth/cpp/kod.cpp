struct Run { Counters c; double seconds = 0; double checksum = 0; };

template <bool NX>
Run measure(std::size_t n, std::size_t payload, bool with_reserve) {
    g.reset();
    std::vector<Payload<NX>> v;
    if (with_reserve) v.reserve(n);

    const auto t0 = std::chrono::steady_clock::now();
    for (std::size_t i = 0; i < n; ++i)
        v.emplace_back(payload);
    const auto t1 = std::chrono::steady_clock::now();

    Run r;
    r.c       = g;
    r.seconds = std::chrono::duration<double>(t1 - t0).count();
    for (const Payload<NX>& e : v) r.checksum += e.head();   // щоб результат був потрібен
    return r;
}

template <bool NX>
Run best_of(int reps, std::size_t n, std::size_t payload, bool with_reserve) {
    Run best = measure<NX>(n, payload, with_reserve);
    for (int i = 1; i < reps; ++i) {
        const Run cur = measure<NX>(n, payload, with_reserve);
        if (cur.seconds < best.seconds) best = cur;   // мінімум, а не середнє
    }
    return best;
}
