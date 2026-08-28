enum LinkType {
#ifndef QGC_NO_SERIAL_LINK
    TypeSerial,     // 0 у звичайній збірці — і взагалі відсутній у збірці без серійного каналу
#endif
    TypeUdp, TypeTcp, TypeBluetooth,
#ifdef QT_DEBUG
    TypeMock,       // існує лише у зневаджувальній збірці
#endif
    TypeLogReplay,
    TypeLast
};
