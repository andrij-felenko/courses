template <typename T, template <typename...> class Container>
class StackAdapter {
public:
    void push(const T& val) { storage_.push_back(val); }
private:
    Container<T> storage_; // Компілятор інстанціює Container під конкретний тип T!
};

// Використання:
StackAdapter<int, std::vector> vec_stack;
StackAdapter<int, std::list>   list_stack;
