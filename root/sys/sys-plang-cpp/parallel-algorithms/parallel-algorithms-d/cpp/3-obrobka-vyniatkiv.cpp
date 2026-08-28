// Правильний підхід: локальна ізоляція помилок у паралельному коді
#include <algorithm>
#include <execution>
#include <vector>
#include <optional>
#include <iostream>

struct ProcessResult {
    int id;
    std::optional<double> value;
    std::string error_message;
};

void process_data_safely(const std::vector<int>& inputs, std::vector<ProcessResult>& outputs) {
    outputs.resize(inputs.size());

    std::transform(std::execution::par, inputs.begin(), inputs.end(), outputs.begin(), [](int x) {
        ProcessResult res;
        res.id = x;
        try {
            if (x < 0) {
                throw std::invalid_argument("Від'ємне значення неприпустиме");
            }
            res.value = 100.0 / x; // Можливе ділення на нуль або помилка
        } catch (const std::exception& ex) {
            res.value = std::nullopt;
            res.error_message = ex.what();
        } catch (...) {
            res.value = std::nullopt;
            res.error_message = "Невідома помилка";
        }
        return res;
    });
}
