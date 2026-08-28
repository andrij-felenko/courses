#include "PayloadSettings.h"

DECLARE_SETTINGGROUP(Payload, "PayloadPlanner")
{
    // тіло конструктора: сюди йде лише те, чого не описати в JSON —
    // наприклад, перелік, що залежить від наявного обладнання
}

DECLARE_SETTINGSFACT(PayloadSettings, triggerInterval)
DECLARE_SETTINGSFACT(PayloadSettings, autoStart)
DECLARE_SETTINGSFACT(PayloadSettings, dumpDirectory)

DECLARE_SETTINGSFACT_NO_FUNC(PayloadSettings, payloadProfile)
{
    if (!_payloadProfileFact) {
        _payloadProfileFact = _createSettingsFact(payloadProfileName);
        connect(_payloadProfileFact, &Fact::rawValueChanged,
                this, &PayloadSettings::_profileChanged);
    }
    return _payloadProfileFact;
}
