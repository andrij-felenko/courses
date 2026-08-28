struct Queue {
    Id* elements;      // Покажчик на динамічний масив ідентифікаторів Id
    int count;         // Поточна кількість елементів у черзі
    int alloc;         // Ємність виділеного блоку пам'яті
};

extern "C" {
    void queue_init(Queue* q);
    void queue_free(Queue* q);
    void queue_push(Queue* q, Id id);
    void queue_push2(Queue* q, Id id1, Id id2);
    Id queue_pop(Queue* q);
    void queue_empty(Queue* q);
}
