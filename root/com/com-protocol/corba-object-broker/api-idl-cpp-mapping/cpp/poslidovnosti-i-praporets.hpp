class Seq {                                     // необмежена sequence<T>
public:
    Seq();
    Seq(ULong max);
    Seq(ULong max, ULong length, T* data, Boolean release = FALSE);

    ULong   maximum() const;
    void    length(ULong);   ULong length() const;
    T&      operator[](ULong index);
    Boolean release() const;
    void    replace(ULong max, ULong length, T* data, Boolean release = FALSE);
    T*      get_buffer(Boolean orphan = FALSE);

    static T*   allocbuf(ULong nelems);
    static void freebuf(T*);
};
// обмежена sequence<T,N> — те саме, але без параметра max у конструкторах
