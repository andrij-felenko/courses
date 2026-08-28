std::generator<int> count_to_three() {
    co_yield 1;
    co_yield 2;
    co_yield 3;
}

int main() {
    auto gen = count_to_three(); // Крок 1: Створення корутини
    for (int val : gen) {        // Крок 2, 3, 4: Ітерація
        std::cout << val << "\n";
    }
}
