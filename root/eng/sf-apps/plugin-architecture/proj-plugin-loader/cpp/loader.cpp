// loader.cpp — ядро. Збірка: g++ -std=c++17 loader.cpp -ldl -o core
#include "contract.h"
#include <dlfcn.h>          // dlopen, dlsym, dlclose, dlerror
#include <filesystem>
#include <iostream>
#include <map>
#include <algorithm>
#include <stdexcept>

namespace fs = std::filesystem;

// проста заміна логера — у реальному ядрі це ваш logger
static void warn(const std::string& m) { std::cerr << "WARN: " << m << '\n'; }
static void info(const std::string& m) { std::cerr << "INFO: " << m << '\n'; }

class ExportRegistry {
    // Серце ядра: сюди плагіни складають себе, звідси ядро їх бере.
    std::map<std::string, Exporter*> byExt;
public:
    void add(Exporter* e) { byExt[e->extension()] = e; }   // "register" — слово C++
    bool has(const std::string& ext) const { return byExt.count(ext) != 0; }
    std::vector<std::uint8_t> exportAs(const std::string& ext, const Document& doc) {
        return byExt.at(ext)->exportDoc(doc);   // .at кине out_of_range, якщо плагіна нема
    }
};

class HostImpl : public Host {
    // Єдине вікно, яке ядро дає плагінові. Плагін дотягується до ядра
    // ТІЛЬКИ через методи цього об'єкта — і нікуди більше.
    ExportRegistry& registry;
public:
    explicit HostImpl(ExportRegistry& r) : registry(r) {}
    void registerExporter(Exporter* e) override { registry.add(e); }
};
