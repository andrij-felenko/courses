void SimpleMissionItem::save(QJsonArray& missionItems)
{
    QList<MissionItem*> items;

    appendMissionItems(items, this);      // основний запис + камера + швидкість

    for (int i = 0; i < items.count(); i++) {
        MissionItem* item = items[i];
        QJsonObject saveObject;
        item->save(saveObject);
        if (i == 0) {
            // це головний елемент — тільки йому дописуємо дані про висоту
        }
        missionItems.append(saveObject);
        item->deleteLater();
    }
}
