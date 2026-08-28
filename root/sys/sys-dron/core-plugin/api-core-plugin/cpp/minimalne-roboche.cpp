// CustomPlugin.cc
Q_APPLICATION_STATIC(CustomPlugin, _customPluginInstance);

QGCCorePlugin *CustomPlugin::instance() { return _customPluginInstance(); }

CustomPlugin::CustomPlugin(QObject *parent)
    : QGCCorePlugin(parent)
    , _options(new CustomOptions(this, this))
{
    _showAdvancedUI = false;     // без цього рядка збірка лишиться «розширеною»
    (void) connect(this, &QGCCorePlugin::showAdvancedUIChanged,
                   this, &CustomPlugin::_advancedChanged);
}
