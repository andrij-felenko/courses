// 1. Порожній безстанний делітер
struct StatelessDeleter {
    void operator()(int* ptr) const noexcept {
        delete ptr;
    }
};

// 2. Безстанний делітер, захищений від спадкування (final)
struct FinalStatelessDeleter final {
    void operator()(int* ptr) const noexcept {
        delete ptr;
    }
};

// 3. Делітер зі станом (наприклад, посилання на арену або лічильник)
struct StatefulDeleter {
    size_t* call_counter{nullptr};

    void operator()(int* ptr) const noexcept {
        if (call_counter) {
            ++(*call_counter);
        }
        delete ptr;
    }
};

// --- Тестування реалізації EBO (legacy) ---
// Звичайний порожній делітер стискається до 8 байтів:
static_assert(sizeof(legacy::compressed_pair<int*, StatelessDeleter>) == 8);
// Для final-делітера EBO вимикається -> розмір зростає до 16 байтів:
static_assert(sizeof(legacy::compressed_pair<int*, FinalStatelessDeleter>) == 16);
// Для stateful-делітера розмір становить 16 байтів (8 байтів покажчик + 8 байтів стан):
static_assert(sizeof(legacy::compressed_pair<int*, StatefulDeleter>) == 16);

// --- Тестування реалізації C++20 ([[no_unique_address]]) ---
// Звичайний порожній делітер:
static_assert(sizeof(modern::compressed_pair<int*, StatelessDeleter>) == 8);
// КРИТИЧНА РІЗНИЦЯ: C++20 успішно стискає final-делітер до 8 байтів!
static_assert(sizeof(modern::compressed_pair<int*, FinalStatelessDeleter>) == 8);
// Stateful-делітер:
static_assert(sizeof(modern::compressed_pair<int*, StatefulDeleter>) == 16);

// --- Тестування кінцевого розумного покажчика optimal_unique_ptr ---
static_assert(sizeof(optimal_unique_ptr<int, std::default_delete<int>>) == 8);
static_assert(sizeof(optimal_unique_ptr<int, StatelessDeleter>) == 8);
static_assert(sizeof(optimal_unique_ptr<int, FinalStatelessDeleter>) == 8);
static_assert(sizeof(optimal_unique_ptr<int, StatefulDeleter>) == 16);
