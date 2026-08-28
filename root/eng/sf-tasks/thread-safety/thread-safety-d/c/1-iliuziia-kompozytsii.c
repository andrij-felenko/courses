bool thread_safe_queue_try_pop(queue_t *q, item_t *out_item) {
    pthread_mutex_lock(&q->lock);
    if (q->head == NULL) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }
    *out_item = dequeue_internal(q);
    pthread_mutex_unlock(&q->lock);
    return true;
}
