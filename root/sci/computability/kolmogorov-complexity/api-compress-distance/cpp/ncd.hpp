// ncd.hpp — Сигнатури C++ RAII Класу
namespace ncd {

class Calculator {
public:
    explicit Calculator(Config config = Config{});
    ~Calculator();

    Calculator(const Calculator&) = delete;
    Calculator& operator=(Calculator&) = delete;

    Calculator(Calculator&&) noexcept;
    Calculator& operator=(Calculator&&) noexcept;

    // Обчислення відстані між двома спанами байтів
    [[nodiscard]] std::expected<double, Error> 
    distance(std::span<const uint8_t> a, std::span<const uint8_t> b) const;

    // Пакетне обчислення матриці подібності
    [[nodiscard]] std::expected<std::vector<double>, Error> 
    matrix(std::span<const std::span<const uint8_t>> items) const;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace ncd
