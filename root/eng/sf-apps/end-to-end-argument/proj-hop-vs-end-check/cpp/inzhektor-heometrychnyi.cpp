// Джерело псувань на одній ділянці.
struct Injector {
    std::mt19937_64 rng;
    std::geometric_distribution<long long> gap;   // чистий проміжок у байтах
    long long countdown;

    Injector(uint64_t seed, double rate) : rng(seed), gap(rate) { countdown = gap(rng); }

    // Пропустити len байтів і скласти зсуви подій, що на них припали.
    void advance(size_t len, std::vector<size_t>& hits) {
        hits.clear();
        size_t pos = 0;
        while (countdown < (long long)(len - pos)) {
            pos += (size_t)countdown;
            hits.push_back(pos);
            ++pos;                                // байт із подією спожито
            countdown = gap(rng);
        }
        countdown -= (long long)(len - pos);      // решту проміжку несемо в наступний кадр
    }
};
