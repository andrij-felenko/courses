// analytics.cpp — той самий шов у C++: обмежена черга + пул std::thread → черга вироків
#include <condition_variable>
#include <cstddef>
#include <deque>
#include <mutex>
#include <string>
#include <thread>

struct Frame   { std::string deviceId; double value; };
struct Verdict { std::string deviceId; double risk;  };

// Шов = ⟨місткість, політика⟩ окремим типом. Політика «блокувати» — це очікування на
// condition_variable: коли повно, продюсер жде місця (зворотний тиск угору, до джерела).
template <typename T>
class BoundedQueue {
    std::deque<T>           buf_;
    std::size_t             cap_;
    std::mutex              m_;
    std::condition_variable notFull_, notEmpty_;
public:
    explicit BoundedQueue(std::size_t cap) : cap_(cap) {}

    void push(T v) {                                   // повно → блокуємось саме тут
        std::unique_lock lk(m_);
        notFull_.wait(lk, [&]{ return buf_.size() < cap_; });
        buf_.push_back(std::move(v));
        notEmpty_.notify_one();
    }
    T pop() {
        std::unique_lock lk(m_);
        notEmpty_.wait(lk, [&]{ return !buf_.empty(); });
        T v = std::move(buf_.front()); buf_.pop_front();
        notFull_.notify_one();                         // звільнили місце — будимо продюсера
        return v;
    }
};

BoundedQueue<Frame>   work{256};       // ШОВ Б: 256 — це і є шов
BoundedQueue<Verdict> verdicts{64};    // ШОВ В: канал до стадії правил

double scoreAnomaly(const Frame& f) { /* ~40 мс чистого CPU: вікно, кореляції, поріг */ return 0; }

void startPool() {
    unsigned n = std::thread::hardware_concurrency();
    for (unsigned i = 0; i < n; ++i)
        std::thread([]{
            for (;;) {                                 // N воркерів — з однієї черги
                Frame f = work.pop();
                verdicts.push({f.deviceId, scoreAnomaly(f)});  // ШОВ В: вирок у правила
            }
        }).detach();
}

void startRules() {
    std::thread([]{
        for (;;) {                                     // стадія правил споживає вироки
            Verdict v = verdicts.pop();
            if (v.risk > 0.9) { /* дія: сповістити, вимкнути розетку */ }
        }
    }).detach();
}

// міст від ядра: кладе кадр у чергу. Повно → push блокується (зворотний тиск до джерела).
void submit(const Frame& f) { work.push(f); }
