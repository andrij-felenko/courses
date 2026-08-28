#include <future>
#include <memory>

struct MoveOnlyData {
    std::unique_ptr<int> ptr;
    MoveOnlyData(int val) : ptr(std::make_unique<int>(val)) {}
};

void process_move_only(std::promise<MoveOnlyData> p) {
    MoveOnlyData data(42);
    p.set_value(std::move(data)); // Обов'язкове переміщення!
}

int main() {
    std::promise<MoveOnlyData> p;
    std::future<MoveOnlyData> f = p.get_future();

    std::thread t(process_move_only, std::move(p));

    MoveOnlyData result = f.get(); // Значення переміщується з Shared State
    std::cout << "Отримано значення: " << *result.ptr << std::endl;
    t.join();
}
