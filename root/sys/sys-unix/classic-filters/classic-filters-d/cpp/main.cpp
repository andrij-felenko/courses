#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>
#include <sstream>

// Ідіоматична C++ реалізація з використанням string_view та unordered_map
void process_stream_in_process_cpp(std::istream& input) {
    std::unordered_map<std::string, long> counts;
    std::string line;

    while (std::getline(input, line)) {
        std::string_view sv(line);
        if (sv.find("ERROR") == std::string_view::npos) {
            continue; // Етап grep
        }

        // Етап cut: виділення 4-го стовпця
        std::size_t start = 0;
        int col = 1;
        std::string_view col4;

        while (start < sv.size()) {
            std::size_t end = sv.find_first_of(" \t", start);
            if (end == std::string_view::npos) end = sv.size();
            
            if (end > start) {
                if (col == 4) {
                    col4 = sv.substr(start, end - start);
                    break;
                }
                col++;
            }
            start = end + 1;
        }

        if (!col4.empty()) {
            counts[std::string(col4)]++; // Етап uniq -c
        }
    }

    for (const auto& [key, count] : counts) {
        std::cout << count << " " << key << "\n";
    }
}
