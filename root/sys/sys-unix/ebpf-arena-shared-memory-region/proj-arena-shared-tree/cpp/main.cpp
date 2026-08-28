#include <iostream>
#include <memory>
#include <stdexcept>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <sys/mman.h>
#include <arpa/inet.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include "shared_tree.h"

class BpfArenaManager {
private:
    int map_fd_{-1};
    void* arena_base_{MAP_FAILED};
    size_t size_bytes_{0};

public:
    explicit BpfArenaManager(size_t page_count) : size_bytes_(page_count * 4096) {
        map_fd_ = bpf_map_create(BPF_MAP_TYPE_ARENA, "arena_map", 0, 0, static_cast<__u32>(page_count), nullptr);
        if (map_fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "bpf_map_create failed");
        }

        arena_base_ = mmap(nullptr, size_bytes_, PROT_READ | PROT_WRITE, MAP_SHARED, map_fd_, 0);
        if (arena_base_ == MAP_FAILED) {
            close(map_fd_);
            throw std::system_error(errno, std::generic_category(), "mmap failed");
        }
    }

    ~BpfArenaManager() {
        if (arena_base_ != MAP_FAILED) {
            munmap(arena_base_, size_bytes_);
        }
        if (map_fd_ >= 0) {
            close(map_fd_);
        }
    }

    BpfArenaManager(const BpfArenaManager&) = delete;
    BpfArenaManager& operator=(const BpfArenaManager&) = delete;

    [[nodiscard]] void* get_base() const noexcept { return arena_base_; }
    [[nodiscard]] int get_fd() const noexcept { return map_fd_; }
};

int main()
{
    try {
        BpfArenaManager arena(1024);
        std::cout << "[+] BPF Arena mmap success: " << arena.get_base() << std::endl;

        auto* hdr = static_cast<struct arena_root_header*>(arena.get_base());
        hdr->magic = ARENA_MAGIC;
        hdr->version = 1;
        hdr->total_lookups = 0;
        hdr->total_matches = 0;

        auto* root_node = reinterpret_cast<struct radix_node*>(
            static_cast<char*>(arena.get_base()) + sizeof(struct arena_root_header)
        );
        std::memset(root_node, 0, sizeof(struct radix_node));
        root_node->prefix = 0;
        root_node->prefix_len = 0;
        root_node->action = 0;

        auto* drop_node = root_node + 1;
        std::memset(drop_node, 0, sizeof(struct radix_node));
        drop_node->prefix = 0x0A000000;
        drop_node->prefix_len = 8;
        drop_node->action = 1;

        root_node->child[0] = drop_node;
        hdr->root = drop_node;

        std::cout << "[+] Radix Tree initialized in shared BPF Arena. Root=" << drop_node << std::endl;
        std::cout << "[+] Press Enter to terminate loader..." << std::endl;
        std::cin.get();

    } catch (const std::exception& ex) {
        std::cerr << "[-] Error: " << ex.what() << std::endl;
        return 1;
    }

    return 0;
}
