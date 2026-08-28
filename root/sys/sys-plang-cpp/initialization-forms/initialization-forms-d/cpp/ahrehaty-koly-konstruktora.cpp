struct Config {
    int  port      = 8080;
    int  backlog   = 128;
    bool reuseAddr = false;
};

Config c1{};                                    // 8080, 128, false
Config c2{9000};                                // 9000, 128, false
Config c3{9000, 512, true};                     // усе задано
Config c4{.port = 9000, .reuseAddr = true};     // C++20: за іменами
