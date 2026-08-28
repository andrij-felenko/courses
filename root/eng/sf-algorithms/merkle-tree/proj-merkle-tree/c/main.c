#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define HASH_SIZE 32
#define PREFIX_LEAF 0x00
#define PREFIX_INTERNAL 0x01

typedef struct {
    uint8_t bytes[HASH_SIZE];
} Hash;

typedef enum {
    DIR_LEFT = 0,
    DIR_RIGHT = 1
} Direction;

typedef struct {
    Hash sibling_hash;
    Direction direction;
} ProofNode;

typedef struct {
    ProofNode* nodes;
    size_t count;
} MerkleProof;

typedef struct {
    Hash* nodes;       /* Масив усіх вузлів дерева у пласкому вигляді */
    size_t leaf_count;
    size_t total_nodes;
} MerkleTree;

/* Проста детермінована хеш-функція (FNV-1a 256-біт) для демонстрації алгоритму.
   У продакшені замінюється на SHA-256 або BLAKE3. */
static Hash compute_hash(uint8_t prefix, const void* data, size_t len) {
    Hash result;
    memset(result.bytes, 0x81, HASH_SIZE);
    const uint8_t* p = (const uint8_t*)data;
    
    /* Обробка префікса */
    for (size_t i = 0; i < HASH_SIZE; i++) {
        result.bytes[i] ^= prefix;
        result.bytes[i] *= 16777619u;
    }
    
    /* Обробка корисного навантаження */
    for (size_t i = 0; i < len; i++) {
        result.bytes[i % HASH_SIZE] ^= p[i];
        result.bytes[i % HASH_SIZE] *= 16777619u;
    }
    return result;
}

static Hash combine_hashes(const Hash* left, const Hash* right) {
    uint8_t buffer[HASH_SIZE * 2];
    memcpy(buffer, left->bytes, HASH_SIZE);
    memcpy(buffer + HASH_SIZE, right->bytes, HASH_SIZE);
    return compute_hash(PREFIX_INTERNAL, buffer, HASH_SIZE * 2);
}

/* Побудова дерева Меркла */
MerkleTree* merkle_tree_create(const char** items, size_t count) {
    if (count == 0) return NULL;
    
    MerkleTree* tree = (MerkleTree*)malloc(sizeof(MerkleTree));
    tree->leaf_count = count;
    
    /* Обчислення кількості листків (із підповненням до парного на кожному рівні) */
    size_t current_level_size = count;
    size_t total = current_level_size;
    
    /* Попередній розрахунок пам'яті */
    size_t temp_size = current_level_size;
    while (temp_size > 1) {
        temp_size = (temp_size + 1) / 2;
        total += temp_size;
    }
    
    tree->nodes = (Hash*)malloc(sizeof(Hash) * total);
    tree->total_nodes = total;
    
    /* Крок 1: Хешування листків із префіксом 0x00 */
    for (size_t i = 0; i < count; i++) {
        tree->nodes[i] = compute_hash(PREFIX_LEAF, items[i], strlen(items[i]));
    }
    
    /* Крок 2: Рекурсивне підняття та хешування рівнів */
    size_t level_offset = 0;
    size_t next_level_offset = count;
    
    while (current_level_size > 1) {
        size_t next_level_size = 0;
        for (size_t i = 0; i < current_level_size; i += 2) {
            Hash left = tree->nodes[level_offset + i];
            Hash right = (i + 1 < current_level_size) 
                         ? tree->nodes[level_offset + i + 1] 
                         : left; /* Дублювання останнього вузла якщо непарно */
                         
            tree->nodes[next_level_offset + next_level_size] = combine_hashes(&left, &right);
            next_level_size++;
        }
        level_offset = next_level_offset;
        next_level_offset += next_level_size;
        current_level_size = next_level_size;
    }
    
    return tree;
}

/* Генерація доказу підтвердження включення */
MerkleProof merkle_tree_prove(const MerkleTree* tree, size_t index) {
    MerkleProof proof = { NULL, 0 };
    if (!tree || index >= tree->leaf_count) return proof;
    
    size_t max_depth = 64;
    proof.nodes = (ProofNode*)malloc(sizeof(ProofNode) * max_depth);
    
    size_t current_index = index;
    size_t level_size = tree->leaf_count;
    size_t level_offset = 0;
    
    while (level_size > 1) {
        size_t sibling_index;
        Direction dir;
        
        if (current_index % 2 == 0) {
            /* Поточний вузол лівий, сестра праворуч */
            sibling_index = (current_index + 1 < level_size) ? current_index + 1 : current_index;
            dir = DIR_RIGHT;
        } else {
            /* Поточний вузол правий, сестра ліворуч */
            sibling_index = current_index - 1;
            dir = DIR_LEFT;
        }
        
        proof.nodes[proof.count].sibling_hash = tree->nodes[level_offset + sibling_index];
        proof.nodes[proof.count].direction = dir;
        proof.count++;
        
        level_offset += level_size;
        level_size = (level_size + 1) / 2;
        current_index /= 2;
    }
    
    return proof;
}

/* Верифікація доказу */
bool merkle_proof_verify(const char* item, const MerkleProof* proof, Hash root) {
    Hash current = compute_hash(PREFIX_LEAF, item, strlen(item));
    
    for (size_t i = 0; i < proof->count; i++) {
        if (proof->nodes[i].direction == DIR_RIGHT) {
            current = combine_hashes(&current, &proof->nodes[i].sibling_hash);
        } else {
            current = combine_hashes(&proof->nodes[i].sibling_hash, &current);
        }
    }
    
    return memcmp(current.bytes, root.bytes, HASH_SIZE) == 0;
}

void merkle_tree_free(MerkleTree* tree) {
    if (tree) {
        free(tree->nodes);
        free(tree);
    }
}

int main(void) {
    const char* transactions[] = {
        "Tx1: Alice->Bob 5 BTC",
        "Tx2: Bob->Charlie 2 BTC",
        "Tx3: Charlie->Dave 1 BTC",
        "Tx4: Dave->Eve 0.5 BTC"
    };
    size_t count = 4;
    
    MerkleTree* tree = merkle_tree_create(transactions, count);
    Hash root = tree->nodes[tree->total_nodes - 1];
    
    printf("Merkle Root: ");
    for (int i = 0; i < 8; i++) printf("%02x", root.bytes[i]);
    printf("...\n");
    
    /* Генерація доказу для транзакції Tx2 (індекс 1) */
    MerkleProof proof = merkle_tree_prove(tree, 1);
    
    bool valid = merkle_proof_verify(transactions[1], &proof, root);
    printf("Перевірка Tx2: %s\n", valid ? "УСПІШНО (VALID)" : "ПОМИЛКА");
    
    /* Спроба підробки */
    bool fake_valid = merkle_proof_verify("Tx2: Bob->Charlie 100 BTC", &proof, root);
    printf("Перевірка підробленої Tx2: %s\n", fake_valid ? "УСПІШНО" : "ВІДХИЛЕНО (INVALID)");
    
    free(proof.nodes);
    merkle_tree_free(tree);
    return 0;
}
