static bool build(std::vector<Node>& g, const fs::path& logPath, unsigned jobs) {
    auto log = loadLog(logPath);
    std::mutex mx;                        // стереже чергу, лічильники й журнал
    std::condition_variable cv;
    std::vector<int> ready;
    int left = (int)g.size();
    std::atomic<bool> failed{false};

    for (int v = 0; v < (int)g.size(); ++v)
        if (g[v].pending == 0) ready.push_back(v);

    auto worker = [&] {
        for (;;) {
            int v;
            {   std::unique_lock<std::mutex> lk(mx);
                cv.wait(lk, [&] { return !ready.empty() || left == 0 || failed.load(); });
                if (failed.load() || ready.empty()) return;
                v = ready.back(); ready.pop_back(); }

            runNode(g[v], log, mx, failed);             // єдине місце, де довго

            {   std::lock_guard<std::mutex> lk(mx);
                --left;
                for (int u : g[v].outs)
                    if (--g[u].pending == 0) ready.push_back(u); }
            cv.notify_all();
        }
    };
    std::vector<std::thread> pool;
    for (unsigned i = 0; i < jobs; ++i) pool.emplace_back(worker);
    for (auto& t : pool) t.join();
    saveLog(logPath, log);
    return !failed.load() && left == 0;
}

int main(int argc, char** argv) {
    std::string rulesPath = "build.rules";
    unsigned jobs = std::thread::hardware_concurrency();
    if (!jobs) jobs = 4;
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "-j" && i + 1 < argc) jobs = (unsigned)std::stoul(argv[++i]);
        else rulesPath = a;
    }
    try {
        auto g = buildGraph(parseRules(rulesPath));
        checkAcyclic(g);
        return build(g, rulesPath + ".log", jobs) ? 0 : 1;
    } catch (const std::exception& e) {
        std::fprintf(stderr, "mb: %s\n", e.what());
        return 2;
    }
}
