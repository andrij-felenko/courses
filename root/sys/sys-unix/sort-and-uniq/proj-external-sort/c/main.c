#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

#define MAX_LINE_LEN 4096
#define DEFAULT_MEM_LIMIT (4 * 1024 * 1024) // 4 MB буфер RAM

typedef struct {
    FILE *file;
    char path[256];
    char current_line[MAX_LINE_LEN];
    int is_active;
} RunStream;

typedef struct {
    RunStream **streams;
    size_t size;
    size_t capacity;
} MinHeap;

static int compare_strings(const void *a, const void *b) {
    const char *sa = *(const char **)a;
    const char *sb = *(const char **)b;
    return strcmp(sa, sb);
}

static void heap_swap(MinHeap *heap, size_t i, size_t j) {
    RunStream *tmp = heap->streams[i];
    heap->streams[i] = heap->streams[j];
    heap->streams[j] = tmp;
}

static void heapify_down(MinHeap *heap, size_t idx) {
    size_t smallest = idx;
    size_t left = 2 * idx + 1;
    size_t right = 2 * idx + 2;

    if (left < heap->size &&
        strcmp(heap->streams[left]->current_line,
               heap->streams[smallest]->current_line) < 0) {
        smallest = left;
    }

    if (right < heap->size &&
        strcmp(heap->streams[right]->current_line,
               heap->streams[smallest]->current_line) < 0) {
        smallest = right;
    }

    if (smallest != idx) {
        heap_swap(heap, idx, smallest);
        heapify_down(heap, smallest);
    }
}

static void heapify_up(MinHeap *heap, size_t idx) {
    while (idx > 0) {
        size_t parent = (idx - 1) / 2;
        if (strcmp(heap->streams[idx]->current_line,
                   heap->streams[parent]->current_line) < 0) {
            heap_swap(heap, idx, parent);
            idx = parent;
        } else {
            break;
        }
    }
}

static void heap_push(MinHeap *heap, RunStream *stream) {
    heap->streams[heap->size] = stream;
    heapify_up(heap, heap->size);
    heap->size++;
}

static RunStream *heap_pop(MinHeap *heap) {
    if (heap->size == 0) return NULL;
    RunStream *root = heap->streams[0];
    heap->streams[0] = heap->streams[heap->size - 1];
    heap->size--;
    if (heap->size > 0) {
        heapify_down(heap, 0);
    }
    return root;
}

static char *write_temp_run(char **lines, size_t count, size_t run_idx) {
    qsort(lines, count, sizeof(char *), compare_strings);

    char *path = malloc(256);
    snprintf(path, 256, "/tmp/extsort_run_%d_%zu.tmp", getpid(), run_idx);

    FILE *out = fopen(path, "w");
    if (!out) {
        perror("Помилка створення тимчасового файлу");
        free(path);
        return NULL;
    }

    for (size_t i = 0; i < count; ++i) {
        fputs(lines[i], out);
        free(lines[i]);
    }
    fclose(out);
    return path;
}

static size_t generate_runs(FILE *in, size_t mem_limit, char ***out_run_paths) {
    size_t run_count = 0;
    size_t run_cap = 16;
    char **run_paths = malloc(run_cap * sizeof(char *));

    size_t lines_cap = 1024;
    char **lines = malloc(lines_cap * sizeof(char *));
    size_t lines_count = 0;
    size_t current_mem = 0;

    char buffer[MAX_LINE_LEN];
    while (fgets(buffer, sizeof(buffer), in)) {
        size_t len = strlen(buffer);
        char *line = strdup(buffer);

        if (lines_count >= lines_cap) {
            lines_cap *= 2;
            lines = realloc(lines, lines_cap * sizeof(char *));
        }
        lines[lines_count++] = line;
        current_mem += len + sizeof(char *);

        if (current_mem >= mem_limit) {
            char *p = write_temp_run(lines, lines_count, run_count);
            if (run_count >= run_cap) {
                run_cap *= 2;
                run_paths = realloc(run_paths, run_cap * sizeof(char *));
            }
            run_paths[run_count++] = p;
            lines_count = 0;
            current_mem = 0;
        }
    }

    if (lines_count > 0) {
        char *p = write_temp_run(lines, lines_count, run_count);
        if (run_count >= run_cap) {
            run_cap *= 2;
            run_paths = realloc(run_paths, run_cap * sizeof(char *));
        }
        run_paths[run_count++] = p;
    }

    free(lines);
    *out_run_paths = run_paths;
    return run_count;
}

static void merge_runs(char **run_paths, size_t run_count, FILE *out) {
    if (run_count == 0) return;

    RunStream *streams = calloc(run_count, sizeof(RunStream));
    MinHeap heap = {
        .streams = malloc(run_count * sizeof(RunStream *)),
        .size = 0,
        .capacity = run_count
    };

    for (size_t i = 0; i < run_count; ++i) {
        strncpy(streams[i].path, run_paths[i], sizeof(streams[i].path) - 1);
        streams[i].file = fopen(streams[i].path, "r");
        if (streams[i].file && fgets(streams[i].current_line, MAX_LINE_LEN, streams[i].file)) {
            streams[i].is_active = 1;
            heap_push(&heap, &streams[i]);
        } else {
            streams[i].is_active = 0;
            if (streams[i].file) fclose(streams[i].file);
        }
    }

    while (heap.size > 0) {
        RunStream *min_stream = heap_pop(&heap);
        fputs(min_stream->current_line, out);

        if (fgets(min_stream->current_line, MAX_LINE_LEN, min_stream->file)) {
            heap_push(&heap, min_stream);
        } else {
            fclose(min_stream->file);
            min_stream->is_active = 0;
        }
    }

    for (size_t i = 0; i < run_count; ++i) {
        unlink(run_paths[i]);
        free(run_paths[i]);
    }

    free(streams);
    free(heap.streams);
    free(run_paths);
}

int main(int argc, char *argv[]) {
    FILE *in = (argc > 1) ? fopen(argv[1], "r") : stdin;
    if (!in) {
        perror("Помилка відкриття вхідного файлу");
        return 1;
    }

    char **run_paths = NULL;
    size_t run_count = generate_runs(in, DEFAULT_MEM_LIMIT, &run_paths);
    if (in != stdin) fclose(in);

    merge_runs(run_paths, run_count, stdout);
    return 0;
}
