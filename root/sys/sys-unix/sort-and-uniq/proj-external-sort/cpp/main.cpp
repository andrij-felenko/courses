#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <queue>
#include <memory>
#include <algorithm>
#include <filesystem>
#include <unistd.h>

namespace fs = std::filesystem;

class ExternalMergeSort {
public:
    explicit ExternalMergeSort(size_t mem_limit_bytes = 4 * 1024 * 1024)
        : mem_limit_(mem_limit_bytes) {}

    void sort(std::istream& in, std::ostream& out) {
        auto run_files = generate_runs(in);
        merge_runs(run_files, out);
    }

private:
    struct RunStream {
        std::ifstream file;
        fs::path path;
        std::string current_line;

        explicit RunStream(fs::path p) : path(std::move(p)), file(path) {
            advance();
        }

        [[nodiscard]] bool is_valid() const noexcept {
            return !current_line.empty() || file.good();
        }

        bool advance() {
            if (std::getline(file, current_line)) {
                current_line.push_back('\n');
                return true;
            }
            current_line.clear();
            return false;
        }
    };

    struct StreamComparator {
        bool operator()(const std::unique_ptr<RunStream>& a,
                        const std::unique_ptr<RunStream>& b) const {
            return a->current_line > b->current_line; // Мін-купа для вибору найменшого рядка
        }
    };

    std::vector<fs::path> generate_runs(std::istream& in) {
        std::vector<fs::path> run_files;
        std::vector<std::string> buffer;
        size_t current_bytes = 0;
        std::string line;
        size_t run_index = 0;

        auto flush_buffer = [&]() {
            if (buffer.empty()) return;
            std::sort(buffer.begin(), buffer.end());

            fs::path temp_path = fs::temp_directory_path() /
                ("extsort_cpp_" + std::to_string(getpid()) + "_" + std::to_string(run_index++) + ".tmp");

            std::ofstream out(temp_path, std::ios::binary);
            for (const auto& item : buffer) {
                out << item << '\n';
            }

            run_files.push_back(temp_path);
            buffer.clear();
            current_bytes = 0;
        };

        while (std::getline(in, line)) {
            current_bytes += line.size() + sizeof(std::string);
            buffer.push_back(std::move(line));

            if (current_bytes >= mem_limit_) {
                flush_buffer();
            }
        }

        flush_buffer();
        return run_files;
    }

    void merge_runs(const std::vector<fs::path>& run_files, std::ostream& out) {
        if (run_files.empty()) return;

        std::priority_queue<
            std::unique_ptr<RunStream>,
            std::vector<std::unique_ptr<RunStream>>,
            StreamComparator
        > min_heap;

        for (const auto& path : run_files) {
            auto stream = std::make_unique<RunStream>(path);
            if (!stream->current_line.empty()) {
                min_heap.push(std::move(stream));
            }
        }

        while (!min_heap.empty()) {
            auto min_stream = std::move(const_cast<std::unique_ptr<RunStream>&>(min_heap.top()));
            min_heap.pop();

            out << min_stream->current_line;

            if (min_stream->advance()) {
                min_heap.push(std::move(min_stream));
            }
        }

        for (const auto& path : run_files) {
            std::error_code ec;
            fs::remove(path, ec);
        }
    }

    size_t mem_limit_;
};

int main(int argc, char* argv[]) {
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);

    ExternalMergeSort sorter(8 * 1024 * 1024); // 8 MB RAM буфер

    if (argc > 1) {
        std::ifstream in(argv[1], std::ios::binary);
        if (!in) {
            std::cerr << "Помилка відкриття файлу: " << argv[1] << '\n';
            return 1;
        }
        sorter.sort(in, std::cout);
    } else {
        sorter.sort(std::cin, std::cout);
    }

    return 0;
}
