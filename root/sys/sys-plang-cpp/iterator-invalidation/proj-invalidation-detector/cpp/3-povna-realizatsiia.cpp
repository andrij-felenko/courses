#include <iostream>
#include <vector>
#include <stdexcept>
#include <cstdint>
#include <string>
#include <utility>

template <typename T>
class CheckedVector;

// ── Безпечний ітератор з контролем епохи ──────────────────────────────────
template <typename T>
class CheckedIterator {
public:
    using iterator_category = std::random_access_iterator_tag;
    using value_type        = T;
    using difference_type   = std::ptrdiff_t;
    using pointer           = T*;
    using reference         = T&;

    CheckedIterator() = default;

    CheckedIterator(const CheckedVector<T>* vec, typename std::vector<T>::iterator raw_it, uint64_t epoch)
        : m_vec(vec), m_raw_it(raw_it), m_created_epoch(epoch) {}

    // Розіменування з перевіркою дійсності
    reference operator*() const {
        validate_validity();
        validate_dereferenceable();
        return *m_raw_it;
    }

    pointer operator->() const {
        validate_validity();
        validate_dereferenceable();
        return m_raw_it.operator->();
    }

    // Префіксний інкремент
    CheckedIterator& operator++() {
        validate_validity();
        ++m_raw_it;
        return *this;
    }

    // Постфіксний інкремент
    CheckedIterator operator++(int) {
        validate_validity();
        CheckedIterator tmp = *this;
        ++(*this);
        return tmp;
    }

    // Префіксний декремент
    CheckedIterator& operator--() {
        validate_validity();
        --m_raw_it;
        return *this;
    }

    // Арифметика довільного доступу за O(1)
    CheckedIterator operator+(difference_type n) const {
        validate_validity();
        return CheckedIterator(m_vec, m_raw_it + n, m_created_epoch);
    }

    CheckedIterator operator-(difference_type n) const {
        validate_validity();
        return CheckedIterator(m_vec, m_raw_it - n, m_created_epoch);
    }

    difference_type operator-(const CheckedIterator& other) const {
        validate_comparison_with(other);
        return m_raw_it - other.m_raw_it;
    }

    // Оператори порівняння
    bool operator==(const CheckedIterator& other) const {
        validate_comparison_with(other);
        return m_raw_it == other.m_raw_it;
    }

    bool operator!=(const CheckedIterator& other) const {
        return !(*this == other);
    }

    uint64_t created_epoch() const { return m_created_epoch; }

private:
    void validate_validity() const {
        if (!m_vec) {
            throw std::runtime_error("IteratorError: Спроба використати порожній (неініціалізований) ітератор!");
        }
        if (m_created_epoch != m_vec->epoch()) {
            throw std::runtime_error("IteratorInvalidationError: Спроба використання інвалідованого ітератора! "
                                     "Контейнер видозмінився після створення ітератора.");
        }
    }

    void validate_dereferenceable() const {
        if (m_raw_it == m_vec->raw_end()) {
            throw std::runtime_error("IteratorBoundsError: Спроба розіменування ітератора кінця end()!");
        }
    }

    void validate_comparison_with(const CheckedIterator& other) const {
        validate_validity();
        other.validate_validity();
        if (m_vec != other.m_vec) {
            throw std::runtime_error("IteratorMismatchError: Порівняння ітераторів, що належать різним контейнерам!");
        }
    }

    const CheckedVector<T>* m_vec = nullptr;
    typename std::vector<T>::iterator m_raw_it;
    uint64_t m_created_epoch = 0;
};

// ── Безпечний контейнер-вектор ─────────────────────────────────────────────
template <typename T>
class CheckedVector {
public:
    using iterator       = CheckedIterator<T>;
    using const_iterator = CheckedIterator<const T>;

    CheckedVector() = default;

    CheckedVector(std::initializer_list<T> init)
        : m_data(init), m_epoch(0) {}

    T& operator[](size_t index) {
        return m_data.at(index);
    }

    const T& operator[](size_t index) const {
        return m_data.at(index);
    }

    iterator begin() {
        return iterator(this, m_data.begin(), m_epoch);
    }

    iterator end() {
        return iterator(this, m_data.end(), m_epoch);
    }

    typename std::vector<T>::iterator raw_end() const {
        return const_cast<std::vector<T>&>(m_data).end();
    }

    // Модифікуючі операції (кожна збільшує епоху)
    void push_back(const T& val) {
        m_data.push_back(val);
        ++m_epoch;
    }

    void push_back(T&& val) {
        m_data.push_back(std::move(val));
        ++m_epoch;
    }

    iterator erase(iterator pos) {
        auto raw_pos = m_data.begin() + (pos - begin());
        auto new_raw = m_data.erase(raw_pos);
        ++m_epoch;
        return iterator(this, new_raw, m_epoch);
    }

    void reserve(size_t n) {
        if (n > m_data.capacity()) {
            m_data.reserve(n);
            ++m_epoch;
        }
    }

    void clear() {
        m_data.clear();
        ++m_epoch;
    }

    size_t size() const { return m_data.size(); }
    size_t capacity() const { return m_data.capacity(); }
    uint64_t epoch() const { return m_epoch; }

private:
    std::vector<T> m_data;
    uint64_t m_epoch = 0;
};
