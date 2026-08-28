template<typename T>
void by_ref(T& x);

template<typename T>
void by_const_ref(const T& x);

const int val = 100;
int raw_array[8];

by_ref(val);          // T = const int, параметр x: const int&
by_const_ref(val);    // T = int, параметр x: const int&
by_ref(raw_array);    // T = int[8], параметр x: int(&)[8]
