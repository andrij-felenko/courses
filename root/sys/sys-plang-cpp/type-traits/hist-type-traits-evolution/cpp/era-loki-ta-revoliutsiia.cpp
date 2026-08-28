// Концептуальна схема з бібліотеки Loki (2001 рік)
template <typename T>
struct TypeTraits {
    enum { isPointer = false };
    enum { isReference = false };
    enum { isConst = false };
    typedef T ParameterType;
};

// Часткова спеціалізація для вказівників
template <typename T>
struct TypeTraits<T*> {
    enum { isPointer = true };
    enum { isReference = false };
    enum { isConst = false };
    typedef T* ParameterType;
};
