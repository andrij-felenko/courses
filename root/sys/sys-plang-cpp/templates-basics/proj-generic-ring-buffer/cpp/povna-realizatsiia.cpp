#include <iostream>
#include <cstddef>
#include <new>
#include <utility>
#include <type_traits>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <iterator>
#include <algorithm>

template <typename T, std::size_t Capacity>
class RingBuffer {
    static_assert(Capacity > 0, "Розмір кільцевого буфера зобов'язаний бути більшим за 0!");

public:
    // Шаблони псевдонімів (Alias Templates) для стандартизації інтерфейсу
    using value_type      = T;
    using size_type       = std::size_t;
    using reference       = T&;
    using const_reference = const T&;
    using pointer         = T*;
    using const_pointer   = const T*;

    // Вкладений шаблон ітератора кільцевого буфера
    template <bool IsConst>
    class RingIterator {
    public:
        using iterator_category = std::forward_iterator_tag;
        using value_type        = T;
        using difference_type   = std::ptrdiff_t;
        using pointer           = std::conditional_t<IsConst, const T*, T*>;
        using reference         = std::conditional_t<IsConst, const T&, T&>;

        RingIterator(std::conditional_t<IsConst, const RingBuffer*, RingBuffer*> buffer, size_type offset)
            : buffer_(buffer), offset_(offset) {}

        reference operator*() const {
            return (*buffer_)[offset_];
        }

        pointer operator->() const {
            return &((*buffer_)[offset_]);
        }

        RingIterator& operator++() {
            ++offset_;
            return *this;
        }

        RingIterator operator++(int) {
            RingIterator tmp = *this;
            ++offset_;
            return tmp;
        }

        bool operator==(const RingIterator& other) const noexcept {
            return buffer_ == other.buffer_ && offset_ == other.offset_;
        }

        bool operator!=(const RingIterator& other) const noexcept {
            return !(*this == other);
        }

    private:
        std::conditional_t<IsConst, const RingBuffer*, RingBuffer*> buffer_;
        size_type offset_{0};
    };

    using iterator       = RingIterator<false>;
    using const_iterator = RingIterator<true>;

    // Конструктор за замовчуванням: створює порожній буфер без конструювання елементів
    constexpr RingBuffer() noexcept : head_(0), tail_(0), size_(0) {}

    // Конструктор копіювання того ж типу
    RingBuffer(const RingBuffer& other) {
        for (size_type i = 0; i < other.size_; ++i) {
            push(other[i]);
        }
    }

    // Узагальнений конструктор копіювання з буфера іншої місткості OtherCapacity
    template <std::size_t OtherCapacity>
    explicit RingBuffer(const RingBuffer<T, OtherCapacity>& other) {
        const size_type count_to_copy = std::min(Capacity, other.size());
        for (size_type i = 0; i < count_to_copy; ++i) {
            push(other[i]);
        }
    }

    // Конструктор переміщення
    RingBuffer(RingBuffer&& other) noexcept(std::is_nothrow_move_constructible_v<T>) {
        while (!other.empty()) {
            auto val = other.pop();
            if (val) {
                push(std::move(*val));
            }
        }
    }

    // Деструктор: знищує лише реально існуючі елементи
    ~RingBuffer() noexcept {
        clear();
    }

    // Оператор копіювального присвоювання
    RingBuffer& operator=(const RingBuffer& other) {
        if (this != &other) {
            clear();
            for (size_type i = 0; i < other.size_; ++i) {
                push(other[i]);
            }
        }
        return *this;
    }

    // Оператор переміщувального присвоювання
    RingBuffer& operator=(RingBuffer&& other) noexcept(std::is_nothrow_move_constructible_v<T>) {
        if (this != &other) {
            clear();
            while (!other.empty()) {
                auto val = other.pop();
                if (val) {
                    push(std::move(*val));
                }
            }
        }
        return *this;
    }

    // Очищення буфера: оптимізовано для тривіальних та нетривіальних типів
    void clear() noexcept {
        if constexpr (!std::is_trivially_destructible_v<T>) {
            while (!empty()) {
                pop();
            }
        }
        head_ = 0;
        tail_ = 0;
        size_ = 0;
    }

    [[nodiscard]] constexpr size_type size() const noexcept { return size_; }
    [[nodiscard]] constexpr size_type capacity() const noexcept { return Capacity; }
    [[nodiscard]] constexpr bool empty() const noexcept { return size_ == 0; }
    [[nodiscard]] constexpr bool full() const noexcept { return size_ == Capacity; }

