#include <iostream>

void run_diff_example_cpp() {
    constexpr std::string_view text_old = "int main() {\n    printf(\"Hello\\n\");\n    return 0;\n}\n";
    constexpr std::string_view text_new = "int main() {\n    puts(\"Hello, World!\");\n    return 0;\n}\n";

    diff::Config cfg{
        .algorithm = diff::Algorithm::Myers,
        .context_lines = 2
    };

    diff::Engine engine(cfg);
    auto res = engine.compare(text_old, text_new);

    if (!res) {
        std::cerr << "Помилка порівняння: код " << static_cast<int>(res.error()) << '\n';
        return;
    }

    std::string patch = diff::Engine::format_unified(*res, "a/main.c", "b/main.c");
    std::cout << patch << '\n';
}
