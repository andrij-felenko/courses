typedef struct {
    Goal *buffer;
    size_t capacity;
    uint8_t head;
    uint8_t tail;
    uint8_t count;
    Goal active_goal;
    bool has_active_goal;
    void *context;
} GoalEngine;

void goal_engine_init(GoalEngine *ge, Goal *buffer, size_t capacity, void *ctx);
bool goal_engine_push(GoalEngine *ge, const Goal *goal);
bool goal_engine_fetch_next(GoalEngine *ge);
void goal_engine_step(GoalEngine *ge, uint32_t now_ms, EventQueue *out_queue);
void goal_engine_complete_active(GoalEngine *ge);
void goal_engine_abort_all(GoalEngine *ge);
