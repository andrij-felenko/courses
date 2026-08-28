SharedLinkInterfacePtr LinkManager::sharedLinkInterfacePointerForLink(const LinkInterface *link)
{
    QMutexLocker locker(&_linksMutex);
    for (const SharedLinkInterfacePtr &sharedLink : _rgLinks) {
        if (sharedLink.get() == link) {
            return sharedLink;
        }
    }
    return SharedLinkInterfacePtr(nullptr);   // уже від'єднане — це нормально
}
