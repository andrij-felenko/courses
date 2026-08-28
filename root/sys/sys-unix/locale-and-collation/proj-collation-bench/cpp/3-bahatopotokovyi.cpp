// C++17: Багатопотокова обробка через std::thread та ізольовані std::locale
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <thread>
#include <locale>

void thread_sort_cpp(std::vector<std::string>& data_chunk, const std::string& loc_name) {
    std::locale loc(loc_name);
    const auto& coll = std::use_facet<std::collate<char>>(loc);

    std::sort(data_chunk.begin(), data_chunk.end(), [&coll](const std::string& a, const std::string& b) {
        return coll.compare(a.data(), a.data() + a.size(),
                            b.data(), b.data() + b.size()) < 0;
    });
}

void run_multithreaded_bench_cpp(std::vector<std::string>& full_dataset) {
    std::size_t num_threads = 4;
    std::size_t chunk_size = full_dataset.size() / num_threads;

    std::vector<std::vector<std::string>> chunks(num_threads);
    for (std::size_t i = 0; i < num_threads; ++i) {
        auto start_it = full_dataset.begin() + i * chunk_size;
        auto end_it = (i == num_threads - 1) ? full_dataset.end() : start_it + chunk_size;
        chunks[i].assign(start_it, end_it);
    }

    std::vector<std::thread> workers;
    for (std::size_t i = 0; i < num_threads; ++i) {
        workers.emplace_back(thread_sort_cpp, std::ref(chunks[i]), "uk_UA.UTF-8");
    }

    for (auto& t : workers) {
        t.join();
    }
    std::cout << "[C++] Багатопотокове сортування успішно завершено на " << num_threads << " потоках.\n";
}
