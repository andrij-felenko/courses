#include <vector>
#include <cstdint>

using Bits = std::vector<uint8_t>;   // по одному біту на елемент (0 або 1)

// Модель кристала: ланцюг тригерів + комбінаційна логіка між ними.
struct Chip {
    Bits ff;                                  // стан усіх тригерів ланцюга
    explicit Chip(size_t n) : ff(n, 0) {}     // після ввімкнення там сміття; тут нулі

    // scan_en = 1: подати біт на scan-in, тактнути, зчитати scan-out.
    // Голова ланцюга бере новий біт, хвіст випадає назовні — один крок зсуву.
    uint8_t shift(uint8_t scan_in) {
        uint8_t scan_out = ff.back();         // що випадає з кінця ланцюга
        for (size_t i = ff.size() - 1; i > 0; --i)
            ff[i] = ff[i - 1];                 // усі тригери крокують на позицію далі
        ff.front() = scan_in;                 // на звільнене місце — новий біт
        return scan_out;
    }

    // scan_en = 0: РІВНО один робочий такт. Кожен тригер бере наступний стан
    // від комбінаційної логіки — саме її справність ми й перевіряємо.
    void capture() { ff = logic(ff); }

    // Комбінаційна логіка між стінками тригерів (замість неї — реальна схема).
    static Bits logic(const Bits& in);
};

// Тестер: прогнати набір векторів крізь ланцюг і звірити з еталоном.
// vectors[k] — що засунути в тригери; golden[k] — відгук справного кристала
// (знятий тим самим тестером у тому ж порядку зсуву, тож біти сходяться).
bool runScanTest(Chip& chip, const std::vector<Bits>& vectors,
                 const std::vector<Bits>& golden) {
    const size_t N = chip.ff.size();
    const size_t M = vectors.size();
    Bits response(N);

    // SHIFT-IN найпершого вектора: виштовхувати ще нема чого.
    for (size_t i = 0; i < N; ++i)
        chip.shift(vectors[0][i]);

    for (size_t k = 0; k < M; ++k) {
        chip.capture();                        // CAPTURE: один робочий такт

        // SHIFT-OUT на N тактів: виштовхуємо відгук на vectors[k] і ТИМ САМИМ
        // рухом засуваємо vectors[k+1] — довгі фази зсуву перекриваються.
        for (size_t i = 0; i < N; ++i) {
            uint8_t feed = (k + 1 < M) ? vectors[k + 1][i] : 0;
            response[i] = chip.shift(feed);
        }

        if (response != golden[k])
            return false;                      // відгук не збігся — кристал бракований
    }
    return true;                               // усі вектори пройшли — кристал справний
}

// Заглушка замість реальної схеми, щоб приклад збирався й крутився.
Bits Chip::logic(const Bits& in) {
    Bits out(in.size());
    for (size_t i = 0; i < in.size(); ++i)
        out[i] = in[i] ^ in[(i + 1) % in.size()];
    return out;
}
