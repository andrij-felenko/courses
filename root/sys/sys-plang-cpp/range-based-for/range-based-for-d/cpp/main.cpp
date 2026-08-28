{
    оператор-ініціалізації              // з C++20, необов'язковий
    auto&& __range = вираз-діапазону;
    auto __begin   = begin-вираз;
    auto __end     = end-вираз;
    for ( ; __begin != __end; ++__begin) {
        оголошення = *__begin;
        тіло
    }
}
