#include <string>
#include <vector>

class QueryBuilder {
    std::string query_;
public:
    QueryBuilder& add_filter(std::string_view f) [[clang::lifetimebound]] {
        query_ += " WHERE " + std::string(f);
        return *this;
    }

    QueryBuilder& set_limit(int limit) [[clang::lifetimebound]] {
        query_ += " LIMIT " + std::to_string(limit);
        return *this;
    }

    std::string build() const {
        return query_;
    }
};

void run() {
    // Безпечно: виклик build() повертає значення std::string за значенням до кінця повного виразу
    std::string q = QueryBuilder{}.add_filter("active=1").set_limit(10).build();

    // Небезпечно: збереження посилання на проміжний тимчасовий Builder
    // Завдяки [[clang::lifetimebound]] компілятор видасть попередження
    QueryBuilder& builder_ref = QueryBuilder{}.add_filter("active=1"); // warning: temporary bound to reference
}
