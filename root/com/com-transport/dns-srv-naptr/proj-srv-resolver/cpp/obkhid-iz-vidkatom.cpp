// dial іде готовим планом: цілі за порядком, адреси кожної цілі за порядком.
// Жодного нового запиту в DNS: план уже розіграний, перерозігрувати його не можна.
Conn dial(const std::string& domain, const std::vector<Target>& plan, int budget) {
    int tries = 0;
    for (const auto& t : plan) {
        for (const auto& a : t.addrs) {
            if (tries++ >= budget)              // специфікація межі не ставить — ставимо ми
                throw Exhausted{"бюджет спроб вичерпано"};

            int fd = connect_to(a, t.port, std::chrono::seconds(2));
            if (fd < 0) continue;               // відмова або таймаут — наступна адреса

            // Ім'я для TLS — ПОЧАТКОВИЙ домен, а не ціль, куди привів SRV.
            if (Conn c = start_tls(fd, domain)) return c;
            ::close(fd);
        }
    }
    throw Exhausted{"жодна ціль не відповіла"};
}
