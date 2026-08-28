// custom/src/CustomFirmwarePlugin.h
class CustomFirmwarePlugin : public PX4FirmwarePlugin
{
    Q_OBJECT
public:
    explicit CustomFirmwarePlugin(QObject *parent = nullptr);

    QMap<QString, FactGroup*> *factGroups() final { return &_factGroups; }

private:
    FuelCellFactGroup         _fuelCellFactGroup;
    QMap<QString, FactGroup*> _factGroups;
};

// custom/src/CustomFirmwarePlugin.cc
CustomFirmwarePlugin::CustomFirmwarePlugin(QObject *parent)
    : PX4FirmwarePlugin(parent)
    , _fuelCellFactGroup(this)
{
    _factGroups.insert(QStringLiteral("fuelcell"), &_fuelCellFactGroup);
}
