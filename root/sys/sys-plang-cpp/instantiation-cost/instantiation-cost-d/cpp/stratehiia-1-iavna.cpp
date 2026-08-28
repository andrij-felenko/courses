// Array.hpp
template <typename T>
class Array {
public:
    void process();
    // ...
};

// Заборона неявної інстанціації у файлах, що включають цей заголовок
extern template class Array<int>;
extern template class Array<double>;
