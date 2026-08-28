#include <shared_mutex>
#include <iostream>

std::shared_mutex rw_mutex;
int shared_data = 42;

void reader_thread() {
    // RAII-захоплення сумісного замка (читання)
    std::shared_lock<std::shared_mutex> lock(rw_mutex);
    
    // Безпечна критична секція читання
    std::cout << "Data value: " << shared_data << "\n";
    
    // Деструктор lock автоматично викликає rw_mutex.unlock_shared()
}

void writer_thread(int new_value) {
    // RAII-захоплення монопольного замка (запис)
    std::unique_lock<std::shared_mutex> lock(rw_mutex);
    
    // Монопольна критична секція запису
    shared_data = new_value;
    
    // Деструктор lock автоматично викликає rw_mutex.unlock()
}
