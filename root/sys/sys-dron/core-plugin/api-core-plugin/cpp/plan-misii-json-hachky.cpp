virtual void preSaveToJson         (PlanMasterController *pController, QJsonObject &json)        { }
virtual void preSaveToMissionJson  (PlanMasterController *pController, QJsonObject &missionJson) { }
virtual void postSaveToMissionJson (PlanMasterController *pController, QJsonObject &missionJson) { }
virtual void postSaveToJson        (PlanMasterController *pController, QJsonObject &json)        { }
virtual void preLoadFromJson       (PlanMasterController *pController, QJsonObject &json)        { }
virtual void postLoadFromJson      (PlanMasterController *pController, QJsonObject &json)        { }

virtual QVariantList complexMissionItemNames(Vehicle *vehicle);
virtual ComplexMissionItem *createComplexMissionItem(const QString &complexItemType,
                                                     PlanMasterController *masterController,
                                                     bool flyView,
                                                     const QString &kmlOrShpFile = QString());
virtual QList<PlanCreator *> planCreators(PlanMasterController *planMasterController);
