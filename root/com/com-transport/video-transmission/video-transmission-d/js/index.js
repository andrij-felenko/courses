// Наскрізна затримка цифрового відеолінка, мілісекунди
const tCapture = 12;   // сенсор → кадр у пам'яті
const tCodec   = 10;   // стиск H.264 одного кадру
const tChannel = 8;    // пакетизація + радіо/мережа (саме повітря ~ 0)
const tBuffer  = 20;   // буфер проти джитера — нерівність приходу пакетів

const glassToGlass = tCapture + tCodec + tChannel + tBuffer;
// = 12 + 10 + 8 + 20 = 50 мс

// Якби втрачений пакет тягли по TCP: + один круговий обіг (RTT)
const rtt = 60;
const withTcpResend = glassToGlass + rtt;   // = 110 мс
