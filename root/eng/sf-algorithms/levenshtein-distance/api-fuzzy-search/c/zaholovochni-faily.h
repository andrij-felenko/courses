#ifndef FUZZY_MATCHER_H
#define FUZZY_MATCHER_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    FUZZY_OK = 0,
    FUZZY_ERR_INVALID_ARG = -1,
    FUZZY_ERR_NO_MEMORY = -2,
    FUZZY_ERR_NOT_FOUND = -3
} fuzzy_status_t;

typedef struct fuzzy_trie fuzzy_trie_t;

typedef struct {
    int max_distance;           /* Поріг відстані Левенштейна (зазвичай 1 або 2) */
    size_t prefix_freeze_len;   /* Довжина точного префікса без помилок */
    bool allow_transposition;   /* Перемикач алгоритму Дамерау—Левенштейна */
    size_t max_results;         /* Ліміт кількості повернених результатів */
} fuzzy_options_t;

typedef struct {
    const char* word;
    int distance;
    void* user_data;
} fuzzy_match_t;

typedef bool (*fuzzy_match_callback_fn)(const fuzzy_match_t* match, void* context);

/* Створення та видалення структури дерева Trie */
fuzzy_trie_t* fuzzy_trie_create(void);
void fuzzy_trie_destroy(fuzzy_trie_t* trie);

/* Додавання слів до словника */
fuzzy_status_t fuzzy_trie_insert(fuzzy_trie_t* trie, const char* word, void* user_data);

/* Виконання нечіткого пошуку */
fuzzy_status_t fuzzy_trie_search(
    const fuzzy_trie_t* trie,
    const char* query,
    const fuzzy_options_t* options,
    fuzzy_match_callback_fn callback,
    void* context
);

#ifdef __cplusplus
}
#endif

#endif /* FUZZY_MATCHER_H */
