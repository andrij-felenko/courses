// Ідіоматична обгортка історії команд на C++20
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <fstream>
#include <stdexcept>
#include <iostream>

class CommandHistory {
public:
    struct Entry {
        std::string command;
        std::chrono::system_clock::time_point timestamp;
    };

    void add_entry(std::string_view cmd) {
        if (cmd.empty()) return;
        entries_.push_back(Entry{
            std::string(cmd),
            std::chrono::system_clock::now()
        });
    }

    void save_to_file(const std::string &path) const {
        std::ofstream out(path, std::ios::out | std::ios::trunc);
        if (!out.is_open()) {
            throw std::runtime_error("Failed to open history file for writing: " + path);
        }
        for (const auto &entry : entries_) {
            auto epoch = std::chrono::duration_cast<std::chrono::seconds>(
                entry.timestamp.time_since_epoch()
            ).count();
            out << '#' << epoch << '\n' << entry.command << '\n';
        }
    }

private:
    std::vector<Entry> entries_;
};
