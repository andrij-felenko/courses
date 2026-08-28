class FirmwarePluginInstanceData : public QObject
{
public:
    enum class CommandSupportedResult : uint8_t { SUPPORTED = 23, UNSUPPORTED = 24, UNKNOWN = 25 };

    void setCommandSupported(MAV_CMD cmd, CommandSupportedResult status)
        { MAV_CMD_supported[cmd] = status; }
    CommandSupportedResult getCommandSupported(MAV_CMD cmd) const;
private:
    QMap<MAV_CMD, CommandSupportedResult> MAV_CMD_supported;
};
