namespace ds {

template <typename T>
class BinomialHeap {
public:
    using NodeHandle = Node*;

    // Конструктор за замовчуванням: створює порожню купу за O(1)
    BinomialHeap() noexcept;

    // Деструктор: автоматично звільняє уся дерева за O(n)
    ~BinomialHeap();

    // Заборона копіювання: купа є унікальним володарем вузлів
    BinomialHeap(const BinomialHeap&) = delete;
    BinomialHeap& operator=(const BinomialHeap&) = delete;

    // Переміщення: передає володіння деревами за O(1)
    BinomialHeap(BinomialHeap&& other) noexcept;
    BinomialHeap& operator=(BinomialHeap&& other) noexcept;

    // Перевірка на порожнечу
    [[nodiscard]] bool empty() const noexcept;

    // Вставка: повертає NodeHandle для подальшого використання у decrease_key
    NodeHandle insert(T key);

    // Злиття з іншою купою: other стає порожньою
    void merge(BinomialHeap& other);

    // Пошук мінімуму: повертає std::nullopt для порожньої купи
    [[nodiscard]] std::optional<T> find_min() const;

    // Вилучення мінімуму: кидає std::underflow_error для порожньої купи
    T extract_min();

    // Зменшення ключа: кидає std::invalid_argument при new_key > current
    void decrease_key(NodeHandle handle, T new_key);
};

} // namespace ds
