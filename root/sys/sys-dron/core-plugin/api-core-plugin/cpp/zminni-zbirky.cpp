// src/API/QGCCorePlugin.cc — після підстановки препроцесора
#ifdef QGC_CUSTOM_BUILD
#include CUSTOMHEADER
#endif

#ifndef QGC_CUSTOM_BUILD
Q_APPLICATION_STATIC(QGCCorePlugin, _qgcCorePluginInstance);
#endif

QGCCorePlugin *QGCCorePlugin::instance()
{
#ifndef QGC_CUSTOM_BUILD
    return _qgcCorePluginInstance();
#else
    return CUSTOMCLASS::instance();
#endif
}
