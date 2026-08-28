#define _GNU_SOURCE
#include <iostream>
#include <string_view>
#include <dlfcn.h>
#include <unistd.h>
#include <cstring>

extern "C" {

using ExecveSignature = int (*)(const char*, char* const[], char* const[]);

/* C++ обгортка перехоплювача execve */
int execve(const char* filename, char* const argv[], char* const envp[]) {
    auto original_execve = reinterpret_cast<ExecveSignature>(dlsym(RTLD_NEXT, "execve"));
    if (!original_execve) {
        std::cerr << "[libargv_trace] dlsym failure: " << dlerror() << '\n';
        _exit(1);
    }

    std::cerr << "\n[EXECVE INTERCEPT] Запуск програми: " << filename << '\n';
    if (argv) {
        for (int i = 0; argv[i] != nullptr; ++i) {
            std::string_view arg(argv[i]);
            std::cerr << "  -> argv[" << i << "] = \"" << arg << "\" (байтів: " << arg.size() << ")\n";
        }
    }
    std::cerr << "[EXECVE INTERCEPT] ----------------------------------------\n\n";

    return original_execve(filename, argv, envp);
}

} // extern "C"
