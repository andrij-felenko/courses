#include <vector>
#include <string>
#include <format>

// Фільтрація експортованих змінних на C++
std::vector<std::string> build_export_environment(const std::vector<shell::ShellVariable>& var_table) {
    std::vector<std::string> envp_strings;
    for (const auto& var : var_table) {
        if (var.attributes & shell::ShellVariable::Exported) {
            envp_strings.push_back(std::format("{}={}", var.name, var.value));
        }
    }
    return envp_strings;
}
