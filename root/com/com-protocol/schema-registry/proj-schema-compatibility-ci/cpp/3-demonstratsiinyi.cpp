int main() {
    using namespace schema_wire;
    using namespace schema_validator;

    std::cout << "=== ТЕСТ 1: C++ Wire Framing та потокобезпечний кеш ===\n";
    ThreadSafeSchemaCache cache;
    cache.put(42, R"({"type":"record","name":"Order","fields":[{"name":"id","type":"long"}]})");

    std::vector<uint8_t> payload = {0xCA, 0xFE, 0xBA, 0xBE};
    auto encoded_frame = encode(42, payload);
    std::cout << "Розмір кадру: " << encoded_frame.size() << " байтів (оверхед = 5 байтів)\n";

    auto parsed = decode(encoded_frame);
    if (parsed) {
        std::cout << "✓ Розпарсено ID: " << parsed->schema_id << "\n";
        auto schema = cache.get(parsed->schema_id);
        if (schema) {
            std::cout << "✓ Схему знайдено в локальному RAM-кеші: " << *schema << "\n";
        }
    }

    std::cout << "\n=== ТЕСТ 2: C++ Валідатор еволюції схем ===\n";
    RecordSchema old_v1{
        .record_name = "OrderPlaced",
        .fields = {
            Field{.name = "order_id", .type = DataType::Int64, .has_default = false},
            Field{.name = "amount", .type = DataType::Int32, .has_default = false}
        }
    };

    RecordSchema new_v2_ok{
        .record_name = "OrderPlaced",
        .fields = {
            Field{.name = "order_id", .type = DataType::Int64, .has_default = false},
            Field{.name = "amount", .type = DataType::Int64, .has_default = false}, // Розширення типу
            Field{.name = "currency", .type = DataType::String, .has_default = true, .default_value = "EUR"}
        }
    };

    auto res_ok = SchemaCompatibilityEngine::check_backward(old_v1, new_v2_ok);
    if (res_ok) {
        std::cout << "✓ Валідація BACKWARD успішна для сумісної схеми V2.\n";
    }

    RecordSchema new_v3_bad{
        .record_name = "OrderPlaced",
        .fields = {
            Field{.name = "order_id", .type = DataType::Int64, .has_default = false},
            Field{.name = "amount", .type = DataType::Int32, .has_default = false},
            Field{.name = "fraud_score", .type = DataType::Int32, .has_default = false} // Обов'язкове поле без дефолту!
        }
    };

    auto res_bad = SchemaCompatibilityEngine::check_backward(old_v1, new_v3_bad);
    if (!res_bad) {
        std::cout << "✓ Перевірка перехопила порушення контракту:\n  " << res_bad.error() << "\n";
    }

    return 0;
}
