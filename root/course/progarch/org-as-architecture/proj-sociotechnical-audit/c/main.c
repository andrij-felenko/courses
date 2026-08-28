/* Утиліта аналізу соціотехнічного незбігу мовою C (POSIX API, чітке управління пам'яттю) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE 1024
#define MAX_FILES 500

typedef struct {
    char filepath[256];
    char main_team[64];
    int main_team_changes;
    int total_changes;
    int distinct_teams_count;
} FileSociotechnicalStat;

static FileSociotechnicalStat g_stats[MAX_FILES];
static int g_stat_count = 0;

static FileSociotechnicalStat* find_or_create_file(const char* path) {
    for (int i = 0; i < g_stat_count; ++i) {
        if (strcmp(g_stats[i].filepath, path) == 0) {
            return &g_stats[i];
        }
    }
    if (g_stat_count < MAX_FILES) {
        FileSociotechnicalStat* st = &g_stats[g_stat_count++];
        strncpy(st->filepath, path, 255);
        st->filepath[255] = '\0';
        st->main_team[0] = '\0';
        st->main_team_changes = 0;
        st->total_changes = 0;
        st->distinct_teams_count = 1;
        return st;
    }
    return NULL;
}

int main(void) {
    FILE* fp = popen("git log --numstat --no-merges --format=COMMIT|%ae", "r");
    if (!fp) {
        perror("Не вдалося запустити git log");
        return 1;
    }

    char buffer[MAX_LINE];
    char current_team[64] = "Unknown";

    while (fgets(buffer, sizeof(buffer), fp)) {
        buffer[strcspn(buffer, "\r\n")] = 0;
        if (strlen(buffer) == 0) continue;

        if (strncmp(buffer, "COMMIT|", 7) == 0) {
            char* email = buffer + 7;
            if (strstr(email, "twin")) {
                strncpy(current_team, "TwinTeam", 63);
            } else if (strstr(email, "auto")) {
                strncpy(current_team, "AutoTeam", 63);
            } else {
                strncpy(current_team, "CoreTeam", 63);
            }
            current_team[63] = '\0';
        } else {
            int added = 0, deleted = 0;
            char path[256];
            if (sscanf(buffer, "%d\t%d\t%255s", &added, &deleted, path) == 3) {
                FileSociotechnicalStat* st = find_or_create_file(path);
                if (st) {
                    int changes = added + deleted;
                    st->total_changes += changes;
                    if (changes > st->main_team_changes) {
                        st->main_team_changes = changes;
                        strncpy(st->main_team, current_team, 63);
                        st->main_team[63] = '\0';
                    }
                }
            }
        }
    }
    pclose(fp);

    printf("=== ЗВІТ СОЦІОТЕХНІЧНОГО АУДИТУ (C-реалізація) ===\n");
    int mismatched = 0;
    for (int i = 0; i < g_stat_count; ++i) {
        double tor = (double)g_stats[i].main_team_changes / (g_stats[i].total_changes ? g_stats[i].total_changes : 1);
        if (tor < 0.60) {
            mismatched++;
            printf("Файл: %s | Головний власник: %s | TOR: %.2f%%\n",
                   g_stats[i].filepath, g_stats[i].main_team, tor * 100.0);
        }
    }
    double cmi = (double)mismatched / (g_stat_count ? g_stat_count : 1);
    printf("Аналізовано файлів: %d\n", g_stat_count);
    printf("Індекс соціотехнічного незбігу (CMI): %.2f%%\n", cmi * 100.0);

    return 0;
}
