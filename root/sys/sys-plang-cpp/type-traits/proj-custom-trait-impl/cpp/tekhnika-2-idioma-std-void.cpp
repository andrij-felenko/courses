#include <iostream>
#include <type_traits>
#include <string>

// Первинний шаблон із додатковим параметром-заповнювачем (по замовчуванню void)
template<typename T, typename = void>
struct has_serialize : std::false_type {};

// Часткова спеціалізація за допомогою std::void_t та std::declval
template<typename T>
struct has_serialize<T, std::void_t<
    decltype(std::declval<const T&>().serialize())
>> : std::is_same<
    decltype(std::declval<const T&>().serialize()), 
    std::string
> {};

template<typename T>
inline constexpr bool has_serialize_v = has_serialize<T>::value;

// Тестові типи для перевірки
struct GoodClass {
    std::string serialize() const { return "data"; }
};

struct BadReturnClass {
    int serialize() const { return 42; } // Метод є, але тип повернення не std::string
};

struct NoMethodClass {};

int main() {
    std::cout << std::boolalpha;
    std::cout << "GoodClass: " << has_serialize_v<GoodClass> << "\n";            // true
    std::cout << "BadReturnClass: " << has_serialize_v<BadReturnClass> << "\n";  // false
    std::cout << "NoMethodClass: " << has_serialize_v<NoMethodClass> << "\n";    // false
}
