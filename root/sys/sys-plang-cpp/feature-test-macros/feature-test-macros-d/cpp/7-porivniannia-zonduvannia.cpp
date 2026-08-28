#include <iostream>

// У мові C++ зондування виконується гранулярно для кожної окремої можливості
#if defined(__has_include)
    #if __has_include(<version>)
        #include <version>
    #endif
#endif

#if defined(__cpp_static_assert) && __cpp_static_assert >= 201411L
    // C++17 дозволяє static_assert без обов'язкового текстового повідомлення
    static_assert(sizeof(int) >= 4);
#elif defined(__cpp_static_assert) && __cpp_static_assert >= 200410L
    // C++11 вимагає текстовий рядок другим аргументом
    static_assert(sizeof(int) >= 4, "Помилка: int занадто малий!");
#endif

int main() {
    std::cout << "Компіляція програми на сучасному C++\n";
    return 0;
}
