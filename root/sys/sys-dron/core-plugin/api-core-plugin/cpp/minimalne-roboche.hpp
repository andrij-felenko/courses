// CustomPlugin.h
class CustomFlyViewOptions : public QGCFlyViewOptions
{
    Q_OBJECT
public:
    explicit CustomFlyViewOptions(CustomOptions *options, QObject *parent = nullptr);
protected:
    bool showInstrumentPanel() const final { return false; }
    bool showMultiVehicleList() const final { return false; }
};

class CustomOptions : public QGCOptions
{
    Q_OBJECT
public:
    explicit CustomOptions(CustomPlugin *plugin, QObject *parent = nullptr);
    // прапорець дивиться на стан, а не на константу
    bool showFirmwareUpgrade() const final { return _plugin->showAdvancedUI(); }
    const QGCFlyViewOptions *flyViewOptions() const final { return _flyViewOptions; }
private:
    CustomPlugin        *_plugin        = nullptr;
    CustomFlyViewOptions *_flyViewOptions = nullptr;
};

class CustomPlugin : public QGCCorePlugin
{
    Q_OBJECT
public:
    explicit CustomPlugin(QObject *parent = nullptr);
    static QGCCorePlugin *instance();          // обов'язково: саме це кличе CUSTOMCLASS::instance()
    QGCOptions *options() final { return _options; }
private:
    CustomOptions *_options = nullptr;
};
