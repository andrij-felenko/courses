// storage_adapter.hpp — Ідіоматичний C++20 портативний інтерфейс сховища
#pragma once

#include <memory>
#include <string_view>
#include <span>
#include <vector>
#include <expected>
#include <system_error>
#include <filesystem>
#include <fstream>
#include <iostream>

enum class StorageError {
    NotFound,
    AccessDenied,
    NetworkFailure,
    IoError,
    InvalidArgument
};

// Абстрактний інтерфейс сховища об'єктів (Порт)
class StorageAdapter {
public:
    virtual ~StorageAdapter() = default;

    [[nodiscard]] virtual std::expected<void, StorageError> 
    write_object(std::string_view key, std::span<const std::byte> data) noexcept = 0;

    [[nodiscard]] virtual std::expected<std::vector<std::byte>, StorageError> 
    read_object(std::string_view key) noexcept = 0;

    [[nodiscard]] virtual std::expected<void, StorageError> 
    delete_object(std::string_view key) noexcept = 0;
};

// Адаптер для локальної POSIX файлової системи (Fallback / Local Dev)
class PosixStorageAdapter final : public StorageAdapter {
public:
    explicit PosixStorageAdapter(std::filesystem::path base_path)
        : base_path_(std::move(base_path)) {}

    std::expected<void, StorageError> 
    write_object(std::string_view key, std::span<const std::byte> data) noexcept override {
        try {
            auto full_path = base_path_ / key;
            std::filesystem::create_directories(full_path.parent_path());

            std::ofstream file(full_path, std::ios::binary | std::ios::trunc);
            if (!file) return std::unexpected(StorageError::IoError);

            file.write(reinterpret_cast<const char*>(data.data()), static_cast<std::streamsize>(data.size()));
            file.flush();
            return {};
        } catch (...) {
            return std::unexpected(StorageError::IoError);
        }
    }

    std::expected<std::vector<std::byte>, StorageError> 
    read_object(std::string_view key) noexcept override {
        try {
            auto full_path = base_path_ / key;
            if (!std::filesystem::exists(full_path)) {
                return std::unexpected(StorageError::NotFound);
            }

            std::ifstream file(full_path, std::ios::binary | std::ios::ate);
            if (!file) return std::unexpected(StorageError::IoError);

            auto size = file.tellg();
            file.seekg(0, std::ios::beg);

            std::vector<std::byte> buffer(static_cast<size_t>(size));
            file.read(reinterpret_cast<char*>(buffer.data()), size);
            return buffer;
        } catch (...) {
            return std::unexpected(StorageError::IoError);
        }
    }

    std::expected<void, StorageError> 
    delete_object(std::string_view key) noexcept override {
        try {
            auto full_path = base_path_ / key;
            if (std::filesystem::remove(full_path)) return {};
            return std::unexpected(StorageError::NotFound);
        } catch (...) {
            return std::unexpected(StorageError::IoError);
        }
    }

private:
    std::filesystem::path base_path_;
};
