// Первинний шаблон змінної
template<typename T>
constexpr std::size_t alignment_v = alignof(T);

// Часткова спеціалізація для масивів невідомого розміру
template<typename T>
constexpr std::size_t alignment_v<T[]> = alignof(T);

// Часткова спеціалізація для вказівників на функції
template<typename Ret, typename... Args>
constexpr std::size_t alignment_v<Ret(*)(Args...)> = alignof(void*);

// Повна спеціалізація для void (оскільки alignof(void) не є валідним виразом)
template<>
constexpr std::size_t alignment_v<void> = 0;
