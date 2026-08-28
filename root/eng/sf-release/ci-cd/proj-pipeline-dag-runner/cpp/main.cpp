#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <memory>
#include <span>

enum class JobStatus {
    Pending,
    Ready,
    Running,
    Success,
    Failed,
    Skipped
};

struct Job {
    std::string name;
    std::chrono::milliseconds duration;
    bool should_fail{false};
    JobStatus status{JobStatus::Pending};
    int in_degree{0};
    std::vector<std::string> dependencies;
    std::vector<std::string> dependents;
};

class DagRunner {
public:
    explicit DagRunner(std::size_t worker_count = 4)
        : worker_count_(worker_count) {}

    void add_job(std::string name, std::chrono::milliseconds duration, bool should_fail = false) {
        jobs_.emplace(name, Job{
            .name = std::move(name),
            .duration = duration,
            .should_fail = should_fail
        });
    }

    void add_dependency(std::string_view parent_name, std::string_view child_name) {
        auto p_it = jobs_.find(std::string(parent_name));
        auto c_it = jobs_.find(std::string(child_name));
        if (p_it != jobs_.end() && c_it != jobs_.end()) {
            c_it->second.dependencies.push_back(p_it->first);
            c_it->second.in_degree++;
            p_it->second.dependents.push_back(c_it->first);
        }
    }

    void run() {
        {
            std::lock_guard lock(mutex_);
            for (auto& [name, job] : jobs_) {
                if (job.in_degree == 0) {
                    job.status = JobStatus::Ready;
                    ready_queue_.push(name);
                }
            }
        }

        std::vector<std::jthread> workers;
        workers.reserve(worker_count_);
        for (std::size_t i = 0; i < worker_count_; ++i) {
            workers.emplace_back([this](std::stop_token st) {
                worker_loop(st);
            });
        }

        {
            std::unique_lock lock(mutex_);
            cv_done_.wait(lock, [this] {
                return completed_count_ >= jobs_.size();
            });
            shutdown_ = true;
        }
        cv_ready_.notify_all();
    }

private:
    void cascade_skip(const std::string& failed_name) {
        for (auto& [name, job] : jobs_) {
            if (job.status == JobStatus::Pending || job.status == JobStatus::Ready) {
                for (const auto& dep : job.dependencies) {
                    if (dep == failed_name) {
                        job.status = JobStatus::Skipped;
                        completed_count_++;
                        std::cout << "[RUNNER C++] Job '" << job.name 
                                  << "' SKIPPED (upstream '" << failed_name << "' failed)\n";
                        cascade_skip(job.name);
                        break;
                    }
                }
            }
        }
    }

    void worker_loop(std::stop_token st) {
        while (!st.stop_requested()) {
            std::string current_job_name;

            {
                std::unique_lock lock(mutex_);
                cv_ready_.wait(lock, [this, &st] {
                    return !ready_queue_.empty() || shutdown_ || st.stop_requested();
                });

                if (shutdown_ || st.stop_requested() || completed_count_ >= jobs_.size()) {
                    break;
                }

                if (ready_queue_.empty()) continue;

                current_job_name = ready_queue_.front();
                ready_queue_.pop();
                jobs_[current_job_name].status = JobStatus::Running;
            }

            auto& job = jobs_[current_job_name];
            std::cout << "[RUNNER C++] Starting job '" << job.name 
                      << "' (" << job.duration.count() << " ms)...\n";

            std::this_thread::sleep_for(job.duration);
            bool success = !job.should_fail;

            {
                std::lock_guard lock(mutex_);
                completed_count_++;

                if (success) {
                    job.status = JobStatus::Success;
                    std::cout << "[RUNNER C++] Job '" << job.name << "' COMPLETED SUCCESS\n";

                    for (const auto& dep_name : job.dependents) {
                        auto& child = jobs_[dep_name];
                        if (child.status == JobStatus::Pending) {
                            child.in_degree--;
                            if (child.in_degree == 0) {
                                child.status = JobStatus::Ready;
                                ready_queue_.push(child.name);
                                cv_ready_.notify_one();
                            }
                        }
                    }
                } else {
                    job.status = JobStatus::Failed;
                    std::cout << "[RUNNER C++] Job '" << job.name << "' FAILED!\n";
                    cascade_skip(job.name);
                }

                if (completed_count_ >= jobs_.size()) {
                    cv_done_.notify_all();
                    cv_ready_.notify_all();
                }
            }
        }
    }

    std::size_t worker_count_;
    std::unordered_map<std::string, Job> jobs_;
    std::queue<std::string> ready_queue_;
    std::size_t completed_count_{0};
    bool shutdown_{false};
    std::mutex mutex_;
    std::condition_variable cv_ready_;
    std::condition_variable cv_done_;
};

int main() {
    DagRunner runner(4);

    runner.add_job("lint-and-format", std::chrono::milliseconds(50));
    runner.add_job("compile-binary", std::chrono::milliseconds(100));
    runner.add_job("unit-tests", std::chrono::milliseconds(80));
    runner.add_job("security-sast", std::chrono::milliseconds(60));
    runner.add_job("e2e-integration", std::chrono::milliseconds(120));
    runner.add_job("build-oci-image", std::chrono::milliseconds(90));

    runner.add_dependency("lint-and-format", "unit-tests");
    runner.add_dependency("compile-binary", "unit-tests");
    runner.add_dependency("compile-binary", "security-sast");
    runner.add_dependency("unit-tests", "e2e-integration");
    runner.add_dependency("security-sast", "e2e-integration");
    runner.add_dependency("e2e-integration", "build-oci-image");

    std::cout << "=== Starting C++20 DAG Pipeline Runner ===\n";
    runner.run();
    std::cout << "=== Pipeline Execution Finished ===\n";
    return 0;
}
