#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MERKLE_DEPTH 3
#define NUM_LEAVES (1 << MERKLE_DEPTH)
#define TREE_SIZE (1 << (MERKLE_DEPTH + 1))

/* Хеш-функція FNV-1a (64-bit) для швидкого хешування */
#define FNV_OFFSET 14695981039346656037ULL
#define FNV_PRIME  1099511628211ULL

static uint64_t fnv1a_hash(const void *data, size_t len) {
    const uint8_t *ptr = (const uint8_t *)data;
    uint64_t hash = FNV_OFFSET;
    for (size_t i = 0; i < len; ++i) {
        hash ^= ptr[i];
        hash *= FNV_PRIME;
    }
    return hash;
}

static uint64_t fnv1a_combine(uint64_t left, uint64_t right) {
    uint64_t hash = FNV_OFFSET;
    hash ^= left;  hash *= FNV_PRIME;
    hash ^= right; hash *= FNV_PRIME;
    return hash;
}

/* Структура запису таблиці */
typedef struct {
    uint64_t key_token;
    char key[32];
    char value[64];
    uint64_t timestamp;
    bool is_tombstone;
} DatabaseRecord;

/* Структура бінарного дерева Меркла */
typedef struct {
    uint64_t nodes[TREE_SIZE];
    uint64_t leaf_counts[NUM_LEAVES];
} MerkleTree;

/* Ініціалізація дерева */
void merkle_init(MerkleTree *tree) {
    memset(tree->nodes, 0, sizeof(tree->nodes));
    memset(tree->leaf_counts, 0, sizeof(tree->leaf_counts));
}

/* Додавання запису до листка дерева */
void merkle_add_record(MerkleTree *tree, const DatabaseRecord *rec) {
    /* Обчислюємо індекс листка за старшими бітами токена */
    uint32_t leaf_idx = (uint32_t)(rec->key_token >> (64 - MERKLE_DEPTH));
    uint32_t node_idx = NUM_LEAVES + leaf_idx;

    /* Хешуємо вміст запису */
    uint64_t rec_hash = fnv1a_hash(rec->key, strlen(rec->key));
    rec_hash = fnv1a_combine(rec_hash, fnv1a_hash(rec->value, strlen(rec->value)));
    rec_hash = fnv1a_combine(rec_hash, rec->timestamp);
    rec_hash = fnv1a_combine(rec_hash, (uint64_t)rec->is_tombstone);

    /* Акумулюємо хеш у листку */
    if (tree->leaf_counts[leaf_idx] == 0) {
        tree->nodes[node_idx] = rec_hash;
    } else {
        tree->nodes[node_idx] = fnv1a_combine(tree->nodes[node_idx], rec_hash);
    }
    tree->leaf_counts[leaf_idx]++;
}

/* Згортання дерева знизу вгору (Bottom-Up Rollup) */
void merkle_build(MerkleTree *tree) {
    for (int i = NUM_LEAVES - 1; i >= 1; --i) {
        uint64_t left = tree->nodes[2 * i];
        uint64_t right = tree->nodes[2 * i + 1];
        if (left == 0 && right == 0) {
            tree->nodes[i] = 0;
        } else {
            tree->nodes[i] = fnv1a_combine(left, right);
        }
    }
}

/* Рекурсивний пошук розбіжних листків */
void merkle_find_diffs(const MerkleTree *a, const MerkleTree *b, 
                       uint32_t node_idx, uint32_t depth,
                       uint32_t *diff_leaves, uint32_t *diff_count) {
    if (a->nodes[node_idx] == b->nodes[node_idx]) {
        return; /* Піддерева повністю ідентичні, пропускаємо */
    }

    if (depth == MERKLE_DEPTH) {
        /* Досягнуто листка з розбіжністю */
        diff_leaves[(*diff_count)++] = node_idx - NUM_LEAVES;
        return;
    }

    /* Спускаємося до лівого та правого нащадків */
    merkle_find_diffs(a, b, 2 * node_idx, depth + 1, diff_leaves, diff_count);
    merkle_find_diffs(a, b, 2 * node_idx + 1, depth + 1, diff_leaves, diff_count);
}

int main(void) {
    MerkleTree node_a, node_b;
    merkle_init(&node_a);
    merkle_init(&node_b);

    /* Спільний набір даних */
    DatabaseRecord r1 = { 0x1000000000000000ULL, "user:101", "Alice", 1000, false };
    DatabaseRecord r2 = { 0x4000000000000000ULL, "user:102", "Bob",   1000, false };
    DatabaseRecord r3 = { 0x8000000000000000ULL, "user:103", "Carol", 1000, false };

    merkle_add_record(&node_a, &r1);
    merkle_add_record(&node_a, &r2);
    merkle_add_record(&node_a, &r3);

    merkle_add_record(&node_b, &r1);
    merkle_add_record(&node_b, &r2);
    merkle_add_record(&node_b, &r3);

    /* Вузол A отримав оновлення, яке вузол B пропустив через мережевий збій */
    DatabaseRecord r4 = { 0xC000000000000000ULL, "user:104", "Dave_Updated", 2000, false };
    merkle_add_record(&node_a, &r4);

    merkle_build(&node_a);
    merkle_build(&node_b);

    printf("Корінь Репліки A: 0x%016llX\n", (unsigned long long)node_a.nodes[1]);
    printf("Корінь Репліки B: 0x%016llX\n", (unsigned long long)node_b.nodes[1]);

    uint32_t diff_leaves[NUM_LEAVES];
    uint32_t diff_count = 0;
    merkle_find_diffs(&node_a, &node_b, 1, 0, diff_leaves, &diff_count);

    printf("Знайдено розбіжних листків: %u\n", diff_count);
    for (uint32_t i = 0; i < diff_count; ++i) {
        uint64_t range_start = (uint64_t)diff_leaves[i] << (64 - MERKLE_DEPTH);
        uint64_t range_end = range_start + (1ULL << (64 - MERKLE_DEPTH)) - 1;
        printf("  -> Листок %u: діапазон токенів [0x%016llX, 0x%016llX]\n",
               diff_leaves[i], (unsigned long long)range_start, (unsigned long long)range_end);
    }

    return 0;
}
