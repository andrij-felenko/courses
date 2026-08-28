// Головний приклад використання на C++

struct QuoteData {
    double price{0.0};
    uint64_t volume{0};
    uint64_t timestamp{0};
};

static Seqlock g_seqlock;
static QuoteData g_quote;

void run_writer() {
    for (uint64_t i = 1; i <= 100000; ++i) {
        {
            SeqlockWriterGuard guard(g_seqlock);
            g_quote.price = 100.0 + static_cast<double>(i);
            g_quote.volume = i * 10;
            g_quote.timestamp = i;
        }
    }
}

void run_reader(int id) {
    uint64_t successful_reads = 0;
    uint64_t retries = 0;

    for (int i = 0; i < 10000; ++i) {
        QuoteData local_copy;
        uint32_t seq = 0;

        do {
            seq = g_seqlock.read_begin();
            local_copy = g_quote;
            if (g_seqlock.read_retry(seq)) {
                retries++;
                continue;
            }
            break;
        } while (true);

        if (local_copy.volume != local_copy.timestamp * 10) {
            std::cerr << "ПОМИЛКА [Читач " << id << "]: Неконсистентні дані!\n";
        } else {
            successful_reads++;
        }
    }

    std::cout << "Читач " << id << " завершив: успішно=" << successful_reads
              << ", повторів=" << retries << "\n";
}

int main() {
    std::thread w(run_writer);
    std::thread r1(run_reader, 1);
    std::thread r2(run_reader, 2);

    w.join();
    r1.join();
    r2.join();

    return 0;
}
