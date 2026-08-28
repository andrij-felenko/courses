// tools/schema_compiler.cpp
#include <iostream>
#include <fstream>
#include <string_view>

int main(int argc, char* argv[]) {
    if (argc < 5) return 1;
    std::ofstream out(argv[4]);
    if (!out) return 1;
    out << "// Автоматично згенерований C++-файл\n";
    out << "#include <string_view>\n";
    out << "std::string_view getSchemaVersion() noexcept { return \"1.0.0\"; }\n";
    return 0;
}
