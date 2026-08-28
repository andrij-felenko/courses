enum class Status : int32_t {
    Success             =  0,
    NullPointer         = -1,
    InvalidVertex       = -2,
    OutOfMemory         = -3,
    NotEulerian         = -4,
    Disconnected        = -5,
    NoPathExists        = -6,
    EmptyGraph          = -7,
    FrozenGraph         = -8
};
