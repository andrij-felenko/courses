#include <array>

struct MixerRow {
    float roll;
    float pitch;
    float yaw;
    float throttle;
};

// Стандартна матриця мікшування Quad-X (Props In)
constexpr std::array<MixerRow, 4> mixerPropsIn{{
    { -1.0f,  +1.0f,  +1.0f,  +1.0f }, // Мотор 1 (RR, CCW)
    { -1.0f,  -1.0f,  -1.0f,  +1.0f }, // Мотор 2 (FR, CW)
    { +1.0f,  +1.0f,  -1.0f,  +1.0f }, // Мотор 3 (RL, CW)
    { +1.0f,  -1.0f,  +1.0f,  +1.0f }, // Мотор 4 (FL, CCW)
}};

// Реверсна матриця мікшування Quad-X (Props Out / Inverted Yaw)
constexpr std::array<MixerRow, 4> mixerPropsOut{{
    { -1.0f,  +1.0f,  -1.0f,  +1.0f }, // Мотор 1 (RR, CW)  <- Знак Yaw інвертовано!
    { -1.0f,  -1.0f,  +1.0f,  +1.0f }, // Мотор 2 (FR, CCW) <- Знак Yaw інвертовано!
    { +1.0f,  +1.0f,  +1.0f,  +1.0f }, // Мотор 3 (RL, CCW) <- Знак Yaw інвертовано!
    { +1.0f,  -1.0f,  -1.0f,  +1.0f }, // Мотор 4 (FL, CW)  <- Знак Yaw інвертовано!
}};
