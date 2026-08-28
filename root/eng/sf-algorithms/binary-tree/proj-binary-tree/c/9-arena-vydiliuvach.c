// Простий арена-виділювач пам'яті для вузлів двійкового дерева на C
typedef struct TreeArena {
    Node* memory_block;
    size_t capacity;
    size_t offset;
} TreeArena;

TreeArena* create_arena(size_t capacity) {
    TreeArena* arena = (TreeArena*)malloc(sizeof(TreeArena));
    arena->memory_block = (Node*)malloc(capacity * sizeof(Node));
    arena->capacity = capacity;
    arena->offset = 0;
    return arena;
}

Node* arena_alloc_node(TreeArena* arena, int val) {
    if (arena->offset >= arena->capacity) {
        fprintf(stderr, "Арена вичерпана!\n");
        return NULL;
    }
    Node* node = &arena->memory_block[arena->offset++];
    node->data = val;
    node->left = NULL;
    node->right = NULL;
    return node;
}

void free_arena(TreeArena* arena) {
    free(arena->memory_block);
    free(arena);
}
