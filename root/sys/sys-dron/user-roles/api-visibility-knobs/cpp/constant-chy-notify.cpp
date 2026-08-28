class CustomOptions : public QGCOptions
{
    Q_OBJECT

public:
    explicit CustomOptions(CustomPlugin *plugin, QObject *parent = nullptr);

    // showFirmwareUpgrade оголошено з NOTIFY — його МОЖНА в'язати до стану
    bool showFirmwareUpgrade() const final { return _plugin->showAdvancedUI(); }

private:
    QGCCorePlugin *_plugin = nullptr;
};

CustomPlugin::CustomPlugin(QObject *parent)
    : QGCCorePlugin(parent)
    , _options(new CustomOptions(this, this))
{
    _showAdvancedUI = false;   // збірка стартує БЕЗ поглибленого шару
    (void) connect(this, &QGCCorePlugin::showAdvancedUIChanged,
                   this, &CustomPlugin::_advancedChanged);
}

void CustomPlugin::_advancedChanged(bool changed)
{
    // базовий QGCOptions цього не зробить за тебе
    emit _options->showFirmwareUpgradeChanged(changed);
}
