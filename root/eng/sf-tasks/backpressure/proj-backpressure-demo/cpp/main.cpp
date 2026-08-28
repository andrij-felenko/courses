#include <condition_variable>
#include <mutex>
#include <queue>

// Стеля: у STL готової конкурентної черги немає — пишемо руками.
// Уся стеля — це друга умовна змінна notFull, на якій засинає той, хто кладе.
template <class T>
class bounded_queue {
    std::mutex              mu;
    std::condition_variable notFull, notEmpty;
    std::queue<T>           items;
    const std::size_t       cap;
public:
    explicit bounded_queue(std::size_t cap) : cap(cap) {}

    void put(T j) {                                    // на ПОВНІЙ черзі блокує
        std::unique_lock lk(mu);
        notFull.wait(lk, [&] { return items.size() < cap; });
        items.push(std::move(j));
        notEmpty.notify_one();
    }
    T take() {                                         // на ПОРОЖНІЙ — чекає
        std::unique_lock lk(mu);
        notEmpty.wait(lk, [&] { return !items.empty(); });
        T j = std::move(items.front());
        items.pop();
        notFull.notify_one();
        return j;
    }
};

// Двійник без стелі — це та сама черга, з якої вийняли один рядок:
// приберіть notFull разом із notFull.wait — і put уже НІКОЛИ не чекає,
// а черга росте до OOM. Саме так необмежена черга й повертається: хтось
// «спрощує» put, викинувши очікування, якого на швидкому споживачі й не видно.
