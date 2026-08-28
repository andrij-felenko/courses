#include <iostream>
#include <string>
#include <span>
#include <vector>

struct JsonPayload { std::string json_text; };
struct BinaryPayload { std::vector<uint8_t> raw_bytes; };
struct TextPayload { std::string plain_text; };

struct JsonHandler {
    void handle_message(const JsonPayload& p) {
        std::cout << "Обробка JSON: " << p.json_text << '\n';
    }
};

struct BinaryHandler {
    void handle_message(const BinaryPayload& p) {
        std::cout << "Обробка Binary: " << p.raw_bytes.size() << " байтів\n";
    }
};

struct TextHandler {
    void handle_message(const TextPayload& p) {
        std::cout << "Обробка PlainText: " << p.plain_text << '\n';
    }
};

// Конвеєр об'єднує всі обробники в єдиний ієрархічний диспетчер:
template <typename... Handlers>
struct MessagePipeline : Handlers... {
    using Handlers::handle_message...; // C++17 варіативне using-оголошення!
};

int main() {
    MessagePipeline<JsonHandler, BinaryHandler, TextHandler> pipeline;

    pipeline.handle_message(JsonPayload{"{\"user_id\": 42}"});
    pipeline.handle_message(BinaryPayload{{0x01, 0x02, 0x03}});
    pipeline.handle_message(TextPayload{"Звичайне повідомлення журналу"});

    return 0;
}
