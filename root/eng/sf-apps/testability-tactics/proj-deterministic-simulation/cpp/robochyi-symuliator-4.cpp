// Сервер-лічильник. dedup=false → наївний (застосовує все); true — дедуплікує за opID.
struct Server {
    uint64_t value = 0;
    bool dedup = false;
    std::unordered_map<uint64_t, bool> seen;

    void apply(uint64_t opID) {
        if (dedup) {
            if (seen[opID]) return; // ідемпотентність: той самий opID рахуємо один раз
            seen[opID] = true;
        }
        ++value;
    }
};

// Клієнт шле операцію й повторює її, якщо не діждався підтвердження за timeout.
struct Client {
    Sim& sim;
    Net& net;
    Server& srv;
    std::unordered_map<uint64_t, bool> acked;
    uint64_t timeout;

    void sendOp(uint64_t opID, int attempt) {
        char d[48];
        std::snprintf(d, sizeof d, "op%llu спроба%d", (unsigned long long)opID, attempt);
        std::string desc = d;
        net.send("cli→srv " + desc, [this, opID, desc]() {
            srv.apply(opID); // сервер застосовує
            net.send("srv→cli ack " + desc, [this, opID]() {
                acked[opID] = true; // …і підтверджує
            });
        });
        sim.after(timeout, [this, opID, attempt]() { // таймер повтору
            if (!acked[opID] && attempt < 3) {
                sendOp(opID, attempt + 1); // не діждались ack → шлемо ТОЙ САМИЙ opID знову
            }
        });
    }
};
