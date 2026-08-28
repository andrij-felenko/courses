// C++20: Оптимальний обхід неперервного вектора проти вузлового списку
#include <iostream>
#include <vector>
#include <list>
#include <numeric>
#include <chrono>

struct BenchmarkResult {
    double duration_ms;
    int64_t total_sum;
};

// Функція запобігання усуненню обчислень компілятором
template <typename T>
void do_not_optimize(T&& val) {
    asm volatile("" : : "g"(val) : "memory");
}

BenchmarkResult bench_vector(size_t count) {
    std::vector<int32_t> vec(count);
    std::iota(vec.begin(), vec.end(), 1);

    auto start = std::chrono::high_resolution_clock::now();
    int64_t sum = 0;
    for (int32_t val : vec) {
        sum += val;
    }
    do_not_optimize(sum);
    auto end = std::chrono::high_resolution_clock::now();
    
    double ms = std::chrono::duration<double, std::milli>(end - start).count();
    return {ms, sum};
}

BenchmarkResult bench_list(size_t count) {
    std::vector<int32_t> temp(count);
    std::iota(temp.begin(), temp.end(), 1);
    std::list<int32_t> lst(temp.begin(), temp.end());

    auto start = std::chrono::high_resolution_clock::now();
    int64_t sum = 0;
    for (int32_t val : lst) {
        sum += val;
    }
    do_not_optimize(sum);
    auto end = std::chrono::high_resolution_clock::now();
    
    double ms = std::chrono::duration<double, std::milli>(end - start).count();
    return {ms, sum};
}

int main() {
    constexpr size_t N = 10'000'000;
    auto res_vec = bench_vector(N);
    auto res_lst = bench_list(N);

    std::cout << "Vector sum: " << res_vec.total_sum << " in " << res_vec.duration_ms << " ms\n";
    std::cout << "List sum:   " << res_lst.total_sum << " in " << res_lst.duration_ms << " ms\n";
    std::cout << "Прискорення Vector відносно List: " << (res_lst.duration_ms / res_vec.duration_ms) << "x\n";
}
