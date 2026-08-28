struct UidGidExtent {
    uid_t first_ns;
    uid_t first_host;
    uid_t count;
};

struct UidGidMap {
    std::uint32_t nr_extents;
    std::variant<
        std::array<UidGidExtent, 5>,
        std::pair<std::vector<UidGidExtent>, std::vector<UidGidExtent>>
    > extents;
};
