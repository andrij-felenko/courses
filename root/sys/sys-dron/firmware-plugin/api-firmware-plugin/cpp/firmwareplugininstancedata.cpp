class FirmwarePluginInstanceData : public QObject
{
    Q_OBJECT
public:
    using QObject::QObject;

    enum class CommandSupportedResult : uint8_t {
        SUPPORTED   = 23,
        UNSUPPORTED = 24,
        UNKNOWN     = 25,
    };

    /// true, якщо будь-яка версія прошивки колись підтримувала cmd —
    /// щоб не витрачати зайвий обмін із автопілотом на розвідку
    virtual CommandSupportedResult anyVersionSupportsCommand(MAV_CMD /*cmd*/) const
        { return CommandSupportedResult::UNKNOWN; }

    void setCommandSupported(MAV_CMD cmd, CommandSupportedResult status)
        { MAV_CMD_supported[cmd] = status; }
    CommandSupportedResult getCommandSupported(MAV_CMD cmd) const;

private:
    QMap<MAV_CMD, CommandSupportedResult> MAV_CMD_supported;
};
