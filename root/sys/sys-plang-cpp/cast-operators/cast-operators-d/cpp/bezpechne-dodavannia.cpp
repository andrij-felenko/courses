#include <utility>
#include <vector>

void process_vector(std::vector<int>& v);
void process_vector(const std::vector<int>& v);

void caller(std::vector<int>& my_vec) {
    // Явний виклик const-версії функції без небезпечного ручного касту:
    process_vector(std::as_const(my_vec));
}
