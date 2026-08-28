// SokilFirmwarePluginInstanceData.h
class SokilFirmwarePluginInstanceData : public FirmwarePluginInstanceData
{
    Q_OBJECT
public:
    explicit SokilFirmwarePluginInstanceData(QObject *parent = nullptr)
        : FirmwarePluginInstanceData(parent) {}

    QTime lastStreamRequestTime;    // коли востаннє просили частоти
    uint32_t firmwareBuild = 0;     // збірка, що приїхала в AUTOPILOT_VERSION
};
