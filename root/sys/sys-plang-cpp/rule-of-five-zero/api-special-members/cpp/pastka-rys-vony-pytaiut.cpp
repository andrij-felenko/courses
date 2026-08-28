#include <cstdio>
#include <memory>
#include <string>
#include <type_traits>

template <class T>
void probe(const char* name) {
    std::printf("%-16s trivially_copyable=%d  nothrow_move=%d  trivially_dtor=%d\n",
                name,
                (int)std::is_trivially_copyable_v<T>,
                (int)std::is_nothrow_move_constructible_v<T>,
                (int)std::is_trivially_destructible_v<T>);
}

int main() {
    probe<int>("int");                          // 1  1  1
    probe<std::unique_ptr<int>>("unique_ptr");  // 0  1  0
    probe<std::string>("string");               // 0  1  0
}
