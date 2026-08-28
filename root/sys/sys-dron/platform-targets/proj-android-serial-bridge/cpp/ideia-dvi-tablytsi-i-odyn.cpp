static QReadWriteLock s_ptrLock;
static QHash<jlong, QSerialPortPrivate*> s_tokenToPtr;
static QHash<QSerialPortPrivate*, jlong> s_ptrToToken;

void registerPointer(QSerialPortPrivate* ptr)
{
    QWriteLocker locker(&s_ptrLock);

    jlong token;
    do {
        token = static_cast<jlong>(QRandomGenerator::global()->generate64());
    } while (token == 0 || s_tokenToPtr.contains(token));

    s_tokenToPtr.insert(token, ptr);
    s_ptrToToken.insert(ptr, token);
}
