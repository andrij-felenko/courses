namespace std::filesystem {
    enum class perms : std::uint32_t {
        none         = 0,
        
        owner_read   = 0400, owner_write  = 0200, owner_exec   = 0100, owner_all   = 0700,
        group_read   = 0040, group_write  = 0020, group_exec   = 0010, group_all   = 0070,
        others_read  = 0004, others_write = 0002, others_exec  = 0001, others_all  = 0007,
        
        all          = 0777,
        
        set_uid      = 04000,
        set_gid      = 02000,
        sticky_bit   = 01000,
        mask         = 07777,
        unknown      = 0xFFFF
    };
}
