// Мережа під повним контролем симулятора: він сам вирішує долю кожного повідомлення.
struct Net {
    Sim& sim;
    uint64_t dropPct;
    uint64_t minLat;
    uint64_t maxLat;
    std::vector<std::string> log;

    // send доставляє deliver() КОЛИСЬ — або не доставляє зовсім. Усе рішення — із зерна.
    void send(const std::string& desc, std::function<void()> deliver) {
        char t[48];
        if (sim.rng.chance(dropPct)) { // втрата
            std::snprintf(t, sizeof t, "t=%2llu  ВТРАТА   ", (unsigned long long)sim.now);
            log.push_back(std::string(t) + desc);
            return;
        }
        uint64_t lat = minLat + sim.rng.intn(maxLat - minLat + 1); // затримка з засіяного діапазону
        sim.after(lat, [this, desc, deliver = std::move(deliver)]() {
            char t[48];
            std::snprintf(t, sizeof t, "t=%2llu  доставка ", (unsigned long long)sim.now);
            log.push_back(std::string(t) + desc);
            deliver();
        });
    }
};
