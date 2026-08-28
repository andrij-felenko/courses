// Концептуальний приклад безблокувальної публікації у фронт з вирівнюванням:
template <typename T>
class alignas(64) LockFreeFrontier {
    std::vector<T> data;
    alignas(64) std::atomic<std::size_t> tail{0};
public:
    void push(T val) {
        std::size_t idx = tail.fetch_add(1, std::memory_order_relaxed);
        data[idx] = val;
    }
};
