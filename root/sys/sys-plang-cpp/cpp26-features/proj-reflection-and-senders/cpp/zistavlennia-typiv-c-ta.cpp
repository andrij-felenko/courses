// Функція часу компіляції для визначення SQL-типу
consteval std::string_view cpp_type_to_sql(std::meta::info type_info) {
    if (type_info == ^^int32_t || type_info == ^^int64_t || type_info == ^^uint32_t || type_info == ^^uint64_t) {
        return "INTEGER";
    } else if (type_info == ^^double || type_info == ^^float) {
        return "REAL";
    } else if (type_info == ^^std::string || type_info == ^^std::string_view) {
        return "TEXT";
    } else if (type_info == ^^bool) {
        return "BOOLEAN";
    } else {
        return "BLOB";
    }
}

// Генератор SQL-запиту створення таблиці під час компіляції
template <typename T>
consteval auto generate_create_table_sql(std::string_view table_name) {
    constexpr auto type_meta = ^^T;
    constexpr auto members = std::meta::nonstatic_data_members_of(type_meta);

    std::string sql = "CREATE TABLE IF NOT EXISTS ";
    sql += table_name;
    sql += " (";

    bool first = true;
    for (size_t i = 0; i < members.size(); ++i) {
        if (!first) sql += ", ";
        
        auto member = members[i];
        std::string_view col_name = std::meta::name_of(member);
        auto col_type_info = std::meta::type_of(member);
        std::string_view sql_type = cpp_type_to_sql(col_type_info);

        sql += col_name;
        sql += " ";
        sql += sql_type;

        // Автоматичне призначення первинного ключа для поля з іменем "id"
        if (col_name == "id") {
            sql += " PRIMARY KEY";
        } else {
            sql += " NOT NULL";
        }
        first = false;
    }

    sql += ");";
    return sql;
}

// Генератор SQL-запиту вставки запису
template <typename T>
consteval auto generate_insert_sql(std::string_view table_name) {
    constexpr auto type_meta = ^^T;
    constexpr auto members = std::meta::nonstatic_data_members_of(type_meta);

    std::string cols = "";
    std::string placeholders = "";

    bool first = true;
    for (size_t i = 0; i < members.size(); ++i) {
        if (!first) {
            cols += ", ";
            placeholders += ", ";
        }
        cols += std::meta::name_of(members[i]);
        placeholders += "?";
        first = false;
    }

    std::string sql = "INSERT INTO ";
    sql += table_name;
    sql += " (";
    sql += cols;
    sql += ") VALUES (";
    sql += placeholders;
    sql += ");";
    return sql;
}
