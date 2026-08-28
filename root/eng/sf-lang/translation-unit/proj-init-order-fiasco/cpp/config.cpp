// config.cpp
#include "config.hpp"
Config g_config;

// logger.cpp
#include "logger.hpp"
Logger g_logger;

// main.cpp
#include "logger.hpp"

int main() {
    g_logger.log("Application main() reached.");
    return 0;
}
