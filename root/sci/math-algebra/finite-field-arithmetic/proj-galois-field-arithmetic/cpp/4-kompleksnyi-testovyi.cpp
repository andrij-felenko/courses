int main() {
    galois::GaloisField256 gf;
    std::cout << "=== Перевірка C++ класу GaloisField256 ===\n";

    int errors = 0;
    for (uint32_t i = 1; i < 256; ++i) {
        const uint8_t elem = static_cast<uint8_t>(i);
        const auto inv_opt = galois::gf_inverse(elem);

        if (!inv_opt.has_value()) {
            std::cerr << "ПОМИЛКА: відсутній обернений елемент для " << i << "\n";
            errors++;
            continue;
        }

        const uint8_t prod = gf.multiply(elem, inv_opt.value());
        if (prod != 1) {
            std::cerr << "ПОМИЛКА: elem=0x" << std::hex << static_cast<int>(elem)
                      << ", inv=0x" << static_cast<int>(inv_opt.value())
                      << ", prod=0x" << static_cast<int>(prod) << "\n";
            errors++;
        }
    }

    if (errors == 0) {
        std::cout << "УСПІХ: C++20 реалізація пройшла всі 255 перевірок коректності без жодного збою!\n";
    } else {
        std::cerr << "ЗБОЙ: Тестовий стенд виявив " << errors << " помилок!\n";
    }
    return errors;
}
