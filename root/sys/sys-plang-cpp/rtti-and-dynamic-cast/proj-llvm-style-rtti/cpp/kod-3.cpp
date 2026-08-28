template <class To, class From>
bool isa(const From* p) { return To::classof(p); }

template <class To, class From>
To* dyn_cast(From* p) { return isa<To>(p) ? static_cast<To*>(p) : nullptr; }

template <class To, class From>
To* cast(From* p) {
    assert(isa<To>(p) && "cast<> argument of incompatible type");
    return static_cast<To*>(p);
}
