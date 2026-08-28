// Один прогін — чиста функція від зерна: та сама відповідь щоразу.
struct Result {
    bool ok;
    uint64_t value;
    std::vector<std::string> log;
};

Result runOnce(uint64_t seed, bool naive) {
    Sim s(seed);
    Net net{s, 0, 1, 12}; // втрати тут вимкнені (dropPct=0) — ізолюємо гонитву таймауту
    Server srv;
    srv.dedup = !naive;
    Client cli{s, net, srv, {}, 24};

    for (uint64_t i = 0; i < K; ++i) { // вкидаємо K операцій у різні моменти
        s.after(i * 10, [&cli, i]() { cli.sendOp(i, 1); });
    }
    s.run();

    // ІНВАРІАНТ БЕЗПЕКИ: жодну операцію не пораховано двічі.
    return {srv.value <= K, srv.value, net.log};
}
