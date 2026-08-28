/* path_resolver.c — Реалізація мовою C (POSIX 2008) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <errno.h>

#define HASH_SIZE 101

typedef struct HashNode {
    char *name;
    char *path;
    struct HashNode *next;
} HashNode;

typedef struct {
    HashNode *buckets[HASH_SIZE];
} CommandCache;

static unsigned int hash_string(const char *str) {
    unsigned int hash = 5381;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash % HASH_SIZE;
}

void cache_init(CommandCache *cache) {
    memset(cache->buckets, 0, sizeof(cache->buckets));
}

const char *cache_lookup(CommandCache *cache, const char *name) {
    unsigned int index = hash_string(name);
    HashNode *node = cache->buckets[index];
    while (node) {
        if (strcmp(node->name, name) == 0) {
            return node->path;
        }
        node = node->next;
    }
    return NULL;
}

void cache_insert(CommandCache *cache, const char *name, const char *path) {
    unsigned int index = hash_string(name);
    HashNode *node = (HashNode *)malloc(sizeof(HashNode));
    node->name = strdup(name);
    node->path = strdup(path);
    node->next = cache->buckets[index];
    cache->buckets[index] = node;
}

void cache_free(CommandCache *cache) {
    for (int i = 0; i < HASH_SIZE; ++i) {
        HashNode *node = cache->buckets[i];
        while (node) {
            HashNode *temp = node;
            node = node->next;
            free(temp->name);
            free(temp->path);
            free(temp);
        }
    }
}

char *resolve_in_path(CommandCache *cache, const char *cmd) {
    if (strchr(cmd, '/') != NULL) {
        return strdup(cmd);
    }

    const char *cached = cache_lookup(cache, cmd);
    if (cached != NULL) {
        printf("[DEBUG Cache HIT] '%s' -> '%s'\n", cmd, cached);
        return strdup(cached);
    }

    const char *path_env = getenv("PATH");
    if (!path_env) {
        path_env = "/usr/bin:/bin";
    }

    char *path_copy = strdup(path_env);
    char *saveptr = NULL;
    char *dir = strtok_r(path_copy, ":", &saveptr);
    char full_path[1024];

    while (dir != NULL) {
        const char *dir_to_use = (strlen(dir) == 0) ? "." : dir;
        snprintf(full_path, sizeof(full_path), "%s/%s", dir_to_use, cmd);

        if (faccessat(AT_FDCWD, full_path, X_OK, AT_EACCESS) == 0) {
            printf("[DEBUG PATH Miss -> Found] '%s' -> '%s'\n", cmd, full_path);
            cache_insert(cache, cmd, full_path);
            free(path_copy);
            return strdup(full_path);
        }
        dir = strtok_r(NULL, ":", &saveptr);
    }

    free(path_copy);
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <команда> [аргументи...]\n", argv[0]);
        return 1;
    }

    CommandCache cache;
    cache_init(&cache);

    const char *cmd_name = argv[1];
    char *resolved_path = resolve_in_path(&cache, cmd_name);

    if (!resolved_path) {
        fprintf(stderr, "Помилка: команду '%s' не знайдено в PATH\n", cmd_name);
        cache_free(&cache);
        return 127;
    }

    pid_t pid = fork();
    if (pid == 0) {
        execvp(resolved_path, &argv[1]);
        perror("execvp");
        exit(127);
    } else if (pid > 0) {
        int status;
        waitpid(pid, &status, 0);
        printf("[Process exited with status %d]\n", WEXITSTATUS(status));
    }

    free(resolved_path);
    cache_free(&cache);
    return 0;
}
