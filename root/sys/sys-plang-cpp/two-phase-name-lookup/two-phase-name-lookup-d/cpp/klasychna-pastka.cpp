template <typename T>
class Base {
public:
    void clear_cache() {
        // очищення ресурсів
    }
protected:
    int flags = 0;
};

template <typename T>
class Derived : public Base<T> {
public:
    void reset() {
        // ПОМИЛКА КОМПІЛЯЦІЇ: 'clear_cache' was not declared in this scope
        clear_cache(); 
        
        // ПОМИЛКА КОМПІЛЯЦІЇ: 'flags' was not declared in this scope
        flags = 0; 
    }
};
