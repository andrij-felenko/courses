// Виконати задачу, якщо ключ розійшовся з журнальним.
// Повертає true, якщо артефакт СТАВ ІНШИМ (це лише для звіту).
static bool runNode(const Node& n, std::unordered_map<std::string, Stamp>& log,
                    std::mutex& mx, std::atomic<bool>& failed) {
    const Rule& r = n.rule;
    const uint64_t key = taskKey(r);
    Stamp prev;
    {   std::lock_guard<std::mutex> lk(mx);
        if (auto it = log.find(r.out); it != log.end()) prev = it->second; }

    if (key && key == prev.key && fs::exists(r.out)) {
        std::printf("—  %s\n", r.out.c_str());          // ключ той самий: робити нічого
        return false;
    }

    const std::string tmp = r.out + ".mb-tmp";          // ПОРУЧ із виходом, у тій самій теці
    const std::string cmd = expand(r, tmp);
    std::printf("▸  %s\n", cmd.c_str());
    std::error_code ec;
    fs::remove(tmp, ec);

    if (std::system(cmd.c_str()) != 0) {
        fs::remove(tmp, ec);                            // недописаного не лишаємо
        std::fprintf(stderr, "провал: %s\n", r.out.c_str());
        failed = true;
        return false;
    }
    Fnv art;
    if (!hashFile(tmp, art)) {
        std::fprintf(stderr, "команда не створила %s\n", tmp.c_str());
        failed = true;
        return false;
    }
    fs::rename(tmp, r.out, ec);                         // одна неподільна дія
    if (ec) {
        std::fprintf(stderr, "не перейменувати %s: %s\n", tmp.c_str(), ec.message().c_str());
        failed = true;
        return false;
    }
    std::lock_guard<std::mutex> lk(mx);
    const bool changed = (art.h != prev.art);
    log[r.out] = Stamp{key, art.h};
    return changed;
}
