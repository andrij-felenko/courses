// У C++ безпечна перевірка стану зони здійснюється через enum class
enum class ZoneCondition : std::uint8_t {
    Empty      = BLK_ZONE_COND_EMPTY,
    ImpOpen    = BLK_ZONE_COND_IMP_OPEN,
    ExpOpen    = BLK_ZONE_COND_EXP_OPEN,
    Closed     = BLK_ZONE_COND_CLOSED,
    Full       = BLK_ZONE_COND_FULL,
    ReadOnly   = BLK_ZONE_COND_READONLY,
    Offline    = BLK_ZONE_COND_OFFLINE
};
