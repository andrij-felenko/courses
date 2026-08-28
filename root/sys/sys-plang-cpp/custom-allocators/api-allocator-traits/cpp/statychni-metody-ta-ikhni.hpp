// 1. Виділення сирої пам'яті
[[nodiscard]] static pointer allocate(Alloc& a, size_type n);
[[nodiscard]] static pointer allocate(Alloc& a, size_type n, const_void_pointer hint);

// 2. Виділення пам'яті з інформацією про надлишкову ємність (C++23)
[[nodiscard]] static std::allocation_result<pointer, size_type>
allocate_at_least(Alloc& a, size_type n);

// 3. Звільнення сирої пам'яті
static void deallocate(Alloc& a, pointer p, size_type n);

// 4. Ініціалізація та конструювання об'єкта
template <class T, class... Args>
static void construct(Alloc& a, T* p, Args&&... args);

// 5. Знищення об'єкта
template <class T>
static void destroy(Alloc& a, T* p);

// 6. Теоретичний ліміт виділення
static size_type max_size(const Alloc& a) noexcept;

// 7. Створення алокатора для копійованого контейнера
static Alloc select_on_container_copy_construction(const Alloc& a);
