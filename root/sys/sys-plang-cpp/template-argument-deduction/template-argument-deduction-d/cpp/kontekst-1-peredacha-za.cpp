template<typename T>
void by_value(T x);

const int a = 5;
const int& ref = a;
int buffer[16];

by_value(a);      // T = int, параметр x: int
by_value(ref);    // T = int, параметр x: int
by_value(buffer); // T = int*, параметр x: int*
by_value("text"); // T = const char*, параметр x: const char*
