void LinkManager::_linkDisconnected()
{
    LinkInterface *const link = qobject_cast<LinkInterface*>(sender());
    if (!link) { return; }

    SharedLinkInterfacePtr linkToCleanup;
    {
        QMutexLocker locker(&_linksMutex);
        for (auto it = _rgLinks.begin(); it != _rgLinks.end(); ++it) {
            if (it->get() == link) {
                linkToCleanup = *it;      // ⚠️ забрати копію ПЕРЕД видаленням зі списку
                _rgLinks.erase(it);
                break;
            }
        }
    }
    if (!linkToCleanup) { return; }       // уже прибрано — це не помилка

    // ... відв'язати опис, відписатися від сигналів
    link->_freeMavlinkChannel();
}
