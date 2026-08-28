#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <duckdb.hpp>

namespace analytics {

class InProcessAnalytics {
public:
    InProcessAnalytics() : db_(nullptr), con_(db_) {
        con_.Query("CREATE TABLE metrics (timestamp BIGINT, value DOUBLE);");
        con_.Query("INSERT INTO metrics SELECT range, random() * 50.0 FROM range(500000);");
    }

    /* Вибірка з безкопійним читанням через нативний C++ API DuckDB */
    double calculate_parallel_aggregate() {
        auto result = con_.Query("SELECT value FROM metrics WHERE value > 25.0;");
        if (!result->success) {
            throw std::runtime_error(result->GetError());
        }

        double total_sum = 0.0;
        size_t total_rows = 0;

        /* Ітерація по векторних чанках DataChunk */
        while (auto chunk = result->Fetch()) {
            if (!chunk || chunk->size() == 0) break;

            /* Отримання стовпцевого масиву */
            auto& vector = chunk->data[0];
            const auto* values = duckdb::FlatVector::GetData<double>(vector);
            size_t count = chunk->size();

            /* Безпечний діапазон std::span */
            std::span<const double> value_span(values, count);

            for (double v : value_span) {
                total_sum += v;
            }
            total_rows += count;
        }

        return total_rows > 0 ? (total_sum / static_cast<double>(total_rows)) : 0.0;
    }

private:
    duckdb::DuckDB db_;
    duckdb::Connection con_;
};

} // namespace analytics
