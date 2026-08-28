#include "SettingsManager.h"
#include "PayloadSettings.h"

void PayloadPlanner::start()
{
    PayloadSettings *payload = SettingsManager::instance()->payloadSettings();

    const double interval = payload->triggerInterval()->rawValue().toDouble();
    const uint32_t profile = payload->payloadProfile()->rawValue().toUInt();

    if (payload->autoStart()->rawValue().toBool()) {
        _beginCapture(profile, interval);
    }

    connect(payload->triggerInterval(), &Fact::rawValueChanged,
            this, [this](const QVariant &value) {
        _retimeCapture(value.toDouble());
    });
}

void PayloadPlanner::setDumpDirectory(const QString &path)
{
    // запис на диск відбувається тут-таки, окремої дії «зберегти» немає
    SettingsManager::instance()->payloadSettings()->dumpDirectory()->setRawValue(path);
}
