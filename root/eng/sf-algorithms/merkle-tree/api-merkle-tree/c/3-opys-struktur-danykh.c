typedef struct {
    uint8_t bytes[MERKLE_HASH_SIZE];
} merkle_hash_t;

typedef enum {
    MERKLE_DIR_LEFT  = 0,  /* Сестра розташована ліворуч від поточного вузла */
    MERKLE_DIR_RIGHT = 1   /* Сестра розташована праворуч від поточного вузла */
} merkle_direction_t;

typedef struct {
    merkle_hash_t sibling_hash;
    merkle_direction_t direction;
} merkle_proof_node_t;

typedef struct {
    merkle_proof_node_t* nodes;
    size_t node_count;
} merkle_proof_t;

typedef struct merkle_tree_s merkle_tree_t;
