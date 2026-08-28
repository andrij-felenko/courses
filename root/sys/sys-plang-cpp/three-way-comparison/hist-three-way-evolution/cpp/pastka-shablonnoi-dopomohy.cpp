namespace std::rel_ops {
    template <class T>
    bool operator!=(const T& x, const T& y) { return !(x == y); }

    template <class T>
    bool operator>(const T& x, const T& y) { return y < x; }

    template <class T>
    bool operator<=(const T& x, const T& y) { return !(y < x); }

    template <class T>
    bool operator>=(const T& x, const T& y) { return !(x < y); }
}
