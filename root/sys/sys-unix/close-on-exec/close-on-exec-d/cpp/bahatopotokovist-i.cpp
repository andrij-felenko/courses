pid_t pid = ::fork();
if (pid == 0) {
    std::array<char*, 5> args = { 
        const_cast<char*>("logger"), 
        const_cast<char*>("-t"), 
        const_cast<char*>("backup"), 
        const_cast<char*>("OK"), 
        nullptr 
    };
    ::execve("/usr/bin/logger", args.data(), nullptr);
}
