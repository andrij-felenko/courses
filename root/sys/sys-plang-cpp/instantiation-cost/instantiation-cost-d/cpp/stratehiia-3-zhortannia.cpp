// Базова реалізація для бестипових вказівників void*
template <>
class Vector<void*> : private RawVectorBase {
public:
    void push_back(void* val);
    void* get(std::size_t idx) const;
};

// Часткова спеціалізація для всіх вказівників T*
template <typename T>
class Vector<T*> : private Vector<void*> {
public:
    void push_back(T* val) {
        Vector<void*>::push_back(static_cast<void*>(val));
    }

    T* get(std::size_t idx) const {
        return static_cast<T*>(Vector<void*>::get(idx));
    }
};
