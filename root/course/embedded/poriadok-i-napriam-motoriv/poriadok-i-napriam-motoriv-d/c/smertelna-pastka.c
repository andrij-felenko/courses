// Стандартна матриця мікшування Quad-X (Props In)
static const motorMixer_t mixerPropsIn[4] = {
    //  Roll   Pitch    Yaw   Throttle
    { -1.0f,  +1.0f,  +1.0f,  +1.0f }, // Мотор 1 (RR, CCW)
    { -1.0f,  -1.0f,  -1.0f,  +1.0f }, // Мотор 2 (FR, CW)
    { +1.0f,  +1.0f,  -1.0f,  +1.0f }, // Мотор 3 (RL, CW)
    { +1.0f,  -1.0f,  +1.0f,  +1.0f }, // Мотор 4 (FL, CCW)
};

// Реверсна матриця мікшування Quad-X (Props Out / Inverted Yaw)
static const motorMixer_t mixerPropsOut[4] = {
    //  Roll   Pitch    Yaw   Throttle
    { -1.0f,  +1.0f,  -1.0f,  +1.0f }, // Мотор 1 (RR, CW)  <- Знак Yaw інвертовано!
    { -1.0f,  -1.0f,  +1.0f,  +1.0f }, // Мотор 2 (FR, CCW) <- Знак Yaw інвертовано!
    { +1.0f,  +1.0f,  +1.0f,  +1.0f }, // Мотор 3 (RL, CCW) <- Знак Yaw інвертовано!
    { +1.0f,  -1.0f,  -1.0f,  +1.0f }, // Мотор 4 (FL, CW)  <- Знак Yaw інвертовано!
};
