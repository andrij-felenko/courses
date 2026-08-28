// Побудова топології двійкового дерева за порядковим індексом (Unranking) мовою C
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef struct Node {
    struct Node* left;
    struct Node* right;
} Node;

static Node* create_node(void) {
    Node* n = (Node*)calloc(1, sizeof(Node));
    return n;
}

Node* build_tree_unrank(size_t n, uint64_t rank, const uint64_t* C) {
    if (n == 0) return NULL;

    Node* root = create_node();
    for (size_t left_size = 0; left_size < n; ++left_size) {
        size_t right_size = n - 1 - left_size;
        uint64_t count = C[left_size] * C[right_size];
        if (rank < count) {
            uint64_t left_rank = rank / C[right_size];
            uint64_t right_rank = rank % C[right_size];
            root->left = build_tree_unrank(left_size, left_rank, C);
            root->right = build_tree_unrank(right_size, right_rank, C);
            return root;
        }
        rank -= count;
    }
    return root;
}
