// LinkTypes.h — усе, що бачать обидві нитки
#pragma once

#include <QByteArray>
#include <QMetaType>
#include <atomic>
#include <chrono>
#include <memory>

// Монотонний час у наносекундах. steady_clock у C++ — один на весь процес
// і ніколи не йде назад, тож мітку, поставлену в одній нитці,
// можна законно відняти в іншій.
inline qint64 monoNs()
{
    using namespace std::chrono;
    return duration_cast<nanoseconds>(steady_clock::now().time_since_epoch()).count();
}

// Пачка байтів разом із міткою миті, коли її прочитали з сокета.
struct Chunk {
    QByteArray bytes;
    qint64     stampNs = 0;
};
Q_DECLARE_METATYPE(Chunk)
