#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

// Алфавіт розгалуження B = 32 (5 бітів на рівень)
#define BITS_PER_LEVEL 5
#define BRANCH_FACTOR 32
#define BITMAP_MASK 0x1F

typedef enum {
    NODE_LEAF,
    NODE_BITMAP
} NodeType;

typedef struct Node Node;

typedef struct {
    char* key;
    uint32_t hash;
    int value;
} KeyValue;

typedef struct {
    uint32_t bitmap;
    Node** children;
} BitmapNode;

struct Node {
    NodeType type;
    union {
        KeyValue leaf;
        BitmapNode internal;
    } data;
};

// Некриптографічна геш-функція FNV-1a (32 біти)
uint32_t fnv1a_hash(const char* key) {
    uint32_t hash = 2166136261U;
    while (*key) {
        hash ^= (uint8_t)(*key++);
        hash *= 16777619U;
    }
    return hash;
}

// Підрахунок одиничних бітів через убудовану інструкцію CPU
static inline int popcount32(uint32_t val) {
#if defined(__GNUC__) || defined(__clang__)
    return __builtin_popcount(val);
#else
    val = val - ((val >> 1) & 0x55555555);
    val = (val & 0x33333333) + ((val >> 2) & 0x33333333);
    return (((val + (val >> 4)) & 0x0F0F0F0F) * 0x01010101) >> 24;
#endif
}

Node* create_leaf(const char* key, uint32_t hash, int value) {
    Node* node = (Node*)malloc(sizeof(Node));
    if (!node) return NULL;
    node->type = NODE_LEAF;
    node->data.leaf.key = strdup(key);
    node->data.leaf.hash = hash;
    node->data.leaf.value = value;
    return node;
}

Node* create_bitmap_node(uint32_t bitmap, Node** children, int count) {
    Node* node = (Node*)malloc(sizeof(Node));
    if (!node) return NULL;
    node->type = NODE_BITMAP;
    node->data.internal.bitmap = bitmap;
    node->data.internal.children = (Node**)malloc(sizeof(Node*) * count);
    if (count > 0 && children) {
        memcpy(node->data.internal.children, children, sizeof(Node*) * count);
    }
    return node;
}

// Пошук значення у HAMT за час O(log32 N)
bool hamt_lookup(const Node* root, const char* key, int* out_value) {
    if (!root) return false;
    uint32_t hash = fnv1a_hash(key);
    const Node* curr = root;
    uint32_t shift = 0;

    while (curr) {
        if (curr->type == NODE_LEAF) {
            if (curr->data.leaf.hash == hash && strcmp(curr->data.leaf.key, key) == 0) {
                *out_value = curr->data.leaf.value;
                return true;
            }
            return false;
        }

        uint32_t chunk = (hash >> shift) & BITMAP_MASK;
        uint32_t bit_pos = 1U << chunk;
        uint32_t bitmap = curr->data.internal.bitmap;

        if ((bitmap & bit_pos) == 0) {
            return false;
        }

        int idx = popcount32(bitmap & (bit_pos - 1));
        curr = curr->data.internal.children[idx];
        shift += BITS_PER_LEVEL;
    }
    return false;
}

// Персистентна вставка (Path Copying): повертає новий корінь, не змінюючи старий
Node* hamt_insert_internal(const Node* node, const char* key, uint32_t hash, int value, uint32_t shift) {
    if (!node) {
        return create_leaf(key, hash, value);
    }

    if (node->type == NODE_LEAF) {
        if (node->data.leaf.hash == hash && strcmp(node->data.leaf.key, key) == 0) {
            return create_leaf(key, hash, value);
        }

        uint32_t existing_chunk = (node->data.leaf.hash >> shift) & BITMAP_MASK;
        uint32_t new_chunk = (hash >> shift) & BITMAP_MASK;

        if (existing_chunk == new_chunk) {
            Node* sub_node = hamt_insert_internal(node, key, hash, value, shift + BITS_PER_LEVEL);
            uint32_t bitmap = 1U << existing_chunk;
            Node* children[1] = { sub_node };
            return create_bitmap_node(bitmap, children, 1);
        } else {
            Node* new_leaf = create_leaf(key, hash, value);
            uint32_t bitmap = (1U << existing_chunk) | (1U << new_chunk);
            Node* children[2];

            Node* copied_leaf = create_leaf(node->data.leaf.key, node->data.leaf.hash, node->data.leaf.value);
            if (existing_chunk < new_chunk) {
                children[0] = copied_leaf;
                children[1] = new_leaf;
            } else {
                children[0] = new_leaf;
                children[1] = copied_leaf;
            }
            return create_bitmap_node(bitmap, children, 2);
        }
    }

    uint32_t chunk = (hash >> shift) & BITMAP_MASK;
    uint32_t bit_pos = 1U << chunk;
    uint32_t bitmap = node->data.internal.bitmap;
    int count = popcount32(bitmap);

    if ((bitmap & bit_pos) != 0) {
        int idx = popcount32(bitmap & (bit_pos - 1));
        Node* updated_child = hamt_insert_internal(node->data.internal.children[idx], key, hash, value, shift + BITS_PER_LEVEL);

        Node** new_children = (Node**)malloc(sizeof(Node*) * count);
        for (int i = 0; i < count; i++) {
            new_children[i] = (i == idx) ? updated_child : node->data.internal.children[i];
        }
        return create_bitmap_node(bitmap, new_children, count);
    } else {
        Node* new_leaf = create_leaf(key, hash, value);
        uint32_t new_bitmap = bitmap | bit_pos;
        int idx = popcount32(bitmap & (bit_pos - 1));

        Node** new_children = (Node**)malloc(sizeof(Node*) * (count + 1));
        for (int i = 0; i < idx; i++) {
            new_children[i] = node->data.internal.children[i];
        }
        new_children[idx] = new_leaf;
        for (int i = idx; i < count; i++) {
            new_children[i + 1] = node->data.internal.children[i];
        }
        return create_bitmap_node(new_bitmap, new_children, count + 1);
    }
}

Node* hamt_insert(const Node* root, const char* key, int value) {
    uint32_t hash = fnv1a_hash(key);
    return hamt_insert_internal(root, key, hash, value, 0);
}

void hamt_free(Node* node) {
    if (!node) return;
    if (node->type == NODE_LEAF) {
        free(node->data.leaf.key);
    } else if (node->type == NODE_BITMAP) {
        int count = popcount32(node->data.internal.bitmap);
        for (int i = 0; i < count; i++) {
            hamt_free(node->data.internal.children[i]);
        }
        free(node->data.internal.children);
    }
    free(node);
}

int main(void) {
    Node* v1 = NULL;
    v1 = hamt_insert(v1, "alpha", 100);
    v1 = hamt_insert(v1, "beta", 200);

    Node* v2 = hamt_insert(v1, "alpha", 999);

    int val = 0;
    if (hamt_lookup(v1, "alpha", &val)) {
        printf("V1 ['alpha'] = %d (очікується 100)\n", val);
    }
    if (hamt_lookup(v2, "alpha", &val)) {
        printf("V2 ['alpha'] = %d (очікується 999)\n", val);
    }

    hamt_free(v1);
    hamt_free(v2);
    return 0;
}
