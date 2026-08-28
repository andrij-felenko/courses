template <class T> class Weak;   // наперед: блок і Shared на нього посилаються

template <class T>
struct ControlBlock {
    T*   obj;        // сам керований об'єкт (nullptr після знищення)
    long strong;     // скільки Shared володіють об'єктом
    long weak;       // скільки Weak спостерігають за блоком

    explicit ControlBlock(T* p) : obj(p), strong(1), weak(0) {}

    void retain() { ++strong; }              // нове сильне посилання

    void release() {                         // сильне посилання зникло
        if (--strong == 0) {                 // пішов останній власник
            delete obj;                      // ← ~T() тут-таки, детерміновано
            obj = nullptr;
            if (weak == 0)                    // і жоден Weak не дивиться на блок
                delete this;                 // → блок теж можна віддати
        }
    }

    void weak_retain() { ++weak; }           // новий спостерігач

    void weak_release() {                    // спостерігач зник
        if (--weak == 0 && strong == 0)      // ні власників, ні спостерігачів
            delete this;                     // → блок нікому не потрібен
    }
};
