class CustomOptions : public QGCOptions
{
public:
    explicit CustomOptions(CustomPlugin *plugin, QObject *parent = nullptr);

    // Прошивку оновлює лише той, хто свідомо ввімкнув розширений режим
    bool showFirmwareUpgrade() const final { return _plugin->showAdvancedUI(); }

    QGCFlyViewOptions *flyViewOptions() final { return _flyViewOptions; }

private:
    CustomPlugin *_plugin = nullptr;
    CustomFlyViewOptions *_flyViewOptions = nullptr;
};
