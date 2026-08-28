// Порівняння синтаксису C++11 та C++14 під час обмеження SFINAE:

// C++11: багатослівний синтаксис із typename та ::type
template<typename T, 
         typename = typename std::enable_if<std::is_integral<T>::value>::type>
void process_number_c11(T val) {
    typedef typename std::remove_reference<T>::type CleanType;
    typedef typename std::decay<T>::type DecayedType;
}

// C++14: компактний синтаксис через псевдоніми _t
template<typename T, 
         typename = std::enable_if_t<std::is_integral<T>::value>>
void process_number_c14(T val) {
    using CleanType   = std::remove_reference_t<T>;
    using DecayedType = std::decay_t<T>;
}
