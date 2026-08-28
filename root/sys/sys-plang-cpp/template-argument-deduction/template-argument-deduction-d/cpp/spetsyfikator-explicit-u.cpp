template<typename T>
struct UniqueHandle {
    explicit UniqueHandle(T* ptr);
};

// Керівне правило з explicit
template<typename T>
explicit UniqueHandle(T*) -> UniqueHandle<T>;

UniqueHandle h1(new int(5));   // УСПІХ: пряма ініціалізація
// UniqueHandle h2 = new int(5); // ПОМИЛКА: explicit блокує копіювальну ініціалізацію через '='
