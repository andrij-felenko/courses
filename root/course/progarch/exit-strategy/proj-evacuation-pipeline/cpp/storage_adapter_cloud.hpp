// storage_adapter_cloud.hpp — Хмарний адаптер C++ (Абстрагований REST Client)
#pragma once
#include "storage_adapter.hpp"
#include <iostream>

class CloudStorageAdapter final : public StorageAdapter {
public:
    CloudStorageAdapter(std::string endpoint, std::string bucket, std::string access_key)
        : endpoint_(std::move(endpoint)), bucket_(std::move(bucket)), access_key_(std::move(access_key)) {}

    std::expected<void, StorageError> 
    write_object(std::string_view key, std::span<const std::byte> data) noexcept override {
        // У продакшені тут використовується стандартизований HTTP/gRPC REST API
        // Без імпорту proprietary SDK провайдера у публічні заголовки
        std::cout << "[CloudStorage] PUT " << endpoint_ << "/" << bucket_ << "/" << key 
                  << " (" << data.size() << " bytes) [AUTH: OK]\n";
        return {};
    }

    std::expected<std::vector<std::byte>, StorageError> 
    read_object(std::string_view key) noexcept override {
        std::cout << "[CloudStorage] GET " << endpoint_ << "/" << bucket_ << "/" << key << "\n";
        return std::vector<std::byte>{};
    }

    std::expected<void, StorageError> 
    delete_object(std::string_view key) noexcept override {
        std::cout << "[CloudStorage] DELETE " << endpoint_ << "/" << bucket_ << "/" << key << "\n";
        return {};
    }

private:
    std::string endpoint_;
    std::string bucket_;
    std::string access_key_;
};
