#include <stdio.h>
#include "fuzzy_matcher.h"

static bool print_result(const fuzzy_match_t* match, void* ctx) {
    printf("  -> Знайдено: %-15s (відстань: %d)
", match->word, match->distance);
    return true;
}

int main(void) {
    fuzzy_trie_t* trie = fuzzy_trie_create();
    
    fuzzy_trie_insert(trie, "kitten", NULL);
    fuzzy_trie_insert(trie, "sitting", NULL);
    fuzzy_trie_insert(trie, "kitchen", NULL);
    fuzzy_trie_insert(trie, "cat", NULL);
    fuzzy_trie_insert(trie, "caterpillar", NULL);

    fuzzy_options_t opts = {
        .max_distance = 2,
        .prefix_freeze_len = 0,
        .allow_transposition = true,
        .max_results = 10
    };

    printf("Пошук для запиту 'kiten':
");
    fuzzy_trie_search(trie, "kiten", &opts, print_result, NULL);

    fuzzy_trie_destroy(trie);
    return 0;
}
