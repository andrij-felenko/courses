// glob_filter.cpp — те саме, що робить `rm !(*.txt|*.md)` з увімкненим extglob,
// але зібране інакше, ніж у C: каталог обходить std::filesystem, а зіставлення
// з маскою лишається за fnmatch(3) — це справжній POSIX-матчер, той самий,
// яким користується оболонка. Одна маска на каталог, решта — винятки.
//
// Збірка: c++ -std=c++20 -Wall -Wextra -o glob_filter glob_filter.cpp
// Запуск: ./glob_filter /tmp/demo '*' '*.txt' '*.md'
#include <algorithm>
#include <filesystem>
#include <iostream>
#include <span>
#include <string>
#include <string_view>
#include <vector>

#include <fnmatch.h>

namespace fs = std::filesystem;

namespace {

// FNM_PERIOD повторює правило POSIX: провідна крапка не збігається з '*' і '?'.
bool matches(const std::string& pattern, const std::string& name)
{
    return ::fnmatch(pattern.c_str(), name.c_str(), FNM_PERIOD) == 0;
}

struct selection {
    std::vector<fs::path> kept;      // під маску підпали, під винятки — ні
    std::vector<fs::path> dropped;   // маску пройшли, але виняток їх забрав
};

selection select_entries(const fs::path& dir, const std::string& mask,
                         std::span<const std::string> excludes)
{
    selection out;

    for (const fs::directory_entry& entry : fs::directory_iterator{dir}) {
        const std::string name = entry.path().filename().string();
        if (!matches(mask, name)) {
            continue;
        }
        const bool excluded = std::ranges::any_of(
            excludes, [&](const std::string& pattern) { return matches(pattern, name); });

        (excluded ? out.dropped : out.kept).push_back(entry.path());
    }

    // directory_iterator порядку не обіцяє, а глобінг оболонки віддає
    // імена впорядкованими — доводимо результат до тієї ж поведінки.
    std::ranges::sort(out.kept);
    std::ranges::sort(out.dropped);
    return out;
}

void print(std::string_view title, const std::vector<fs::path>& paths)
{
    std::cout << title << " (" << paths.size() << "):\n";
    for (const fs::path& path : paths) {
        std::cout << "  " << path.string() << '\n';
    }
}

}  // namespace

int main(int argc, char** argv)
{
    const std::span<char* const> args{argv, static_cast<std::size_t>(argc)};
    if (args.size() < 3) {
        std::cerr << "вжиток: " << args[0] << " <каталог> <маска> [виняток…]\n";
        return 2;
    }

    const fs::path dir{args[1]};
    const std::string mask{args[2]};
    const std::vector<std::string> excludes{args.begin() + 3, args.end()};

    try {
        const selection sel = select_entries(dir, mask, excludes);
        if (sel.kept.empty() && sel.dropped.empty()) {
            // Порожній результат: оболонка за POSIX лишила б тут саму маску.
            std::cout << "маска «" << mask << "» не збіглася з жодним іменем\n";
            return 1;
        }
        print("лишається", sel.kept);
        print("відсіяно винятками", sel.dropped);
    } catch (const fs::filesystem_error& err) {
        std::cerr << "не вдалося обійти каталог: " << err.what() << '\n';
        return 1;
    }

    return 0;
}
