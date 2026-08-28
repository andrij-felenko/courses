struct pidfd_info {
    std::uint64_t mask;      // Маска запитаних та заповнених полів
    std::uint64_t cgroupid;  // 64-бітний унікальний ID cgroup v2
    std::uint32_t pid;       // PID процесу у просторі імен викликача
    std::uint32_t tgid;      // TGID (ID групи потоків / лідер процесу)
    std::uint32_t ppid;      // PPID (PID батьківського процесу)
    std::uint32_t ruid;      // Реальний UID
    std::uint32_t rgid;      // Реальний GID
    std::uint32_t euid;      // Ефективний UID процесу
    std::uint32_t egid;      // Ефективний GID процесу
    std::uint32_t suid;      // Збережений UID
    std::uint32_t sgid;      // Збережений GID
    std::uint32_t fsuid;     // UID для доступу до файлів
    std::uint32_t fsgid;     // GID для доступу до файлів
    std::int32_t  exit_code; // Код завершення (біт PIDFD_INFO_EXIT, Linux 6.13+)
};
