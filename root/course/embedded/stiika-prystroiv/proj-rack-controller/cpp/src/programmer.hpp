// Налагоджувач слота: запуск OpenOCD як дочірнього процесу.
#pragma once

#include <chrono>
#include <filesystem>
#include <span>
#include <string>

class Programmer {
public:
    explicit Programmer(int slotId) noexcept : slotId_{slotId} {}

    // Прошити образ, звірити й пустити плату. Плата має бути під живленням.
    void program(const std::filesystem::path& image);

    // Повне стирання кристала: викликається, коли плата вже стартувала
    // з фабричного ROM-завантажувача (BOOT0 = 1).
    void massErase();

private:
    void runOpenocd(std::span<const std::string> commands, std::chrono::seconds timeout);
    bool tryOpenocd(std::span<const std::string> commands, std::chrono::seconds timeout);

    int slotId_;
};
