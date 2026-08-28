/* Небезпечний вхід у сон: вразливий до стану гонитви (C++20) */
namespace emb {

void unsafeSleepEnter(const EventQueue& queue) noexcept {
    if (queue.empty()) {
        // <- НЕБЕЗПЕЧНЕ ВІКНО: переривання ISR виникає тут
        __asm volatile ("wfi");
    }
}

} // namespace emb
