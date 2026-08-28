// plugins/markdown_exporter.cpp — сторонній файл, зібраний у markdown_exporter.so:
//   g++ -std=c++17 -shared -fPIC markdown_exporter.cpp -o markdown_exporter.so
#include "contract.h"

extern "C" const int PLUGIN_API = 3;      // під яку версію контракту зібрано

namespace {                               // клас не світиться назовні
class MarkdownExporter : public Exporter {
public:
    std::string extension() const override { return "md"; }
    std::vector<std::uint8_t> exportDoc(const Document& doc) const override {
        std::string text;
        for (const auto& b : doc.blocks) {
            if (!text.empty()) text += "\n\n";
            text += "# " + b.title + "\n\n" + b.body;
        }
        return {text.begin(), text.end()};   // рядок -> байти
    }
};
}  // namespace

extern "C" void plugin_register(Host& host) {   // умовлена точка входу
    static MarkdownExporter exporter;            // живе весь час роботи ядра
    host.registerExporter(&exporter);
}
