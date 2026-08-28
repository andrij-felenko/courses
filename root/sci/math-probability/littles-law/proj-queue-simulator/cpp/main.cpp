#include <iostream>
#include <vector>
#include <queue>
#include <random>
#include <string>
#include <iomanip>
#include <cmath>
#include <memory>
#include <functional>

enum class EventType { ARRIVAL, DEPARTURE };
enum class Discipline { FIFO, LIFO };

struct Request {
    uint64_t id;
    double arrive_time;
};

struct Event {
    double time;
    EventType type;
    Request req;

    bool operator>(const Event& other) const {
        return time > other.time;
    }
};

class QueueSimulator {
public:
    QueueSimulator(double arrival_rate, double service_rate, Discipline disc, bool heavy_tailed = false)
        : lambda_(arrival_rate), mu_(service_rate), discipline_(disc), heavy_tailed_(heavy_tailed),
          rng_(1337), exp_arrival_(arrival_rate), exp_service_(service_rate),
          pareto_dist_(1.5) {}

    void run(double max_time) {
        current_time_ = 0.0;
        last_event_time_ = 0.0;
        in_system_count_ = 0;
        area_n_ = 0.0;
        completed_requests_ = 0;
        total_residence_time_ = 0.0;
        server_busy_ = false;
        next_req_id_ = 1;

        // Плануємо перше надходження
        schedule_arrival(0.0);

        while (!event_queue_.empty() && current_time_ < max_time) {
            Event ev = event_queue_.top();
            event_queue_.pop();

            // Оновлюємо інтеграл площі ∫ N(t) dt
            double dt = ev.time - last_event_time_;
            area_n_ += in_system_count_ * dt;
            current_time_ = ev.time;
            last_event_time_ = ev.time;

            if (ev.type == EventType::ARRIVAL) {
                handle_arrival(ev.req);
            } else {
                handle_departure(ev.req);
            }
        }
    }

    void print_results(const std::string& test_name) const {
        double l_measured = area_n_ / current_time_;
        double lambda_measured = completed_requests_ / current_time_;
        double w_measured = total_residence_time_ / completed_requests_;
        double l_little = lambda_measured * w_measured;
        double error_pct = std::abs(l_measured - l_little) / l_measured * 100.0;

        std::cout << "=== " << test_name << " ===\n"
                  << "Симуляційний час: " << std::fixed << std::setprecision(1) << current_time_ << " с\n"
                  << "Завершено заявок: " << completed_requests_ << "\n"
                  << "L (виміряне)    : " << std::setprecision(5) << l_measured << "\n"
                  << "λ (виміряне)    : " << lambda_measured << " req/s\n"
                  << "W (виміряне)    : " << w_measured << " s\n"
                  << "λ · W           : " << l_little << "\n"
                  << "Похибка Літтла  : " << std::setprecision(4) << error_pct << " %\n\n";
    }

private:
    double lambda_;
    double mu_;
    Discipline discipline_;
    bool heavy_tailed_;

    std::mt19937_64 rng_;
    std::exponential_distribution<double> exp_arrival_;
    std::exponential_distribution<double> exp_service_;
    std::pareto_distribution<double> pareto_dist_;

    std::priority_queue<Event, std::vector<Event>, std::greater<Event>> event_queue_;
    std::vector<Request> waiting_queue_;

    double current_time_ = 0.0;
    double last_event_time_ = 0.0;
    uint64_t in_system_count_ = 0;
    double area_n_ = 0.0;
    uint64_t completed_requests_ = 0;
    double total_residence_time_ = 0.0;
    bool server_busy_ = false;
    uint64_t next_req_id_ = 1;

    double next_service_time() {
        if (!heavy_tailed_) {
            return exp_service_(rng_);
        }
        // Парето з узгодженим середнім 1/mu (alpha = 1.5)
        return (1.0 / mu_) * (pareto_dist_(rng_) / 3.0);
    }

    void schedule_arrival(double after_time) {
        double dt = exp_arrival_(rng_);
        Request req{next_req_id_++, after_time + dt};
        event_queue_.push(Event{req.arrive_time, EventType::ARRIVAL, req});
    }

    void handle_arrival(const Request& req) {
        in_system_count_++;
        if (!server_busy_) {
            server_busy_ = true;
            double st = next_service_time();
            event_queue_.push(Event{current_time_ + st, EventType::DEPARTURE, req});
        } else {
            waiting_queue_.push_back(req);
        }
        schedule_arrival(current_time_);
    }

    void handle_departure(const Request& req) {
        in_system_count_--;
        completed_requests_++;
        total_residence_time_ += (current_time_ - req.arrive_time);

        if (!waiting_queue_.empty()) {
            Request next_req;
            if (discipline_ == Discipline::FIFO) {
                next_req = waiting_queue_.front();
                waiting_queue_.erase(waiting_queue_.begin());
            } else { // LIFO
                next_req = waiting_queue_.back();
                waiting_queue_.pop_back();
            }
            double st = next_service_time();
            event_queue_.push(Event{current_time_ + st, EventType::DEPARTURE, next_req});
        } else {
            server_busy_ = false;
        }
    }
};

int main() {
    // Тест 1: Класична черга M/M/1 FIFO (λ = 8.0, μ = 10.0, ρ = 0.8)
    QueueSimulator sim1(8.0, 10.0, Discipline::FIFO);
    sim1.run(100000.0);
    sim1.print_results("Тест 1: M/M/1 черга з дисципліною FIFO");

    // Тест 2: Черга M/M/1 LIFO (стековий порядок обслуговування)
    QueueSimulator sim2(8.0, 10.0, Discipline::LIFO);
    sim2.run(100000.0);
    sim2.print_results("Тест 2: M/M/1 черга з дисципліною LIFO");

    // Тест 3: Черга з важкими хвостами обслуговування M/G/1 (Парето)
    QueueSimulator sim3(5.0, 10.0, Discipline::FIFO, true);
    sim3.run(100000.0);
    sim3.print_results("Тест 3: M/G/1 з важкими хвостами (Парето)");

    return 0;
}
