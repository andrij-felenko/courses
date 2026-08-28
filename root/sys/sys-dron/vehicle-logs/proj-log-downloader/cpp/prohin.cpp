int main(int argc, char** argv)
{
    const uint32_t seed = (argc > 1) ? uint32_t(std::strtoul(argv[1], nullptr, 10)) : 1u;
    const double   loss = (argc > 2) ? std::strtod(argv[2], nullptr) : 0.05;

    std::vector<uint8_t> log(3u << 20);              // 3 МіБ «бортового файлу»
    std::mt19937 filler(0xC0FFEE);
    for (uint8_t& b : log) b = uint8_t(filler());

    FakeVehicle veh(log, seed, loss, /*перестановки*/ 0.03, /*збитий зсув*/ 0.001);
    LogFile out;
    if (!out.open("log_7.ulg", veh.declaredSize())) { std::perror("open"); return 1; }

    Downloader dl(veh, out, /*id*/ 7, veh.declaredSize());
    Ms now = 0;
    dl.start(now);
    while (dl.state() == Downloader::State::Running && now < 3600u * 1000u) {
        now += 19;                                   // кадр 109 Б на 57600 бод
        veh.pump(dl, now);
        dl.onTick(now);
    }

    const Stats& s = dl.stats();
    std::printf("зерно %u, втрати %.0f%%, модельний час %llu с, стан: %s\n",
                seed, loss * 100, (unsigned long long)(now / 1000),
                dl.state() == Downloader::State::Done ? "готово" : "здалися");
    std::printf("кошиків %llu, дублікатів %llu, чужих вікон %llu, збитих зсувів %llu\n",
                (unsigned long long)s.written, (unsigned long long)s.dup,
                (unsigned long long)s.stale,   (unsigned long long)s.unaligned);
    std::printf("запитів %llu, з них за таймером %llu\n",
                (unsigned long long)s.requests, (unsigned long long)s.repeats);

    std::vector<uint8_t> back(dl.size());
    FILE* f = std::fopen("log_7.ulg", "rb");
    const size_t got = std::fread(back.data(), 1, back.size(), f);
    std::fclose(f);
    std::printf("файл %zu Б, збіг із джерелом: %s\n", got,
                (got == log.size() && std::memcmp(back.data(), log.data(), got) == 0)
                    ? "побайтовий" : "РОЗБІЖНІСТЬ");
    return 0;
}
