// Наскрізна затримка цифрового відеолінка, мілісекунди
int t_capture = 12;   // сенсор → кадр у пам'яті
int t_codec   = 10;   // стиск H.264 одного кадру
int t_channel = 8;    // пакетизація + радіо/мережа (саме повітря ~ 0)
int t_buffer  = 20;   // буфер проти джитера — нерівність приходу пакетів

int glass_to_glass = t_capture + t_codec + t_channel + t_buffer;
// = 12 + 10 + 8 + 20 = 50 мс

// Якби втрачений пакет тягли по TCP: + один круговий обіг (RTT)
int rtt = 60;
int with_tcp_resend = glass_to_glass + rtt;   // = 110 мс
