// database.cpp
#include "logger.hpp"

class DatabaseConnection {
public:
    DatabaseConnection() {
        // Припустимо, DatabaseConnection сконструювався ПЕРШИМ
    }

    ~DatabaseConnection() {
        // Деструктор намагається записати підсумок у журнал
        g_logger.log("DatabaseConnection: скидання транзакцій і закриття з'єднання.");
    }
};

DatabaseConnection g_db_conn;
