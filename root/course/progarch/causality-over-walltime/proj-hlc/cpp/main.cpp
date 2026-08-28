#include <algorithm>
#include <cstdint>
#include <functional>
#include <mutex>
#include <stdexcept>
#include <utility>

constexpr std::int64_t  kMaxOffsetMs = 500;      // терпимий відрив чужого годинника вперед, мс
constexpr std::uint32_t kCMax        = 1u << 16; // 16 бітів під лічильник

struct ClockTooFarAhead : std::runtime_error {
    ClockTooFarAhead()
        : std::runtime_error("hlc: чужий годинник неправдоподібно попереду") {}
};
struct CounterOverflow : std::runtime_error {
    CounterOverflow()
        : std::runtime_error("hlc: переповнення лічильника — фізичний час стоїть надто довго") {}
};

// Гібридний годинник одного вузла. Мітка = пара (l, c).
class Hlc {
public:
    explicit Hlc(std::function<std::int64_t()> phys) : phys_(std::move(phys)) {}

    // Локальна подія АБО відправлення — одне й те саме правило.
    std::pair<std::int64_t, std::uint32_t> now() {
        std::lock_guard<std::mutex> lock(mu_);
        const std::int64_t l_prev = l_;
        l_ = std::max(l_prev, phys_());
        c_ = (l_ == l_prev) ? c_ + 1 : 0u; // фізичний застряг — цокаємо, інакше з нуля
        guard();
        return {l_, c_};
    }

    // Отримання повідомлення з міткою (l_m, c_m).
    std::pair<std::int64_t, std::uint32_t> update(std::int64_t l_m, std::uint32_t c_m) {
        std::lock_guard<std::mutex> lock(mu_);
        const std::int64_t pt = phys_();
        if (l_m > pt + kMaxOffsetMs) {
            throw ClockTooFarAhead{}; // не отруюємо свій l чужим годинником
        }
        const std::int64_t l_prev = l_;
        l_ = std::max({l_prev, l_m, pt});
        if (l_ == l_prev && l_ == l_m) {
            c_ = std::max(c_, c_m) + 1;
        } else if (l_ == l_prev) {
            c_ += 1;
        } else if (l_ == l_m) {
            c_ = c_m + 1;
        } else {                        // l_ == pt — фізичний обігнав усіх
            c_ = 0u;
        }
        guard();
        return {l_, c_};
    }

private:
    void guard() const {
        if (c_ >= kCMax) throw CounterOverflow{};
    }

    std::mutex                    mu_;
    std::function<std::int64_t()> phys_;  // джерело настінного часу, мс від епохи
    std::int64_t                  l_ = 0; // фізична частина мітки
    std::uint32_t                 c_ = 0; // лічильник
};

// Порядок міток: спершу за l, потім за c.
inline bool less(std::int64_t l1, std::uint32_t c1,
                 std::int64_t l2, std::uint32_t c2) {
    return l1 < l2 || (l1 == l2 && c1 < c2);
}
