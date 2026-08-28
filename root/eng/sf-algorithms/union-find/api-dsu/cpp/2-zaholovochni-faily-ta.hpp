#ifndef DISJOINT_SET_UNION_HPP
#define DISJOINT_SET_UNION_HPP

#include <cstddef>
#include <vector>
#include <stdexcept>
#include <utility>

namespace algo {

/**
 * @brief Клас системи неперетинних множин (Disjoint Set Union / Union-Find).
 */
class DisjointSetUnion {
public:
    /**
     * @brief Конструює новий об'єкт DSU з n дискретними елементами.
     * 
     * @param n Кількість елементів (індекси від 0 до n-1).
     * @throws std::bad_alloc Якщо не вдалося виділити пам'ять під масиви.
     */
    explicit DisjointSetUnion(std::size_t n);

    ~DisjointSetUnion() noexcept = default;

    // Підтримка семантики переміщення (Move semantics)
    DisjointSetUnion(DisjointSetUnion&& other) noexcept = default;
    DisjointSetUnion& operator=(DisjointSetUnion&& other) noexcept = default;

    // Заборона копіювання для запобігання неявним важким дублюванням пам'яті
    DisjointSetUnion(const DisjointSetUnion&) = delete;
    DisjointSetUnion& operator=(const DisjointSetUnion&) = delete;

    /**
     * @brief Повертає індекс кореневого представника для елемента x.
     * 
     * @param x Індекс елемента [0, n-1].
     * @return std::size_t Індекс канонічного кореня.
     * @throws std::out_of_range Якщо x >= capacity().
     * 
     * @note Модифікує внутрішній стан дерева (Path Compression).
     */
    [[nodiscard]] std::size_t find(std::size_t x);

    /**
     * @brief Об'єднує підмножини, що містять елементи x та y.
     * 
     * @param x Індекс першого елемента.
     * @param y Індекс другого елемента.
     * @return true Якщо елементи належали різним множинам і їх було об'єднано.
     * @return false Якщо елементи вже перебували в одній множині.
     * @throws std::out_of_range Якщо x або y виходять за межі допустимих індексів.
     */
    bool unite(std::size_t x, std::size_t y);

    /**
     * @brief Перевіряє, чи належать елементи x та y одній підмножині.
     * 
     * @param x Індекс першого елемента.
     * @param y Індекс другого елемента.
     * @return true Якщо find(x) == find(y).
     */
    [[nodiscard]] bool connected(std::size_t x, std::size_t y);

    /**
     * @brief Повертає кількість елементів у підмножині елемента x.
     * 
     * @param x Індекс елемента.
     * @return std::size_t Кількість вузлів у даному класі.
     */
    [[nodiscard]] std::size_t set_size(std::size_t x);

    /**
     * @brief Повертає поточну кількість неперетинних підмножин.
     */
    [[nodiscard]] std::size_t num_sets() const noexcept;

    /**
     * @brief Повертає загальну кількість елементів N.
     */
    [[nodiscard]] std::size_t capacity() const noexcept;

private:
    std::size_t capacity_;
    std::size_t num_sets_;
    mutable std::vector<int> parent_or_size_;
};

} // namespace algo

#endif // DISJOINT_SET_UNION_HPP
