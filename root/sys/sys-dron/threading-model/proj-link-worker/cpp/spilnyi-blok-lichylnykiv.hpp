// LinkTypes.h, продовження
struct LinkStats {
    std::atomic<qint64> emitted        {0};   // пише робітник: скільки пачок випущено
    std::atomic<qint64> delivered      {0};   // пише головна: скільки прийнято
    std::atomic<qint64> datagrams      {0};   // пише робітник
    std::atomic<qint64> bytesIn        {0};   // пише робітник
    std::atomic<qint64> residenceLastNs{0};   // пише головна
    std::atomic<qint64> residenceMaxNs {0};   // пише головна

    // Читати саме в цьому порядку: спершу delivered, потім emitted.
    qint64 inFlight() const
    {
        const qint64 d = delivered.load(std::memory_order_relaxed);
        const qint64 e = emitted.load(std::memory_order_relaxed);
        return e - d;
    }
};

using LinkStatsPtr = std::shared_ptr<LinkStats>;
