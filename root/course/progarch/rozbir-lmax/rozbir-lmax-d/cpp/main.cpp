// виробник: зайняти → записати → опублікувати
int64_t seq = cursor.fetch_add(1, std::memory_order_relaxed) + 1;
slots[seq & mask] = event;                          // маска замість ділення
published.store(seq, std::memory_order_release);    // бар'єр: запис у комірку видно ДО публікації

// споживач: прочитати все опубліковане — одним пакетом
int64_t avail = published.load(std::memory_order_acquire);
while (next <= avail) {
    handle(slots[next & mask]);
    ++next;
}
