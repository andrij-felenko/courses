// читання й перетворення
Q_INVOKABLE QString  validate(const QString &cookedValue, bool convertOnly);
Q_INVOKABLE QVariant clamp(const QString &cookedValue);
Q_INVOKABLE QVariant rawToCooked(const QVariant &rawValue) const;
QString              rawValueStringFullPrecision() const;

// запис
void setRawValue(const QVariant &value);        // від логіки застосунку
void setCookedValue(const QVariant &value);     // від людини, у показаних одиницях
void containerSetRawValue(const QVariant &value); // від апарата
void forceSetRawValue(const QVariant &value);   // повз перевірку «те саме значення»
void setEnumIndex(int index);
void setEnumStringValue(const QString &value);

// опис
void          setMetaData(FactMetaData *metaData, bool setDefaultFromMetaData = false);
FactMetaData *metaData();
void          setEnumInfo(const QStringList &strings, const QVariantList &values);

// темп сповіщень
void setSendValueChangedSignals(bool sendValueChangedSignals);
bool deferredValueChangeSignal() const;
void sendDeferredValueChangedSignal();
void clearDeferredValueChangeSignal();