    // Додавання копіюванням: сувора безпека до винятків (Strong Exception Safety)
    bool push(const T& item) {
        if (full()) {
            return false;
        }
        // Placement new у комірку пам'яті tail_
        ::new (static_cast<void*>(element_address(tail_))) T(item);
        tail_ = next_index(tail_);
        ++size_;
        return true;
    }

    // Додавання переміщенням
    bool push(T&& item) {
        if (full()) {
            return false;
        }
        ::new (static_cast<void*>(element_address(tail_))) T(std::move(item));
        tail_ = next_index(tail_);
        ++size_;
        return true;
    }

    // Примусове додавання з витісненням найстарішого елемента при переповненні
    void push_overwrite(const T& item) {
        if (full()) {
            // Знищуємо найстаріший елемент перед перезаписом
            element_address(head_)->~T();
            head_ = next_index(head_);
            --size_;
        }
        push(item);
    }

    // Конструювання безпосередньо у буфері (Emplace)
    template <typename... Args>
    bool emplace(Args&&... args) {
        if (full()) {
            return false;
        }
        ::new (static_cast<void*>(element_address(tail_))) T(std::forward<Args>(args)...);
        tail_ = next_index(tail_);
        ++size_;
        return true;
    }

    // Вилучення елемента з поверненням через std::optional
    std::optional<T> pop() {
        if (empty()) {
            return std::nullopt;
        }
        T* ptr = element_address(head_);
        std::optional<T> result(std::move(*ptr));
        ptr->~T(); // Явний виклик деструктора вилученого об'єкта
        head_ = next_index(head_);
        --size_;
        return result;
    }

    // Доступ за логічним індексом (0 — найстаріший доданий елемент)
    reference operator[](size_type index) {
        return *element_address((head_ + index) % Capacity);
    }

    const_reference operator[](size_type index) const {
        return *element_address((head_ + index) % Capacity);
    }

    reference front() {
        if (empty()) throw std::underflow_error("RingBuffer порожній при зверненні до front()");
        return *element_address(head_);
    }

    const_reference front() const {
        if (empty()) throw std::underflow_error("RingBuffer порожній при зверненні до front() const");
        return *element_address(head_);
    }

    // Вкладений шаблон методу трансформації (Member Function Template)
    template <typename Transformer>
    auto map(Transformer&& fn) const {
        using ResultType = std::invoke_result_t<Transformer, const T&>;
        RingBuffer<ResultType, Capacity> result;
        for (size_type i = 0; i < size_; ++i) {
            result.push(fn((*this)[i]));
        }
        return result;
    }

    // Методи ітераторів
    iterator begin() noexcept { return iterator(this, 0); }
    iterator end() noexcept { return iterator(this, size_); }
    const_iterator begin() const noexcept { return const_iterator(this, 0); }
    const_iterator end() const noexcept { return const_iterator(this, size_); }
    const_iterator cbegin() const noexcept { return const_iterator(this, 0); }
    const_iterator cend() const noexcept { return const_iterator(this, size_); }

    // Метод діагностичного виведення (демонстрація лінивого інстанціювання!)
    // Вимагає наявності operator<< для типу T.
    void dump(std::string_view label = "Buffer") const {
        std::cout << "[" << label << " (size=" << size_ << "/" << Capacity << ")]: ";
        for (size_type i = 0; i < size_; ++i) {
            std::cout << (*this)[i] << " ";
        }
        std::cout << "\n";
    }

private:
    // Дружнє оголошення шаблону для доступу між екземплярами різного розміру
    template <typename U, std::size_t OtherCap>
    friend class RingBuffer;

    // Оптимізований розрахунок наступного індексу через побітову маску або остачу
    static constexpr bool is_power_of_two = (Capacity > 0) && ((Capacity & (Capacity - 1)) == 0);

    static constexpr size_type next_index(size_type idx) noexcept {
        if constexpr (is_power_of_two) {
            return (idx + 1) & (Capacity - 1);
        } else {
            return (idx + 1) % Capacity;
        }
    }

    // Допоміжний метод розрахунку адреси комірки
    T* element_address(size_type idx) noexcept {
        return reinterpret_cast<T*>(&storage_[idx * sizeof(T)]);
    }

    const T* element_address(size_type idx) const noexcept {
        return reinterpret_cast<const T*>(&storage_[idx * sizeof(T)]);
    }

    // Неініціалізоване сховище з коректним вирівнюванням
    alignas(alignof(T)) std::byte storage_[Capacity * sizeof(T)];
    size_type head_{0};
    size_type tail_{0};
    size_type size_{0};
};
