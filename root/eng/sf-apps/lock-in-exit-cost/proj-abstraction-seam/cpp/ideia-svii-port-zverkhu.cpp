#include <string>
#include <vector>
#include <optional>

// Свій порт: рівно потреба системи, у власних поняттях.
// Жодного типу постачальника тут немає — саме тому це шов, а не
// переодягнений SDK.
class ObjectStore {
public:
    virtual ~ObjectStore() = default;

    // Покласти байти під ключем. Кидає StoreError при збої (див. нижче).
    virtual void put(const std::string& key,
                     const std::string& bytes) = 0;

    // Дістати байти. std::nullopt означає «такого ключа немає»
    // (це НЕ помилка); StoreError — саме збій доступу.
    virtual std::optional<std::string> get(const std::string& key) = 0;

    // Перелічити ключі, що починаються з префікса.
    virtual std::vector<std::string> list(const std::string& prefix) = 0;
};
