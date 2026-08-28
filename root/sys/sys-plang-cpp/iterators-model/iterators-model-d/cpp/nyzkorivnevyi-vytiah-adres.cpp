#include <memory>
#include <vector>

void process_c_api(const int* data, size_t count);

void example(const std::vector<int>& vec) {
    if (vec.empty()) return;

    // Безпечний витяг адреси пам'яті без розіменування!
    const int* ptr = std::to_address(vec.begin());
    process_c_api(ptr, vec.size());
}
