#include <iostream>
#include <string_view>
#include <fnmatch.h>

bool matches_pattern(std::string_view filename, std::string_view pattern) {
    std::string null_file(filename);
    std::string null_pat(pattern);
    return fnmatch(null_pat.c_str(), null_file.c_str(), FNM_PATHNAME | FNM_PERIOD) == 0;
}

int main() {
    std::cout << std::boolalpha;
    std::cout << matches_pattern("backup.tar.gz", "*.tar.gz") << '\n'; // true
    std::cout << matches_pattern(".hidden.tar.gz", "*.tar.gz") << '\n'; // false (FNM_PERIOD)
    return 0;
}
