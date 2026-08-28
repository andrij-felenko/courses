#include <future>
#include <vector>
#include <memory>

template <typename T>
std::future<std::vector<T>> when_all(std::vector<std::future<T>>& futures) {
    auto p = std::make_shared<std::promise<std::vector<T>>>();
    auto shared_futures = std::make_shared<std::vector<std::future<T>>>(std::move(futures));

    std::thread([p, shared_futures]() {
        std::vector<T> results;
        results.reserve(shared_futures->size());
        try {
            for (auto& f : *shared_futures) {
                results.push_back(f.get());
            }
            p->set_value(std::move(results));
        } catch (...) {
            p->set_exception(std::current_exception());
        }
    }).detach();

    return p->get_future();
}
