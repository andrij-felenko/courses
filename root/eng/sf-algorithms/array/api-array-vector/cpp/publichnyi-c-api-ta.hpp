#include <memory>
#include <vector>

// 1. У C++ замість сирого malloc/free для динамічного масиву використовують std::unique_ptr<int[]>
std::size_t n = 100;
auto arr = std::make_unique<int[]>(n);

// 2. Або контейнер std::vector для динамічного розміру
std::vector<int> vec(n, 0); // Ініціалізація нулями

// 3. Зміна розміру у C++ (RAII автоматично звільняє пам'ять)
vec.resize(200);
