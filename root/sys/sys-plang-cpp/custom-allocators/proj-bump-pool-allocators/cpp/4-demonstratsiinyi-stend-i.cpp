#include <list>
#include <chrono>

struct Particle {
    float x, y, z;
    float vx, vy, vz;
    int id;

    Particle(int id_val) : x(0), y(0), z(0), vx(1), vy(1), vz(1), id(id_val) {}
};

int main() {
    std::cout << "=== 1. Тестування ArenaAllocator з std::vector ===" << std::endl;
    {
        Arena arena(1024 * 1024);
        ArenaAllocator<Particle> alloc(arena);

        std::vector<Particle, ArenaAllocator<Particle>> particles(alloc);
        particles.reserve(1000);

        for (int i = 0; i < 1000; ++i) {
            particles.emplace_back(i);
        }

        std::cout << "Створено " << particles.size() << " часток.\n";
        std::cout << "Використано пам'яті в арені: " << arena.used_bytes() << " байтів.\n";

        particles.clear();
        arena.reset();
        std::cout << "Після arena.reset() використано: " << arena.used_bytes() << " байтів.\n\n";
    }

    std::cout << "=== 2. Тестування PoolAllocator з std::list ===" << std::endl;
    {
        FixedPool pool(sizeof(Particle) + 2 * sizeof(void*), 500, alignof(std::max_align_t));
        PoolAllocator<Particle> alloc(pool);

        std::list<Particle, PoolAllocator<Particle>> particle_list(alloc);
        for (int i = 0; i < 100; ++i) {
            particle_list.emplace_back(i);
        }

        std::cout << "Розмір списку: " << particle_list.size() << "\n";
        std::cout << "Активних слотів у пулі: " << pool.allocated_count() << "\n";

        particle_list.pop_front();
        particle_list.pop_front();
        std::cout << "Після видалення 2 вузлів зайнято: " << pool.allocated_count() << " слотів.\n\n";
    }

    std::cout << "=== 3. Тестування StackBufferResource з std::pmr ===" << std::endl;
    {
        StackBufferResource<512> stack_res;

        std::pmr::vector<int> numbers(&stack_res);
        numbers.reserve(64);

        for (int i = 0; i < 64; ++i) {
            numbers.push_back(i * 10);
        }

        std::cout << "Використано на стеку: " << stack_res.bytes_used_on_stack() << " байтів.\n";
        std::cout << "Звернень до купи: " << stack_res.upstream_alloc_count() << "\n";

        numbers.resize(500);
        std::cout << "Після resize(500) звернень до купи: " << stack_res.upstream_alloc_count() << "\n";
    }

    return 0;
}
