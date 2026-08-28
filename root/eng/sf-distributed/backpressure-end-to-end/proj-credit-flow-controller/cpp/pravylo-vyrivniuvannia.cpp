// Розділення гарячих змінних на окремі кеш-лінії
struct alignas(64) IngressState {
    size_t tail{0};
    int32_t active_credits{0};
    bool socket_paused{false};
};

struct alignas(64) WorkerState {
    size_t head{0};
};
