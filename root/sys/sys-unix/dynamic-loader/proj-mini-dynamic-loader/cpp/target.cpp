// target.cpp — Ідіоматичний C++20 еквівалент цільової програми
#include <iostream>
#include <string_view>

constexpr std::string_view msg = "Hello from dynamically loaded ELF!";

extern "C" int target_entry() {
    std::cout << msg << '\n';
    return 42;
}
