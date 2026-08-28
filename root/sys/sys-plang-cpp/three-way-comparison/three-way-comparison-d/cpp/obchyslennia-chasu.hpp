struct Version {
    int major;
    int minor;
    int patch;

    friend constexpr auto operator<=>(Version, Version) = default;
};

// Перевірка інваріантів під час компіляції
static_assert(Version{2, 0, 0} > Version{1, 9, 99});
static_assert(Version{2, 1, 0} <=> Version{2, 1, 0} == 0);
