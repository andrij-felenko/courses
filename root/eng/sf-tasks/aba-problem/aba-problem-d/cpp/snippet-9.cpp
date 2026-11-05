// Класичний вразливий паттерн Pop()
Node* old_top = top.load(std::memory_order_relaxed);
do {
    if (!old_top) return nullptr;
    
    // Небезпечне читання: old_top може бути звільнений іншим потоком 
    // саме в цей мікроінтервал часу!
    Node* next_node = old_top->next; 

    // Допоміжне місце для фазингу та ін'єкції затримок:
    // std::this_thread::yield();

} while (!top.compare_exchange_weak(old_top, next_node,
                                   std::memory_order_release,
                                   std::memory_order_relaxed));
