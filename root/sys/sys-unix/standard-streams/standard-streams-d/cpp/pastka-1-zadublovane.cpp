#include <iostream>
#include <unistd.h>

int main() {
    std::cout << "Початок обчислень..."; // Без std::endl або \n
    
    fork();

    std::cout << " Завершено.\n";
    return 0;
}
