// Ініціалізація замка м'ютекса безпосередньо в умові:
if (std::lock_guard lock(queue_mutex); !task_queue.empty()) {
    auto task = task_queue.front();
    task_queue.pop();
    execute(task);
} // lock гарантовано звільняє м'ютекс тут, ще до виконання наступних дій

switch (std::error_code ec = process_device(); ec.value()) {
    case 0:  log_ok(); break;
    default: handle_error(ec); break;
}
