/* Безпечний запис у чергу без блокувань із бар'єром пам'яті */
void push_frame_safe(const ImuSampleFrame* frame) {
    uint32_t h = g_imu_ring.head;
    g_imu_ring.frames[h] = *frame;

    /* Гарантуємо, що запис корисного навантаження завершено до оновлення head */
    __DMB();

    g_imu_ring.head = (h + 1) % RING_BUFFER_CAPACITY;
}
