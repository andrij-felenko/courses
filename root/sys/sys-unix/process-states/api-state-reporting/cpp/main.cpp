#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <system_error>

namespace fs = std::filesystem;

static std::string read_first_line(const fs::path& p)
{
    std::ifstream f(p);
    if (!f)
        return {};
    std::string line;
    std::getline(f, line);
    return line;
}

int main(int argc, char** argv)
{
    if (argc != 2) {
        std::cerr << "вжиток: " << argv[0] << " <pid>\n";
        return 2;
    }

    fs::path task_dir = fs::path("/proc") / argv[1] / "task";
    std::error_code ec;
    auto it = fs::directory_iterator(task_dir, ec);
    if (ec) {
        std::cerr << task_dir << ": " << ec.message() << "\n";
        return 1;
    }

    for (const auto& entry : it) {
        if (!entry.is_directory())
            continue;

        std::string tid = entry.path().filename().string();
        std::string stat = read_first_line(entry.path() / "stat");
        if (stat.empty())
            continue;

        auto pos = stat.rfind(')');
        if (pos == std::string::npos || pos + 2 >= stat.size())
            continue;
        char state = stat[pos + 2];

        std::string wchan = read_first_line(entry.path() / "wchan");
        if (wchan.empty())
            wchan = "0";

        std::cout << tid;
        if (tid.size() < 7)
            std::cout << std::string(7 - tid.size(), ' ');
        std::cout << " " << state << "  " << wchan << "\n";
    }
    return 0;
}
