#include <stdexcept>
#include <string>
#include <vector>

generator<int> parsed(const std::vector<std::string>& rows) {
    for (const std::string& r : rows) {
        if (r.empty()) throw std::runtime_error{ "порожній рядок" };
        co_yield std::stoi(r);
    }
}

int main() {
    const std::vector<std::string> rows{ "10", "20", "", "40" };
    try {
        for (int v : parsed(rows)) std::cout << v << ' ';   // 10 20
    } catch (const std::exception& e) {
        std::cout << "\nобірвалося: " << e.what() << '\n';
    }
}
