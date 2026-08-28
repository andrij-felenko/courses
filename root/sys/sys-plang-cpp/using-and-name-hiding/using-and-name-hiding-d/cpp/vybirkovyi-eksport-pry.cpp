template <typename T>
class SafeStack : private std::vector<T> {
public:
    // Робимо публічними лише ті операції vector, які потрібні стеку:
    using std::vector<T>::empty;
    using std::vector<T>::size;

    void push(const T& value) {
        this->push_back(value);
    }

    void pop() {
        if (!empty()) {
            this->pop_back();
        }
    }

    const T& top() const {
        return this->back();
    }
    // Операції insert, erase, operator[] залишаються схованими в private!
};
