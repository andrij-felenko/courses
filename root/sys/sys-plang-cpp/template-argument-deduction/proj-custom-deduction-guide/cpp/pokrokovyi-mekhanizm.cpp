void run_variant_dispatcher() {
    using Message = std::variant<int, double, std::string>;

    Message msg1 = 42;
    Message msg2 = 3.14159;
    Message msg3 = std::string("Системна подія #104");

    auto handler = Overloaded{
        [](int val) {
            std::cout << "[Обробник Int]: значення = " << val << '\n';
        },
        [](double val) {
            std::cout << "[Обробник Double]: значення = " << val << '\n';
        },
        [](const std::string& val) {
            std::cout << "[Обробник String]: довжина = " << val.length() 
                      << ", вміст = " << val << '\n';
        }
    };

    std::visit(handler, msg1);
    std::visit(handler, msg2);
    std::visit(handler, msg3);
}
