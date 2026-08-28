// Оголошення структури, яка успадковує всі типи замикань із пакета Ts
template <typename... Ts>
struct Overloaded : Ts... {
    // C++17 розпакування using-оголошень введення operator() усіх базових класів
    using Ts::operator()...;
};

// Посібник з виведення аргументів шаблону класу (CTAD Guide)
template <typename... Ts>
Overloaded(Ts...) -> Overloaded<Ts...>;
