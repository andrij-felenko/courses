class Hold {
public:
    Hold(Link &link, int function) : _link(link), _function(function) {}
    ~Hold() { release(); }                            // єдиний спосіб не забути

    Hold(const Hold &) = delete;
    Hold &operator=(const Hold &) = delete;

    Verdict tick(float value, float holdSec) { return sendOrder(_link, param5(), value, holdSec); }

    bool px4Dialect() const     { return _dialect; }
    bool standardPossible() const { return standardFunction(_function) > 0; }
    void fallBackToStandard()   { _dialect = false; }

    void release()
    {
        if (_released) return;
        _released = true;
        // Термін 0 борт перекладає на «відпустити»; NaN лишає вихід знеструмленим.
        // Тричі — бо сама датаграма відпускання теж може загубитися.
        for (int i = 0; i < 3; ++i) {
            sendOrderRaw(_link, param5(), std::numeric_limits<float>::quiet_NaN(), 0.f);
        }
    }

private:
    int param5() const { return _dialect ? 1000 + _function : standardFunction(_function); }

    Link &_link;
    int _function;
    bool _dialect = true;
    bool _released = false;
};

static int runTest(Link &link, int function, float value, double seconds)
{
    constexpr int   periodMs = 100;    // крок сторожового повторення
    constexpr float holdSec  = 1.0f;   // термін одного наказу

    Hold hold(link, function);
    int silence = 0;
    const int64_t stopAt = nowMs() + static_cast<int64_t>(seconds * 1000);
    int64_t next = nowMs();

    while (nowMs() < stopAt) {
        switch (hold.tick(value, holdSec)) {
        case Verdict::Accepted:
        case Verdict::Retry:
            silence = 0;
            break;
        case Verdict::Silence:
            if (++silence * periodMs > 1000) {        // смуга мовчання, не один пропуск
                std::fprintf(stderr, "борт мовчить понад секунду\n");
                return 1;
            }
            break;
        case Verdict::Unsupported:
            if (hold.px4Dialect() && hold.standardPossible()) {
                std::fprintf(stderr, "борт не знає діалекту PX4 — пробуємо стандартний номер\n");
                hold.fallBackToStandard();
                break;
            }
            std::fprintf(stderr, "функцію %d цим протоколом не адресувати\n", function);
            return 1;
        case Verdict::Refused:
            std::fprintf(stderr, "відмовлено: апарат armed або запобіжний перемикач не знято\n");
            return 1;
        }

        next += periodMs;                             // абсолютний розклад, без накопичення зсуву
        if (next < nowMs()) next = nowMs();
        std::this_thread::sleep_for(std::chrono::milliseconds(next - nowMs()));
    }
    return 0;                                          // ~Hold() відпустить сам
}
