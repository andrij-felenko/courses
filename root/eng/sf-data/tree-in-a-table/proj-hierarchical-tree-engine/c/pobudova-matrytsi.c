#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int ancestor_id;
    int descendant_id;
    int depth;
} ClosureEntry;

/* Генерація всіх шляхів транзитивного замикання */
size_t tree_generate_closure(const TreeNode* node, ClosureEntry* out_entries, size_t max_entries) {
    if (!node || !out_entries) return 0;

    size_t count = 0;
    /* Рефлексивний запис зв'язку вузла із самим собою */
    if (count < max_entries) {
        out_entries[count++] = (ClosureEntry){node->id, node->id, 0};
    }

    /* Прохід по всіх предках вгору до кореневого вузла */
    const TreeNode* curr = node->parent;
    int cur_depth = 1;
    while (curr && count < max_entries) {
        out_entries[count++] = (ClosureEntry){curr->id, node->id, cur_depth};
        curr = curr->parent;
        cur_depth++;
    }

    /* Рекурсивне повторення для всіх дочірніх піддерев */
    for (size_t i = 0; i < node->child_count; ++i) {
        count += tree_generate_closure(node->children[i], out_entries + count, max_entries - count);
    }

    return count;
}
