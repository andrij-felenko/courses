static const Loud* seen = nullptr;
static void inspect(const Loud& v) { seen = &v; }

static void part_thread() {
    head("5. Чому std::thread вимагає std::ref");

    Loud shared("спільний");
    Loud::mute(true);                       // далі рахуємо копії, а не друкуємо події

    const int before = Loud::copies();
    std::thread a(inspect, shared);
    a.join();
    std::cout << "    thread(inspect, shared):         копій Loud — "
              << Loud::copies() - before << ";  потік бачив "
              << (seen == &shared ? "той самий" : "ІНШИЙ") << " об'єкт\n";

    const int before2 = Loud::copies();
    std::thread b(inspect, std::cref(shared));
    b.join();
    std::cout << "    thread(inspect, std::cref(...)): копій Loud — "
              << Loud::copies() - before2 << ";  потік бачив "
              << (seen == &shared ? "той самий" : "ІНШИЙ") << " об'єкт\n";

    Loud::mute(false);
}
