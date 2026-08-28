#include <future>
#include <thread>
#include <iostream>

int main() {
    std::promise<int> p;
    std::future<int> f = p.get_future();

    // jthread автоматично зробить join() при виході з блоку!
    std::jthread worker([](std::stop_token st, std::promise<int> p) {
        if (!st.stop_requested()) {
            p.set_value(777);
        }
    }, std::move(p));

    std::cout << "Отримано значення від jthread: " << f.get() << std::endl;
} // worker.join() викликається тут автоматично без падінь!
