#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int ladder_length_c(const char* begin_word, const char* end_word, const char** word_list, int word_count) {
    int len = strlen(begin_word);
    int target_idx = -1;
    for (int i = 0; i < word_count; ++i) {
        if (strcmp(word_list[i], end_word) == 0) {
            target_idx = i;
            break;
        }
    }
    if (target_idx == -1) return 0;

    int* dist = (int*)malloc(sizeof(int) * word_count);
    for (int i = 0; i < word_count; ++i) dist[i] = -1;

    int* queue = (int*)malloc(sizeof(int) * word_count);
    int head = 0, tail = 0;

    for (int i = 0; i < word_count; ++i) {
        int diff = 0;
        for (int k = 0; k < len; ++k) {
            if (begin_word[k] != word_list[i][k]) diff++;
        }
        if (diff == 1) {
            dist[i] = 2; // Кількість слів у ланцюжку (begin + word_list[i])
            queue[tail++] = i;
        }
    }

    int result = 0;
    while (head < tail) {
        int u = queue[head++];
        if (u == target_idx) {
            result = dist[u];
            break;
        }

        for (int v = 0; v < word_count; ++v) {
            if (dist[v] == -1) {
                int diff = 0;
                for (int k = 0; k < len; ++k) {
                    if (word_list[u][k] != word_list[v][k]) diff++;
                }
                if (diff == 1) {
                    dist[v] = dist[u] + 1;
                    queue[tail++] = v;
                }
            }
        }
    }

    free(dist); free(queue);
    return result;
}
