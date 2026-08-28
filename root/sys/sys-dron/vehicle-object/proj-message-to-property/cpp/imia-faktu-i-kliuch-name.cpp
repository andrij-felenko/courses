void FactGroup::_addFact(Fact *fact, const QString &name)
{
    if (_nameToFactMap.contains(name)) {
        qCWarning(FactGroupLog) << "Duplicate Fact" << name;
        return;
    }
    fact->setSendValueChangedSignals(_updateRateMSecs == 0);
    if (_nameToFactMetaDataMap.contains(name)) {
        fact->setMetaData(_nameToFactMetaDataMap[name], true);
    }
    _nameToFactMap[name] = fact;
    ...
