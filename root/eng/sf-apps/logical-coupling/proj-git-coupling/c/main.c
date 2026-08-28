#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE 1024
#define MAX_FILES_PER_COMMIT 64
#define MAX_PAIRS 65536
#define MAX_UNIQUE_FILES 8192

typedef struct {
    char name[256];
    int commit_count;
} FileEntry;

typedef struct {
    int file_a;
    int file_b;
    int co_change_count;
} PairEntry;

static FileEntry g_files[MAX_UNIQUE_FILES];
static int g_file_count = 0;

static PairEntry g_pairs[MAX_PAIRS];
static int g_pair_count = 0;

static int get_or_add_file(const char* name) {
    for (int i = 0; i < g_file_count; i++) {
        if (strcmp(g_files[i].name, name) == 0) return i;
    }
    if (g_file_count >= MAX_UNIQUE_FILES) return -1;
    strncpy(g_files[g_file_count].name, name, sizeof(g_files[0].name) - 1);
    g_files[g_file_count].name[sizeof(g_files[0].name) - 1] = '\0';
    g_files[g_file_count].commit_count = 0;
    return g_file_count++;
}

static void add_co_change(int id_a, int id_b) {
    if (id_a > id_b) { int t = id_a; id_a = id_b; id_b = t; }
    for (int i = 0; i < g_pair_count; i++) {
        if (g_pairs[i].file_a == id_a && g_pairs[i].file_b == id_b) {
            g_pairs[i].co_change_count++;
            return;
        }
    }
    if (g_pair_count < MAX_PAIRS) {
        g_pairs[g_pair_count].file_a = id_a;
        g_pairs[g_pair_count].file_b = id_b;
        g_pairs[g_pair_count].co_change_count = 1;
        g_pair_count++;
    }
}

static void process_commit_files(int* ids, int count) {
    if (count < 2 || count > MAX_FILES_PER_COMMIT) return;
    for (int i = 0; i < count; i++) {
        g_files[ids[i]].commit_count++;
    }
    for (int i = 0; i < count; i++) {
        for (int j = i + 1; j < count; j++) {
            if (ids[i] != ids[j]) {
                add_co_change(ids[i], ids[j]);
            }
        }
    }
}

static int compare_pairs(const void* a, const void* b) {
    const PairEntry* pa = (const PairEntry*)a;
    const PairEntry* pb = (const PairEntry*)b;
    return pb->co_change_count - pa->co_change_count;
}

int main(void) {
    char line[MAX_LINE];
    int current_commit_files[MAX_FILES_PER_COMMIT];
    int commit_file_count = 0;
    int total_commits = 0;

    while (fgets(line, sizeof(line), stdin)) {
        size_t len = strlen(line);
        while (len > 0 && (line[len - 1] == '\n' || line[len - 1] == '\r')) line[--len] = '\0';
        if (len == 0) continue;

        if (strncmp(line, "COMMIT:", 7) == 0) {
            if (commit_file_count > 0) {
                process_commit_files(current_commit_files, commit_file_count);
                commit_file_count = 0;
                total_commits++;
            }
        } else {
            if (commit_file_count < MAX_FILES_PER_COMMIT) {
                int fid = get_or_add_file(line);
                if (fid >= 0) {
                    current_commit_files[commit_file_count++] = fid;
                }
            }
        }
    }
    if (commit_file_count > 0) {
        process_commit_files(current_commit_files, commit_file_count);
        total_commits++;
    }

    qsort(g_pairs, g_pair_count, sizeof(PairEntry), compare_pairs);

    printf("=== ТОП ПАР ІЗ ЛОГІЧНИМ ЗАЧЕПЛЕННЯМ (Всього транзакцій: %d) ===\n", total_commits);
    printf("%-35s %-35s %6s %8s %8s %8s\n", "Файл A", "Файл B", "Спільні", "Conf A->B", "Conf B->A", "Jaccard");
    
    for (int i = 0; i < g_pair_count && i < 20; i++) {
        if (g_pairs[i].co_change_count < 2) continue;
        int fa = g_pairs[i].file_a;
        int fb = g_pairs[i].file_b;
        int n_ab = g_pairs[i].co_change_count;
        int n_a = g_files[fa].commit_count;
        int n_b = g_files[fb].commit_count;
        
        double conf_ab = (double)n_ab / n_a * 100.0;
        double conf_ba = (double)n_ab / n_b * 100.0;
        double jaccard = (double)n_ab / (n_a + n_b - n_ab) * 100.0;

        printf("%-35.35s %-35.35s %6d %7.1f%% %7.1f%% %7.1f%%\n",
               g_files[fa].name, g_files[fb].name, n_ab, conf_ab, conf_ba, jaccard);
    }
    return 0;
}
