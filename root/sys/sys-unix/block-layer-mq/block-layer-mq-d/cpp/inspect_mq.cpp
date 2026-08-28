// inspect_mq.cpp — Зчитування конфігурації blk-mq на C++20
#include <iostream>
#include <fstream>
#include <string>
#include <filesystem>
#include <format>

namespace fs = std::filesystem;

void print_mq_attribute(const std::string& dev, const std::string& attr) {
    fs::path sysfs_path = fs::path("/sys/block") / dev / "mq" / attr;
    if (!fs::exists(sysfs_path)) {
        sysfs_path = fs::path("/sys/block") / dev / "queue" / attr;
    }

    if (fs::exists(sysfs_path)) {
        std::ifstream file(sysfs_path);
        std::string value;
        if (std::getline(file, value)) {
            std::cout << std::format("  {:20s}: {}\n", attr, value);
            return;
        }
    }
    std::cout << std::format("  {:20s}: [недоступно]\n", attr);
}

int main(int argc, char* argv[]) {
    std::string dev_name = (argc > 1) ? argv[1] : "nvme0n1";
    std::cout << std::format("Інспектування blk-mq для пристрою /dev/{}:\n", dev_name);

    print_mq_attribute(dev_name, "nr_hw_queues");
    print_mq_attribute(dev_name, "scheduler");
    print_mq_attribute(dev_name, "nr_requests");
    print_mq_attribute(dev_name, "io_poll");

    return 0;
}
