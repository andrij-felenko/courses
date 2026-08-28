#include <iostream>

int val = 100; // [A] Глобальна змінна

int main() {
    int val = 200; // [B] Затінює глобальну [A]
    std::cout << "Local val = " << val << '\n'; // 200

    {
        int val = 300; // [C] Затінює локальну [B]
        std::cout << "Inner block val = " << val << '\n'; // 300
        
        // У C++ унарний оператор :: дозволяє дістатися до глобальної змінної [A]
        std::cout << "Global val via ::val = " << ::val << '\n'; // 100
    }

    std::cout << "Back to local val = " << val << '\n'; // 200
    return 0;
}
