// ── 1. Властивість, що сама тримає своїх слухачів ──
#include <algorithm>
#include <cstddef>
#include <functional>
#include <utility>
#include <vector>

template <class T>
class Property {
public:
    using Listener = std::function<void(const T&)>;

    explicit Property(T v = T{}) : value_(std::move(v)) {}

    const T& get() const { return value_; }

    void set(T next) {
        if (next == value_) return;          // не змінилось — не сповіщаємо
        value_ = std::move(next);
        std::vector<Sub> copy = subs_;       // копія: слухач може відписатися просто в обході
        for (const Sub& s : copy) s.second(value_);
    }

    std::size_t on(Listener fn) {            // повертаємо квиток на відписку
        subs_.emplace_back(next_id_, std::move(fn));
        return next_id_++;
    }

    void off(std::size_t id) {
        subs_.erase(std::remove_if(subs_.begin(), subs_.end(),
                                   [id](const Sub& s) { return s.first == id; }),
                    subs_.end());
    }

private:
    using Sub = std::pair<std::size_t, Listener>;
    T value_;
    std::vector<Sub> subs_;
    std::size_t next_id_ = 1;
};
