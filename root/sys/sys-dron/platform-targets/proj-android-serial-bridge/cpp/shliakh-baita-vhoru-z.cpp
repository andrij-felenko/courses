static void jniDeviceNewData(JNIEnv* env, jobject, jlong token, jbyteArray data)
{
    const jsize len = env->GetArrayLength(data);
    const jsize cappedLen = qMin<jsize>(len, static_cast<jsize>(MAX_READ_SIZE));

    QByteArray payload(cappedLen, Qt::Uninitialized);
    env->GetByteArrayRegion(data, 0, cappedLen, reinterpret_cast<jbyte*>(payload.data()));
    if (QJniEnvironment::checkAndClearExceptions(env)) {
        return;
    }

    QReadLocker locker(&s_ptrLock);
    QSerialPortPrivate* const p = s_tokenToPtr.value(token, nullptr);
    if (!p) {
        qCWarning(AndroidSerialLog) << "stale token, object already destroyed";
        return;
    }
    p->newDataArrived(payload.constData(), payload.size());
}
