#include <iostream>
#include <memory>
#include <thread>
#include <vector>
#include <span>

struct Record {
    int id{0};
    int payload[64]{1};
};

static Record* g_shared_record{nullptr};
static bool g_probe_mode{false};

void reader_worker(long iterations) {
    long valid_reads = 0;

    for (long i = 0; i < iterations; ++i) {
        if (g_probe_mode) {
            // Спостережницький ефект: вивід у std::cout захоплює блокування потоку
            std::cout << "[Reader] Iteration: " << i << "\n";
        }

        Record* rec = g_shared_record;
        if (rec != nullptr) {
            // Потенційний Use-After-Free: читання без володіння або синхронізації
            int first_val = rec->payload[0];
            if (first_val >= 0) {
                valid_reads++;
            }
        }
    }
}

void writer_worker(long iterations) {
    for (long i = 0; i < iterations; ++i) {
        if (g_probe_mode) {
            std::cout << "[Writer] Resetting record: " << i << "\n";
        }

        auto* fresh = new Record{static_cast<int>(i)};
        fresh->payload[0] = static_cast<int>(i + 1);

        Record* old = g_shared_record;
        g_shared_record = fresh;

        if (old != nullptr) {
            delete old; // Створює небезпечне вікно для паралельного читача
        }
    }
}

int main(int argc, char** argv) {
    g_probe_mode = (argc > 1 && argv[1][0] == '1');

    g_shared_record = new Record{0};

    constexpr long iters = 200000;
    std::jthread t_read(reader_worker, iters);
    std::jthread t_write(writer_worker, iters);

    t_read.join();
    t_write.join();

    delete g_shared_record;
    std::cout << "Execution finished successfully.\n";
    return 0;
}
