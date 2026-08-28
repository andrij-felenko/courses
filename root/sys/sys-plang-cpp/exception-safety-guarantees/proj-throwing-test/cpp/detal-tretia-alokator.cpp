template <class T>
struct Probing {
    using value_type = T;
    Probing() = default;
    template <class U> Probing(const Probing<U>&) noexcept {}

    T* allocate(std::size_t n) {
        wire().tick();                      // ось тут «пам'ять закінчилася»
        void* p = ::operator new(n * sizeof(T));
        ++tally().taken;
        return static_cast<T*>(p);
    }
    void deallocate(T* p, std::size_t) noexcept {
        ++tally().given;
        ::operator delete(p);
    }
};

template <class A, class B>
bool operator==(const Probing<A>&, const Probing<B>&) noexcept { return true; }
template <class A, class B>
bool operator!=(const Probing<A>&, const Probing<B>&) noexcept { return false; }
