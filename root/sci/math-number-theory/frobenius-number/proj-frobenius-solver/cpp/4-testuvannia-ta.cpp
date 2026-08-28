int main() {
    try {
        std::vector<long long> coins2 = {3, 5};
        std::cout << "g(3, 5) = " << frobenius_number(coins2) << std::endl;
        
        std::vector<long long> coins3 = {6, 9, 20};
        std::cout << "g(6, 9, 20) = " << frobenius_number(coins3) << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << std::endl;
    }
    return 0;
}
