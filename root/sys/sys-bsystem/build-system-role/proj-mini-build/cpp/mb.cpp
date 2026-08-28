// mb.cpp — мінімальна система збірки на ключах із вмісту.
//   збірка: c++ -std=c++20 -O2 -pthread mb.cpp -o mb
//   запуск: ./mb [-j N] [build.rules]
#include <algorithm>
#include <atomic>
#include <condition_variable>
#include <cstdint>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <mutex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <unordered_map>
#include <vector>

namespace fs = std::filesystem;

struct Rule {                       // локальний факт: що виходить, із чого, чим
    std::string out;
    std::vector<std::string> ins;
    std::string cmd;                // у команді живуть $out, $in, $ins
};

static std::string trim(const std::string& s) {
    const char* sp = " \t\r";
    auto b = s.find_first_not_of(sp);
    if (b == std::string::npos) return {};
    return s.substr(b, s.find_last_not_of(sp) - b + 1);
}

static std::vector<Rule> parseRules(const fs::path& path) {
    std::ifstream f(path);
    if (!f) throw std::runtime_error("не відкрити " + path.string());
    std::vector<Rule> rules;
    std::string line;
    for (int no = 1; std::getline(f, line); ++no) {
        std::string body = trim(line);
        if (body.empty() || body[0] == '#') continue;
        if (line[0] == ' ' || line[0] == '\t') {              // з відступом — команда
            if (rules.empty() || !rules.back().cmd.empty())
                throw std::runtime_error("рядок " + std::to_string(no) + ": команда не на місці");
            rules.back().cmd = body;
            continue;
        }
        auto colon = body.find(':');
        if (colon == std::string::npos)
            throw std::runtime_error("рядок " + std::to_string(no) + ": нема двокрапки");
        Rule r;
        r.out = trim(body.substr(0, colon));
        if (r.out.empty()) throw std::runtime_error("рядок " + std::to_string(no) + ": порожній вихід");
        std::istringstream is(body.substr(colon + 1));
        for (std::string w; is >> w;) r.ins.push_back(w);
        rules.push_back(std::move(r));
    }
    for (const auto& r : rules)
        if (r.cmd.empty()) throw std::runtime_error("правило «" + r.out + "» без команди");
    return rules;
}

static std::string expand(const Rule& r, const std::string& out) {
    std::string all;
    for (const auto& i : r.ins) { if (!all.empty()) all += ' '; all += i; }
    std::string s;
    for (size_t i = 0; i < r.cmd.size();) {
        if (!r.cmd.compare(i, 4, "$out"))      { s += out; i += 4; }
        else if (!r.cmd.compare(i, 4, "$ins")) { s += all; i += 4; }
        else if (!r.cmd.compare(i, 3, "$in"))  { s += r.ins.empty() ? std::string() : r.ins[0]; i += 3; }
        else                                   { s += r.cmd[i]; ++i; }
    }
    return s;
}
