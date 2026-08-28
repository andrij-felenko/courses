// fast_stream_join.cpp — Ідіоматичне реляційне з'єднання на C++20
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <memory>
#include <system_error>

constexpr char DELIM = '\t';

struct Record {
    std::string line;
    std::string_view key;
    std::string_view value;

    static Record parse(std::string raw_line) {
        Record rec;
        rec.line = std::move(raw_line);
        std::string_view sv(rec.line);
        
        auto pos = sv.find(DELIM);
        if (pos == std::string_view::npos) {
            rec.key = sv;
            rec.value = {};
        } else {
            rec.key = sv.substr(0, pos);
            rec.value = sv.substr(pos + 1);
        }
        return rec;
    }
};

int main(int argc, char *argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " file1.tsv file2.tsv\n";
        return 1;
    }

    // Прискорення стандартного I/O потоків C++
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);

    std::ifstream stream1(argv[1]);
    std::ifstream stream2(argv[2]);

    if (!stream1 || !stream2) {
        std::cerr << "Помилка відкриття файлів для зчитування\n";
        return 1;
    }

    std::string raw1, raw2;
    bool has1 = static_cast<bool>(std::getline(stream1, raw1));
    bool has2 = static_cast<bool>(std::getline(stream2, raw2));

    while (has1 && has2) {
        auto rec1 = Record::parse(raw1);
        auto rec2 = Record::parse(raw2);

        if (rec1.key == rec2.key) {
            // Ключі збіглися: прямий запис у stdout без проміжних алокацій
            std::cout << rec1.key << DELIM << rec1.value << DELIM << rec2.value << '\n';
            has1 = static_cast<bool>(std::getline(stream1, raw1));
            has2 = static_cast<bool>(std::getline(stream2, raw2));
        } else if (rec1.key < rec2.key) {
            has1 = static_cast<bool>(std::getline(stream1, raw1));
        } else {
            has2 = static_cast<bool>(std::getline(stream2, raw2));
        }
    }

    return 0;
}
