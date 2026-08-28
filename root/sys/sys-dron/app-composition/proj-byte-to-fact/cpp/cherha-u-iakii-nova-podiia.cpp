// Стискання подій: ключ — той, хто повідомляє. Якщо його подія вже в черзі,
// нова ЗАМІЩАЄ стару, а не стає позаду неї.
class Bus {
public:
    void post(const void *who, std::function<void()> fn) {
        for (auto &e : _q)
            if (e.who == who) { e.fn = std::move(fn); ++_merged; return; }
        _q.push_back({who, std::move(fn)});
    }
    void drain() {                          // кінець такту: розсилаємо накопичене
        std::vector<Ev> batch;
        batch.swap(_q);                     // те, що обробники напостять зараз, поїде наступним тактом
        for (auto &e : batch) { e.fn(); ++_delivered; }
    }
    uint32_t merged() const    { return _merged; }
    uint32_t delivered() const { return _delivered; }
private:
    struct Ev { const void *who; std::function<void()> fn; };
    std::vector<Ev> _q;
    uint32_t _merged = 0, _delivered = 0;
};
