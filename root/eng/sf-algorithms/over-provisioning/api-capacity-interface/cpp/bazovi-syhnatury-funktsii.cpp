#include <memory>
#include <new>

// У C++ виділення та керування пам'яттю здійснюється через оператори new/delete
T* ptr = new T[count];
delete[] ptr;

// Для динамічних буферів використовується reserve() у контейнерах
std::vector<T> vec;
vec.reserve(new_cap);
