namespace std::filesystem {
    enum class file_type {
        none        = 0,
        not_found   = -1,
        regular     = 1,
        directory   = 2,
        symlink     = 3,
        block       = 4,
        character   = 5,
        fifo        = 6,
        socket      = 7,
        unknown     = 8
    };
}
