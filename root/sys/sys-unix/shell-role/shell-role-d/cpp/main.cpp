// Мінімальний запускач конвеєрів: те, що оболонка робить після розбору рядка.
//
//   ./pipeline "ls -l" "grep txt" -o out.txt
//   ./pipeline --spawn "ps aux" "sort -rn"
//   ./pipeline -b "sleep 5"
//
// Розбору лапок тут немає навмисно: ланки конвеєра беруться готовими
// аргументами, бо предмет — не лексер, а комутація процесів.
#include "jobs.hpp"
#include "pipeline.hpp"
#include "terminal.hpp"

#include <unistd.h>

#include <cstdio>
#include <exception>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>

namespace {

std::vector<std::string> split_words(std::string_view text)
{
    std::vector<std::string> words;
    std::istringstream in{std::string{text}};
    std::string word;

    while (in >> word) {
        words.push_back(word);
    }
    return words;
}

void usage(const char* prog)
{
    std::fprintf(stderr,
                 "вжиток: %s [-o файл | -a файл] [--spawn] [-b] \"ланка\" [\"ланка\" ...]\n"
                 "  -o файл   stdout останньої ланки у файл (перезапис)\n"
                 "  -a файл   те саме, але дописуванням\n"
                 "  --spawn   запускати ланки через posix_spawn замість fork+exec\n"
                 "  -b        запустити конвеєр у фоні\n",
                 prog);
}

}  // namespace

int main(int argc, char** argv)
{
    PipelineSpec spec;
    bool background = false;
    int i = 1;

    for (; i < argc; ++i) {
        const std::string_view arg{argv[i]};
        if (arg == "-o" || arg == "-a") {
            if (i + 1 >= argc) {
                usage(argv[0]);
                return 2;
            }
            spec.append = (arg == "-a");
            spec.outfile = argv[++i];
        } else if (arg == "--spawn") {
            spec.use_spawn = true;
        } else if (arg == "-b") {
            background = true;
        } else {
            break;
        }
    }

    if (i >= argc) {
        usage(argv[0]);
        return 2;
    }

    for (int k = i; k < argc; ++k) {
        Stage stage{split_words(argv[k])};
        if (stage.argv.empty()) {
            std::fprintf(stderr, "порожня ланка конвеєра #%d\n", k - i + 1);
            return 2;
        }
        if (k > i) {
            spec.text += " | ";
        }
        spec.text += argv[k];
        spec.stages.push_back(std::move(stage));
    }
    spec.foreground = !background;

    try {
        TerminalControl term{STDIN_FILENO};
        JobTable jobs{term};
        PipelineRunner runner{jobs, term};

        const int code = runner.run(spec);
        if (background) {
            jobs.wait_all();       // без цього фонове завдання лишилося б сиротою
        }
        jobs.report();
        return code;
    } catch (const std::exception& e) {
        std::fprintf(stderr, "конвеєр: %s\n", e.what());
        return 1;
    }
}
