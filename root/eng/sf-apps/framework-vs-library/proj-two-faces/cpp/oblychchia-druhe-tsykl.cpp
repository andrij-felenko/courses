std::vector<Host> hosts = load_hosts();          // живе довше за цикл
probe::Core core{std::chrono::milliseconds{300}, 3};

const auto t0 = probe::Clock::now();
for (Host& h : hosts) core.add(t0, h.addr, "ping", &h);

probe::run(core, [](const probe::Event& e) {
    const Host& h = *static_cast<const Host*>(e.tag);
    std::printf("%-20s %-10s %lld мс\n", h.name.c_str(), name(e.status),
                static_cast<long long>(e.rtt.count()));
});
