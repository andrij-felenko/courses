#define MAX_DEGREE 4
#define TAPE_SIZE 64

typedef struct {
    int64_t coeffs[MAX_DEGREE];
} NonStandardInt;

typedef struct {
    uint8_t tape[TAPE_SIZE];
    size_t head_pos;
    int current_state;
    NonStandardInt step_count;
    bool halted;
} NonStandardTM;
