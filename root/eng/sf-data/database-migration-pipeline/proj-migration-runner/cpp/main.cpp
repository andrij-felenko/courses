#include <iostream>
#include <string>
#include <vector>
#include <filesystem>
#include <fstream>
#include <chrono>
#include <thread>
#include <format>
#include <stdexcept>
#include <libpq-fe.h>
#include <openssl/sha.h>

namespace fs = std::filesystem;

// RAII обгортка для з'єднання з PostgreSQL (libpq)
class PgConnection {
private:
    PGconn* conn_;

public:
    explicit PgConnection(const std::string& conninfo) {
        conn_ = PQconnectdb(conninfo.c_str());
        if (PQstatus(conn_) != CONNECTION_OK) {
            std::string err = PQerrorMessage(conn_);
            PQfinish(conn_);
            throw std::runtime_error("Помилка підключення до БД: " + err);
        }
    }

    ~PgConnection() {
        if (conn_) {
            PQfinish(conn_);
        }
    }

    PgConnection(const PgConnection&) = delete;
    PgConnection& operator=(const PgConnection&) = delete;

    PGconn* get() const noexcept { return conn_; }

    PGresult* exec(const std::string& sql) {
        PGresult* res = PQexec(conn_, sql.c_str());
        ExecStatusType status = PQresultStatus(res);
        if (status != PGRES_COMMAND_OK && status != PGRES_TUPLES_OK) {
            std::string err = PQerrorMessage(conn_);
            PQclear(res);
            throw std::runtime_error("Помилка виконання SQL: " + err);
        }
        return res;
    }
};

// RAII обгортка для автоматичного звільнення пам'яті PGresult
struct PgResultDeleter {
    void operator()(PGresult* res) const {
        if (res) PQclear(res);
    }
};
using PgResultPtr = std::unique_ptr<PGresult, PgResultDeleter>;

class CppMigrationRunner {
private:
    std::string conninfo_;
    int64_t lock_id_;

    static std::string calculate_sha256(const std::string& content) {
        unsigned char hash[SHA256_DIGEST_LENGTH];
        SHA256(reinterpret_cast<const unsigned char*>(content.data()), content.size(), hash);
        
        std::string hex_str;
        hex_str.reserve(SHA256_DIGEST_LENGTH * 2);
        for (int i = 0; i < SHA256_DIGEST_LENGTH; ++i) {
            hex_str += std::format("{:02x}", hash[i]);
        }
        return hex_str;
    }

public:
    CppMigrationRunner(std::string conninfo, int64_t lock_id)
        : conninfo_(std::move(conninfo)), lock_id_(lock_id) {}

    void acquire_advisory_lock(PgConnection& conn, std::chrono::seconds timeout) {
        auto deadline = std::chrono::steady_clock::now() + timeout;
        std::string query = std::format("SELECT pg_try_advisory_lock({});", lock_id_);

        while (true) {
            PgResultPtr res(conn.exec(query));
            if (PQntuples(res.get()) > 0 && std::string(PQgetvalue(res.get(), 0, 0)) == "t") {
                std::cout << std::format("[Lock] Advisory lock {} захоплено\n", lock_id_);
                return;
            }

            if (std::chrono::steady_clock::now() > deadline) {
                throw std::runtime_error("Таймаут захоплення advisory lock у C++ раннері");
            }

            std::cout << "[Lock] Очікування замка, повтор через 500мс...\n";
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
        }
    }

    void release_advisory_lock(PgConnection& conn) {
        std::string query = std::format("SELECT pg_advisory_unlock({});", lock_id_);
        try {
            PgResultPtr res(conn.exec(query));
            std::cout << std::format("[Lock] Advisory lock {} звільнено\n", lock_id_);
        } catch (const std::exception& ex) {
            std::cerr << "[Lock] Помилка зняття замка: " << ex.what() << "\n";
        }
    }

    void apply_migration_file(PgConnection& conn, const fs::path& filepath) {
        std::ifstream file(filepath);
        if (!file.is_open()) {
            throw std::runtime_error("Не вдалося відкрити файл: " + filepath.string());
        }

        std::string sql_content((std::istreambuf_iterator<char>(file)),
                                 std::istreambuf_iterator<char>());
        std::string checksum = calculate_sha256(sql_content);

        // Встановлюємо lock_timeout та statement_timeout
        conn.exec("SET lock_timeout = '2000ms'; SET statement_timeout = '30000ms';");

        // Транзакційне виконання
        PgResultPtr b_res(conn.exec("BEGIN;"));
        try {
            PgResultPtr m_res(conn.exec(sql_content));
            
            std::string record_sql = std::format(
                "INSERT INTO schema_migrations (version, name, checksum, execution_time_ms) "
                "VALUES ('{}', '{}', '{}', 100);",
                filepath.stem().string(), filepath.filename().string(), checksum);
            
            PgResultPtr r_res(conn.exec(record_sql));
            PgResultPtr c_res(conn.exec("COMMIT;"));
            std::cout << std::format("[Migrate] Файл {} успішно застосовано\n", filepath.filename().string());
        } catch (...) {
            conn.exec("ROLLBACK;");
            throw;
        }
    }
};
