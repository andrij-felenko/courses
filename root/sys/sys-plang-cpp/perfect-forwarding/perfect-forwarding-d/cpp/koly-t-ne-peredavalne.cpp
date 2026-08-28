template <class T> void a(T&& x);                // так
template <class T> void b(const T&& x);          // ні: const псує форму — лише rvalue
template <class T> void c(std::vector<T>&& v);   // ні: T усередині типу — лише rvalue
template <class... A> void d(A&&... args);       // так, для кожного елемента пакета
auto&& r = make_thing();                         // так: auto виводиться

template <class T>
struct Box {
    void push(T&& v);                            // НІ: T зафіксований класом
    template <class U> void emplace(U&& v);      // так: U виводиться з виклику
};
