/* tools/dsl_compiler.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_DEPS 64
#define MAX_PATH_LEN 512
#define MAX_LINE_LEN 1024

typedef struct {
    char input_path[MAX_PATH_LEN];
    char out_dir[MAX_PATH_LEN];
    char depfile_path[MAX_PATH_LEN];
    char dependencies[MAX_DEPS][MAX_PATH_LEN];
    int dep_count;
} CompilerState;

static void add_dependency(CompilerState* state, const char* path) {
    if (state->dep_count >= MAX_DEPS) return;
    for (int i = 0; i < state->dep_count; ++i) {
        if (strcmp(state->dependencies[i], path) == 0) return;
    }
    strncpy(state->dependencies[state->dep_count++], path, MAX_PATH_LEN - 1);
}

static int parse_dependencies(CompilerState* state, const char* file_path) {
    FILE* f = fopen(file_path, "r");
    if (!f) {
        fprintf(stderr, "[dsl_compiler] Не вдалося відкрити: %s\n", file_path);
        return 0;
    }
    add_dependency(state, file_path);

    char line[MAX_LINE_LEN];
    while (fgets(line, sizeof(line), f)) {
        char* inc = strstr(line, "include \"");
        if (inc) {
            char inc_file[MAX_PATH_LEN];
            if (sscanf(inc + 9, "%[^\"]", inc_file) == 1) {
                char resolved_path[MAX_PATH_LEN];
                snprintf(resolved_path, sizeof(resolved_path), "dsl/%s", inc_file);
                parse_dependencies(state, resolved_path);
            }
        }
    }
    fclose(f);
    return 1;
}

static int emit_files(const CompilerState* state) {
    char hpp_path[MAX_PATH_LEN];
    char cpp_path[MAX_PATH_LEN];
    snprintf(hpp_path, sizeof(hpp_path), "%s/messages.hpp", state->out_dir);
    snprintf(cpp_path, sizeof(cpp_path), "%s/messages.cpp", state->out_dir);

    FILE* hpp = fopen(hpp_path, "w");
    if (!hpp) return 0;
    fprintf(hpp, "#pragma once\n#include <stdint.h>\n\n"
                 "typedef struct {\n"
                 "    uint32_t timestamp;\n"
                 "    float voltage;\n"
                 "    float current;\n"
                 "} TelemetryFrame;\n\n"
                 "void print_frame(const TelemetryFrame* frame);\n");
    fclose(hpp);

    FILE* cpp = fopen(cpp_path, "w");
    if (!cpp) return 0;
    fprintf(cpp, "#include \"messages.hpp\"\n#include <stdio.h>\n\n"
                 "void print_frame(const TelemetryFrame* frame) {\n"
                 "    printf(\"[Telemetry] T: %%u V: %%.2f I: %%.2f\\n\",\n"
                 "           frame->timestamp, frame->voltage, frame->current);\n"
                 "}\n");
    fclose(cpp);
    return 1;
}

static int emit_depfile(const CompilerState* state) {
    if (strlen(state->depfile_path) == 0) return 1;
    FILE* dep = fopen(state->depfile_path, "w");
    if (!dep) return 0;

    fprintf(dep, "%s/messages.cpp:", state->out_dir);
    for (int i = 0; i < state->dep_count; ++i) {
        fprintf(dep, " %s", state->dependencies[i]);
    }
    fprintf(dep, "\n");
    fclose(dep);
    return 1;
}

int main(int argc, char* argv[]) {
    CompilerState state;
    memset(&state, 0, sizeof(state));

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--input") == 0 && i + 1 < argc) {
            strncpy(state.input_path, argv[++i], MAX_PATH_LEN - 1);
        } else if (strcmp(argv[i], "--out-dir") == 0 && i + 1 < argc) {
            strncpy(state.out_dir, argv[++i], MAX_PATH_LEN - 1);
        } else if (strcmp(argv[i], "--depfile") == 0 && i + 1 < argc) {
            strncpy(state.depfile_path, argv[++i], MAX_PATH_LEN - 1);
        }
    }

    if (strlen(state.input_path) == 0 || strlen(state.out_dir) == 0) {
        fprintf(stderr, "Використання: dsl_compiler --input <f> --out-dir <d> [--depfile <f>]\n");
        return 1;
    }

    if (!parse_dependencies(&state, state.input_path)) return 2;
    if (!emit_files(&state)) return 3;
    if (!emit_depfile(&state)) return 4;

    return 0;
}
