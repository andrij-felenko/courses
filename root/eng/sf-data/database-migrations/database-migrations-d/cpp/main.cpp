#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

struct ColumnSchema {
    std::string name;
    std::string type;
    bool is_nullable;
};

bool validate_schema_compatibility(const std::vector<ColumnSchema>& schema, const std::string& required_col) {
    auto it = std::find_if(schema.begin(), schema.end(), [&](const ColumnSchema& col) {
        return col.name == required_col;
    });
    if (it != schema.end()) {
        std::cout << "Колонка " << required_col << " знайдена в схемі.\n";
        return true;
    }
    std::cerr << "Помилка несумісності: колонка " << required_col << " відсутня!\n";
    return false;
}
