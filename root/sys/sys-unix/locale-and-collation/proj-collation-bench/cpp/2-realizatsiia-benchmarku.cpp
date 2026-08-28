// C++17: Об'єктно-орієнтований бенчмарк з використанням std::chrono та std::locale
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <chrono>
#include <locale>
#include <memory>

class LocaleBenchmark {
private:
    std::vector<std::string> dataset_;

    void generate_data(std::size_t count) {
        static const std::vector<std::string> words = {
            "апельсин", "Apple", "банан", "Бджола", "вишня", "Арбуз", 
            "гараж", "Ґрунт", "100", "20", "Zebra", "яблуко", "єнот", "Їжак"
        };
        dataset_.reserve(count);
        for (std::size_t i = 0; i < count; ++i) {
            std::string s = words[i % words.size()] + "_" + 
                            words[(i * 3) % words.size()] + "_" + std::to_string(i);
            dataset_.push_back(std::move(s));
        }
    }

public:
    explicit LocaleBenchmark(std::size_t count) {
        generate_data(count);
    }

    void execute() {
        using namespace std::chrono;

        // 1. Швидке двійкове сортування (байтове)
        {
            auto data = dataset_;
            auto start = high_resolution_clock::now();
            std::sort(data.begin(), data.end(), [](const std::string& a, const std::string& b) {
                return a < b;
            });
            auto elapsed = duration_cast<duration<double>>(high_resolution_clock::now() - start);
            std::cout << "[C++] std::sort (байтове порівняння / C-locale): " 
                      << elapsed.count() << " сек\n";
        }

        // 2. Мовне сортування через std::locale та std::collate
        {
            auto data = dataset_;
            std::locale loc("uk_UA.UTF-8");
            const auto& coll = std::use_facet<std::collate<char>>(loc);

            auto start = high_resolution_clock::now();
            std::sort(data.begin(), data.end(), [&coll](const std::string& a, const std::string& b) {
                return coll.compare(a.data(), a.data() + a.size(),
                                    b.data(), b.data() + b.size()) < 0;
            });
            auto elapsed = duration_cast<duration<double>>(high_resolution_clock::now() - start);
            std::cout << "[C++] std::sort з std::collate::compare (uk_UA.UTF-8): " 
                      << elapsed.count() << " сек\n";
        }

        // 3. Оптимізоване сортування через кешування ключів transform
        {
            auto data = dataset_;
            std::locale loc("uk_UA.UTF-8");
            const auto& coll = std::use_facet<std::collate<char>>(loc);

            auto start = high_resolution_clock::now();

            struct KeyWrapper {
                std::string original;
                std::string key;
            };

            std::vector<KeyWrapper> keys;
            keys.reserve(data.size());

            for (const auto& str : data) {
                keys.push_back({str, coll.transform(str.data(), str.data() + str.size())});
            }

            std::sort(keys.begin(), keys.end(), [](const KeyWrapper& a, const KeyWrapper& b) {
                return a.key < b.key;
            });

            auto elapsed = duration_cast<duration<double>>(high_resolution_clock::now() - start);
            std::cout << "[C++] std::sort з трансформованими ключами (transform): " 
                      << elapsed.count() << " сек\n";
        }
    }
};

int main() {
    try {
        LocaleBenchmark bench(300000);
        bench.execute();
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання бенчмарку: " << e.what() << "\n";
    }
    return 0;
}
