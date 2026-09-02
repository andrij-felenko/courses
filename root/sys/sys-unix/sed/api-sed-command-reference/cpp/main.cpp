// main.cpp — mini-sed: навчальний потоковий редактор з однією командою s///.
//
// Збірка:  c++ -std=c++23 -O2 -Wall -Wextra -o mini-sed *.cpp
//          (з мітками SELinux: c++ -DSED_WITH_SELINUX … -lselinux)
//
// Виклик:  mini-sed [-n] [-u] [-z] [-E] [-i[СУФ]] [--follow-symlinks] [-q N]
//                   's/RE/REP/ПРАПОРЦІ' [файл…]
//
// Коди виходу — ті самі, що в sed: 0 · 1 синтаксис · 2 введення/виведення ·
// 141 обірваний канал.
#include <charconv>
#include <expected>
#include <fstream>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>

#include "inplace_editor.hpp"
#include "pipeline.hpp"
#include "sed_state.hpp"
#include "substitution.hpp"

namespace {

struct Config {
    minised::StreamOptions stream;
    bool extended{false};
    bool inplace{false};
    bool follow_symlinks{false};
    std::optional<std::string> backup;
    std::string script;
    std::vector<std::string> files;
};

void usage() {
    std::cerr << "виклик: mini-sed [-n] [-u] [-z] [-E] [-i[СУФ]]"
                 " [--follow-symlinks] [-q N] 's/RE/REP/ПРАПОРЦІ' [файл…]\n";
}

std::expected<Config, std::string> parse_args(int argc, char** argv) {
    Config cfg;
    int i = 1;
    for (; i < argc; ++i) {
        const std::string_view a = argv[i];
        if (a.size() < 2 || a.front() != '-') break;
        if (a == "--") { ++i; break; }
        if (a == "--follow-symlinks") { cfg.follow_symlinks = true; continue; }
        if (a.starts_with("-i")) {                       // суфікс пишеться злито: -i.bak
            cfg.inplace = true;
            if (a.size() > 2) cfg.backup = std::string{a.substr(2)};
            continue;
        }
        if (a == "-q") {
            if (++i >= argc) return std::unexpected("опція -q вимагає числа");
            const std::string_view n = argv[i];
            std::size_t value = 0;
            if (std::from_chars(n.data(), n.data() + n.size(), value).ec != std::errc{})
                return std::unexpected("опція -q вимагає числа");
            cfg.stream.quit_after = value;
            continue;
        }
        if (a[1] == '-') return std::unexpected(std::string{"невідома опція "} + std::string{a});
        for (const char f : a.substr(1)) {
            switch (f) {
                case 'n': cfg.stream.quiet = true; break;
                case 'u': cfg.stream.unbuffered = true; break;
                case 'z': cfg.stream.record_sep = '\0'; break;
                case 'E': case 'r': cfg.extended = true; break;
                default: return std::unexpected(std::string{"невідома опція -"} + f);
            }
        }
    }
    if (i >= argc) return std::unexpected("не задано сценарію");
    cfg.script = argv[i++];
    for (; i < argc; ++i) cfg.files.emplace_back(argv[i]);
    return cfg;
}

// pubsetbuf має право щось означати лише ДО open() — саме тому потік
// створюється порожнім, а файл відкривається окремим викликом.
std::ifstream open_input(const std::string& name, bool unbuffered) {
    std::ifstream in;
    if (unbuffered) in.rdbuf()->pubsetbuf(nullptr, 0);
    in.open(name, std::ios::binary);
    return in;
}

// Режим -i збирає результат у пам'яті: писати у вхідний файл під час читання
// не можна, а тимчасова копія все одно потрібна для rename().
std::string transform(std::istream& in, minised::SedState& st,
                      const minised::Substitution& subst,
                      const minised::StreamOptions& opts) {
    std::ostringstream out;
    st.reset_counters();
    while (st.read_record(in, opts.record_sep)) {
        const bool changed = subst.apply(st.pattern());
        if (!opts.quiet) st.print(out, opts.record_sep);
        if (changed && subst.print_flag()) st.print(out, opts.record_sep);
        if (opts.quit_after && st.line_number() >= opts.quit_after) break;
    }
    return std::move(out).str();
}

int run_inplace(const Config& cfg, const minised::Substitution& subst,
                minised::SedState& st) {
    if (cfg.files.empty()) {
        std::cerr << "mini-sed: -i вимагає імені файла\n";
        return 1;
    }
    int status = 0;
    const minised::InPlaceEditor::Options opts{cfg.backup, cfg.follow_symlinks};
    for (const std::string& name : cfg.files) {
        std::ifstream in = open_input(name, cfg.stream.unbuffered);
        if (!in) {
            std::cerr << "mini-sed: не відкривається " << name << '\n';
            status = 2;
            continue;
        }
        const std::string content = transform(in, st, subst, cfg.stream);
        if (in.bad()) {
            std::cerr << "mini-sed: помилка читання " << name << '\n';
            status = 2;
            continue;
        }
        if (auto ok = minised::InPlaceEditor::commit(name, content, opts); !ok) {
            std::cerr << "mini-sed: " << name << ": " << ok.error().message() << '\n';
            status = 2;
        }
    }
    return status;
}

int run_stream(const Config& cfg, const minised::Substitution& subst,
               minised::SedState& st) {
    minised::Pipeline pipeline{subst, cfg.stream};
    if (cfg.files.empty()) return pipeline.run(std::cin, std::cout, st);

    int status = 0;
    for (const std::string& name : cfg.files) {
        if (name == "-") {
            if (int rc = pipeline.run(std::cin, std::cout, st); rc) return rc;
        } else {
            std::ifstream in = open_input(name, cfg.stream.unbuffered);
            if (!in) {
                std::cerr << "mini-sed: не відкривається " << name << '\n';
                status = 2;
                continue;
            }
            if (int rc = pipeline.run(in, std::cout, st); rc) return rc;
        }
        if (pipeline.quit_requested()) break;   // команда q: решту файлів не чіпаємо
    }
    return status;
}

}  // namespace

int main(int argc, char** argv) {
    // Синхронізацію з stdio знімаємо: інакше кожен << тягне за собою C-потік.
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    auto cfg = parse_args(argc, argv);
    if (!cfg) {
        std::cerr << "mini-sed: " << cfg.error() << '\n';
        usage();
        return 1;
    }

    auto subst = minised::Substitution::compile(cfg->script, cfg->extended);
    if (!subst) {
        std::cerr << "mini-sed: " << subst.error() << '\n';
        return 1;                                  // синтаксична помилка сценарію
    }

    minised::SedState st;
    return cfg->inplace ? run_inplace(*cfg, *subst, st)
                        : run_stream(*cfg, *subst, st);
}
