// Modern C++20 Implementation: RAII та std::scoped_lock
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

struct Resource {
    std::mutex mtx;
    int id;
};

void acquire_two_resources_safe(Resource& r1, Resource& r2) {
    // std::scoped_lock автоматично застосовує алгоритм запобігання дедлокам
    // (використовує std::lock усередині для атомарного та впорядкованого захоплення)
    std::scoped_lock lock(r1.mtx, r2.mtx);

    // Критична секція
    std::cout << "C++ Safe: Acquired resources " << r1.id 
              << " and " << r2.id << " without ABBA deadlock\n";
    
    // Автоматичне звільнення при виході з області видимості (RAII)
}

int main() {
    Resource res_a{.id = 1};
    Resource res_b{.id = 2};

    // Паралельний запуск двох потоків із протилежним порядком аргументів
    std::jthread t1([&]() { acquire_two_resources_safe(res_a, res_b); });
    std::jthread t2([&]() { acquire_two_resources_safe(res_b, res_a); });

    return 0;
}
