// Оголошення параметра-шаблона Container, який сам приймає один параметр типу
template <typename T, template <typename> class Container>
class StackAdapter {
public:
    void push(const T& val) { storage_.push_back(val); }
    void pop() { storage_.pop_back(); }
private:
    Container<T> storage_;
};

// До C++17 у списку параметрів-шаблонів вимагалося винятково слово class.
// Починаючи з C++17, дозволено використовувати typename:
template <typename T, template <typename...> typename Container>
class ModernStackAdapter {
    Container<T> storage_;
};

// Використання:
StackAdapter<int, std::vector> int_stack;   // storage_ матиме тип std::vector<int>
StackAdapter<double, std::list> real_stack; // storage_ матиме тип std::list<double>
