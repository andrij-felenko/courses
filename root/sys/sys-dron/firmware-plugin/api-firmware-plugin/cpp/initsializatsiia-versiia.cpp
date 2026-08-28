ParameterMetaData *loadParameterMetaData(const Vehicle *vehicle);   // НЕ віртуальний — готовий збирач
void cacheParameterMetaDataFile(const QString &metaDataFile);

protected:
    virtual ParameterMetaData *_createParameterMetaData() { return nullptr; }
    virtual QString _internalParameterMetaDataFile(const Vehicle*) const { return QString(); }
    QString         _cachedParameterMetaDataFile(const Vehicle *vehicle) const;
    virtual QString _getLatestVersionFileUrl(Vehicle*) const { return QString(); }
    virtual QString _versionRegex() const { return QString(); }
    virtual void    _versionFileDownloadFinished(const QString &remoteFile, const QString &localFile,
                                                 const Vehicle *vehicle) const;
    virtual MAV_AUTOPILOT _autopilotType() const { return MAV_AUTOPILOT_GENERIC; }
