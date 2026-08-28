template <typename T1, typename T2>
struct pair {
    T1 first;
    T2 second;

    pair() : first(), second() {}
    pair(const T1& a, const T2& b) : first(a), second(b) {}
    
    template <typename U1, typename U2>
    pair(const pair<U1, U2>& p) : first(p.first), second(p.second) {}
};
