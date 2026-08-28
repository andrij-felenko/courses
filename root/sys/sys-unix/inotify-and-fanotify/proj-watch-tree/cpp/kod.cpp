#define _GNU_SOURCE
#include <sys/inotify.h>
#include <sys/epoll.h>
#include <sys/stat.h>
#include <dirent.h>
#include <fcntl.h>
#include <limits.h>
#include <unistd.h>

#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <memory>
#include <chrono>
#include <cstdint>
#include <cstring>

constexpr size_t NBUCKET = (1u << 16);
constexpr int MAXDEPTH = 256;
constexpr int MOVE_SLOTS = 64;
constexpr int TODO_MAX = 4096;
constexpr int MOVE_TIMEOUT_MS = 200;

static const std::uint32_t WATCH_MASK =
      IN_CREATE | IN_DELETE | IN_MOVED_FROM | IN_MOVED_TO | IN_CLOSE_WRITE
    | IN_DELETE_SELF | IN_MOVE_SELF
    | IN_ONLYDIR | IN_DONT_FOLLOW | IN_EXCL_UNLINK;

struct Node {
    int wd{-1};
    int parent{-1};
    std::string name;
    Node* child{nullptr};
    Node* sib{nullptr};
};

struct Context {
    int ifd{-1};
    int ep{-1};
    std::string root;
    std::vector<char> buf;
    bool rebuild{false};
};
