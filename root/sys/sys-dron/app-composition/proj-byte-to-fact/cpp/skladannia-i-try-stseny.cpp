Unit g_shown{"фт", 0.3048};             // що обрав користувач; у станції це налаштування

void feed_bytes(Parser &p, Router &r, const uint8_t *b, size_t n) {
    Frame f;
    for (size_t i = 0; i < n; ++i)
        if (feed(p, b[i], f))
            if (Vehicle *v = r.route(f)) v->handle(f);
}

void feed_chunk(Parser &p, Router &r, const std::vector<uint8_t> &d) {
    feed_bytes(p, r, d.data(), d.size());
}

std::vector<uint8_t> alt_mm(int32_t mm) {
    uint32_t u = static_cast<uint32_t>(mm);
    return {uint8_t(u), uint8_t(u >> 8), uint8_t(u >> 16), uint8_t(u >> 24)};
}

int main() {
    Bus    bus;
    Router router(bus);
    Parser link[2];                     // ← стан розбору на КОЖНЕ джерело

    router.onNewVehicle = [](Vehicle &v) {
        v.altitude.onChanged = [&v](Fact &f) {
            std::printf("  екран: апарат %u   %s %s\n", unsigned(v.sysid),
                        f.name(), f.display(g_shown).c_str());
        };
    };

    const auto hbA  = pack(0, 1, COMP_AUTOPILOT, MSG_HEARTBEAT, {0x80});
    const auto altA = pack(1, 1, COMP_AUTOPILOT, MSG_ALT, alt_mm(42300));
    const auto hbB  = pack(0, 2, COMP_AUTOPILOT, MSG_HEARTBEAT, {0x00});
    const auto altB = pack(1, 2, COMP_AUTOPILOT, MSG_ALT, alt_mm(15000));

    // порції рвуться посеред кадру, а джерела чергуються — як воно й буває
    std::printf("акт 1 — два джерела, свій стан на кожне\n");
    feed_chunk(link[0], router, hbA);
    feed_chunk(link[1], router, hbB);
    feed_bytes(link[0], router, altA.data(), 6);                    // півкадру A
    feed_chunk(link[1], router, altB);                              // увесь кадр B
    feed_bytes(link[0], router, altA.data() + 6, altA.size() - 6);  // решта A
    bus.drain();
    std::printf("  апаратів: %zu   цілих кадрів: %u + %u\n",
                router.vehicles().size(), link[0].good, link[1].good);

    std::printf("акт 2 — ТІ САМІ байти в ОДИН спільний стан\n");
    Parser shared;
    Frame  f;
    int    got = 0;
    for (size_t i = 0; i < 6; ++i)            got += feed(shared, altA[i], f);  // півкадру A
    for (uint8_t b : altB)                    got += feed(shared, b, f);        // увесь кадр B
    for (size_t i = 6; i < altA.size(); ++i)  got += feed(shared, altA[i], f);  // решта A
    std::printf("  цілих кадрів: %d   зіпсованих: %u\n", got, shared.bad);

    std::printf("акт 3 — 50 кадрів висоти за один такт\n");
    Fact &alt = router.vehicles()[0]->altitude;
    const uint32_t c0 = alt.calls, ch0 = alt.changes;
    const uint32_t m0 = bus.merged(), d0 = bus.delivered();
    for (int i = 0; i < 50; ++i)
        feed_chunk(link[0], router,
                   pack(uint8_t(i), 1, COMP_AUTOPILOT, MSG_ALT, alt_mm(42300 + i * 10)));
    std::printf("  setRaw: %u   справжніх змін: %u   злито в черзі: %u\n",
                alt.calls - c0, alt.changes - ch0, bus.merged() - m0);
    bus.drain();
    std::printf("  сповіщень за такт: %u\n", bus.delivered() - d0);

    g_shown = Unit{"м", 1.0};           // користувач перемкнув одиниці
    std::printf("одиниці змінено — жодного нового байта з борту\n");
    for (const auto &v : router.vehicles())
        std::printf("  апарат %u   %s\n", unsigned(v->sysid),
                    v->altitude.display(g_shown).c_str());
}
