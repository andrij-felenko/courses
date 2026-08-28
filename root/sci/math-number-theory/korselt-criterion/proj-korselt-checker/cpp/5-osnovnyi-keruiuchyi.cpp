int main(int argc, char* argv[]) {
    uint64_t n = getInput(argc, argv);
    
    // Перевірка на достатню величину числа
    if (n < 4) {
        std::cout << n << " не є складеним числом, отже апріорі не є числом Кармайкла.\n";
        return 0;
    }
    
    std::vector<uint64_t> factors = getPrimeFactors(n);
    
    // Елементарна перевірка, чи є задане число простим
    if (factors.size() == 1 && factors[0] == n) {
        std::cout << n << " є звичайним простим числом, а зовсім не числом Кармайкла.\n";
        return 0;
    }
    
    // Запуск першої частини критерію Корсельта
    if (!isSquareFree(n, factors)) {
        std::cout << n << " має повні квадратні дільники, тому не задовольняє критерію Корсельта.\n";
        return 0;
    }
    
    // Запуск другої частини критерію Корсельта
    if (!satisfiesKorseltDivisibility(n, factors)) {
        std::cout << n << " не задовольняє обов'язковій умові подільності Корсельта: (p - 1) | (n - 1).\n";
        return 0;
    }
    
    // Фінальний успішний висновок
    std::cout << n << " успішно проходить весь критерій Корсельта! Це справжнє число Кармайкла.\n";
    std::cout << "Його повна факторизація: ";
    for (size_t i = 0; i < factors.size(); ++i) {
        std::cout << factors[i] << (i < factors.size() - 1 ? " * " : "");
    }
    std::cout << "\n";
    
    return 0;
}
