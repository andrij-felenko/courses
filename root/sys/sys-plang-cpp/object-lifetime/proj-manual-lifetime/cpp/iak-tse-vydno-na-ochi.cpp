#include <cstdio>
#include <iterator>

struct Noisy {
    int id;
    explicit Noisy(int i) : id(i) {
        if (i == 4) throw std::runtime_error("конструктор 4 не вдався");
        std::printf("  + збудовано %d\n", id);
    }
    ~Noisy() { std::printf("  - зруйновано %d\n", id); }
    Noisy(const Noisy&) = delete;
};

int main() {
    StaticVector<Noisy, 8> v;
    v.emplace_back(0);
    v.emplace_back(1);

    const int rest[] = {2, 3, 4, 5};
    try {
        v.append(std::begin(rest), std::end(rest));
    } catch (const std::exception& e) {
        std::printf("спіймано: %s; size = %zu\n", e.what(), v.size());
    }
}                                   // ← тут спрацює деструктор контейнера
