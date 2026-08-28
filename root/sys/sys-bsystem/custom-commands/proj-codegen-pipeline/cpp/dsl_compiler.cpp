// tools/dsl_compiler.cpp
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <filesystem>
#include <regex>

namespace fs = std::filesystem;

struct SchemaCompiler {
    fs::path input_path;
    fs::path out_dir;
    fs::path depfile_path;
    std::vector<fs::path> tracked_dependencies;

    bool parse_and_collect_deps(const fs::path& file_path) {
        std::ifstream file(file_path);
        if (!file.is_open()) {
            std::cerr << "[dsl_compiler] Помилка відкриття файлу: " << file_path << "\n";
            return false;
        }

        fs::path canonical = fs::absolute(file_path);
        for (const auto& existing : tracked_dependencies) {
            if (existing == canonical) return true; // Захист від циклічних імпортів
        }
        tracked_dependencies.push_back(canonical);

        std::string line;
        std::regex include_regex(R"(^\s*include\s*\"([^\"]+)\")");

        while (std::getline(file, line)) {
            std::smatch match;
            if (std::regex_search(line, match, include_regex)) {
                fs::path included = file_path.parent_path() / match[1].str();
                if (!parse_and_collect_deps(included)) {
                    return false;
                }
            }
        }
        return true;
    }

    bool emit_code() {
        fs::create_directories(out_dir);
        fs::path hpp_path = out_dir / "messages.hpp";
        fs::path cpp_path = out_dir / "messages.cpp";

        std::ofstream hpp(hpp_path);
        if (!hpp) return false;
        hpp << "#pragma once\n"
            << "#include <cstdint>\n\n"
            << "struct TelemetryFrame {\n"
            << "    uint32_t timestamp;\n"
            << "    float voltage;\n"
            << "    float current;\n"
            << "};\n\n"
            << "void print_frame(const TelemetryFrame& frame);\n";

        std::ofstream cpp(cpp_path);
        if (!cpp) return false;
        cpp << "#include \"messages.hpp\"\n"
            << "#include <iostream>\n\n"
            << "void print_frame(const TelemetryFrame& frame) {\n"
            << "    std::cout << \"[Telemetry] T: \" << frame.timestamp\n"
            << "              << \" V: \" << frame.voltage\n"
            << "              << \" I: \" << frame.current << \"\\n\";\n"
            << "}\n";

        return true;
    }

    bool emit_depfile() {
        if (depfile_path.empty()) return true;

        fs::create_directories(depfile_path.parent_path());
        std::ofstream dep(depfile_path);
        if (!dep) return false;

        fs::path target_out = out_dir / "messages.cpp";
        
        // Синтаксис Makefile depfile: target: dep1 dep2 ...
        dep << target_out.generic_string() << ":";
        for (const auto& d : tracked_dependencies) {
            dep << " " << d.generic_string();
        }
        dep << "\n";
        return true;
    }
};

int main(int argc, char* argv[]) {
    SchemaCompiler compiler;
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--input" && i + 1 < argc) compiler.input_path = argv[++i];
        else if (arg == "--out-dir" && i + 1 < argc) compiler.out_dir = argv[++i];
        else if (arg == "--depfile" && i + 1 < argc) compiler.depfile_path = argv[++i];
    }

    if (compiler.input_path.empty() || compiler.out_dir.empty()) {
        std::cerr << "Використання: dsl_compiler --input <file> --out-dir <dir> [--depfile <file>]\n";
        return 1;
    }

    if (!compiler.parse_and_collect_deps(compiler.input_path)) return 2;
    if (!compiler.emit_code()) return 3;
    if (!compiler.emit_depfile()) return 4;

    return 0;
}
