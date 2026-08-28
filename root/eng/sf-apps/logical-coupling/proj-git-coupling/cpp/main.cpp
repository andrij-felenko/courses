#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <iomanip>

struct PairKey {
    std::string file_a;
    std::string file_b;

    bool operator==(const PairKey& other) const {
        return file_a == other.file_a && file_b == other.file_b;
    }
};

struct PairKeyHash {
    std::size_t operator()(const PairKey& k) const {
        std::size_t h1 = std::hash<std::string>{}(k.file_a);
        std::size_t h2 = std::hash<std::string>{}(k.file_b);
        return h1 ^ (h2 << 1);
    }
};

struct AnalysisResult {
    std::string file_a;
    std::string file_b;
    int co_changes;
    double confidence_a_to_b;
    double confidence_b_to_a;
    double jaccard;
};

class GitCouplingDetector {
public:
    static constexpr int MAX_FILES_THRESHOLD = 50;

    void process_stream(std::istream& in) {
        std::string line;
        std::vector<std::string> current_commit;

        while (std::getline(in, line)) {
            while (!line.empty() && (line.back() == '\r' || line.back() == ' ')) {
                line.pop_back();
            }
            if (line.empty()) continue;

            if (line.rfind("COMMIT:", 0) == 0) {
                flush_commit(current_commit);
                current_commit.clear();
                total_commits_++;
            } else {
                current_commit.push_back(line);
            }
        }
        flush_commit(current_commit);
    }

    std::vector<AnalysisResult> compute_metrics(int min_co_changes = 2) const {
        std::vector<AnalysisResult> results;
        for (const auto& [pair, count] : pair_counts_) {
            if (count < min_co_changes) continue;

            int n_a = file_counts_.at(pair.file_a);
            int n_b = file_counts_.at(pair.file_b);

            double conf_ab = static_cast<double>(count) / n_a * 100.0;
            double conf_ba = static_cast<double>(count) / n_b * 100.0;
            double jaccard = static_cast<double>(count) / (n_a + n_b - count) * 100.0;

            results.push_back({pair.file_a, pair.file_b, count, conf_ab, conf_ba, jaccard});
        }

        std::sort(results.begin(), results.end(), [](const auto& lhs, const auto& rhs) {
            return lhs.jaccard > rhs.jaccard;
        });

        return results;
    }

    int total_commits() const { return total_commits_; }

private:
    void flush_commit(std::vector<std::string>& files) {
        if (files.size() < 2 || files.size() > MAX_FILES_THRESHOLD) return;

        std::sort(files.begin(), files.end());
        files.erase(std::unique(files.begin(), files.end()), files.end());

        for (const auto& f : files) {
            file_counts_[f]++;
        }

        for (std::size_t i = 0; i < files.size(); ++i) {
            for (std::size_t j = i + 1; j < files.size(); ++j) {
                PairKey key{files[i], files[j]};
                pair_counts_[key]++;
            }
        }
    }

    int total_commits_ = 0;
    std::unordered_map<std::string, int> file_counts_;
    std::unordered_map<PairKey, int, PairKeyHash> pair_counts_;
};

int main() {
    GitCouplingDetector detector;
    detector.process_stream(std::cin);

    auto results = detector.compute_metrics(2);

    std::cout << "=== ТОП ПАР ІЗ ЛОГІЧНИМ ЗАЧЕПЛЕННЯМ (Всього транзакцій: " 
              << detector.total_commits() << ") ===\n";
    std::cout << std::left << std::setw(35) << "Файл A" 
              << std::setw(35) << "Файл B" 
              << std::right << std::setw(8) << "Спільні" 
              << std::setw(11) << "Conf A->B" 
              << std::setw(11) << "Conf B->A" 
              << std::setw(10) << "Jaccard" << "\n";

    for (std::size_t i = 0; i < std::min<std::size_t>(results.size(), 20); ++i) {
        const auto& r = results[i];
        std::cout << std::left << std::setw(35) << r.file_a.substr(0, 34)
                  << std::setw(35) << r.file_b.substr(0, 34)
                  << std::right << std::setw(8) << r.co_changes
                  << std::fixed << std::setprecision(1)
                  << std::setw(10) << r.confidence_a_to_b << "%"
                  << std::setw(10) << r.confidence_b_to_a << "%"
                  << std::setw(9) << r.jaccard << "%\n";
    }

    return 0;
}
