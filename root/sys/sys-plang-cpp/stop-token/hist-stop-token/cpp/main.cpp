// Історичний підхід Boost.Thread (2007)
void worker_boost() {
    try {
        while (true) {
            boost::this_thread::interruption_point(); // Точка перевірки
            do_work();
        }
    } catch (const boost::thread_interrupted&) {
        // Чисте переривання та звільнення ресурсів
    }
}
