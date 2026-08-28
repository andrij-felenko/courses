// КАТЕГОРИЧНО НЕПРАВИЛЬНО:
if (queue->count == 0) {
    pthread_cond_wait(&queue->not_empty, &queue->lock);
}
// Тут черга все ще може бути порожньою через гонку або хибне пробудження!

// ПРАВИЛЬНО (семантика Меса):
while (queue->count == 0 && !queue->is_closed) {
    pthread_cond_wait(&queue->not_empty, &queue->lock);
}
