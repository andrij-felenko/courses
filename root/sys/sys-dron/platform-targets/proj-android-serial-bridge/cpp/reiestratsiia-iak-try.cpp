void AndroidSerial::setNativeMethods()
{
    const JNINativeMethod javaMethods[]{
        {"nativeDeviceHasDisconnected", "(J)V",  reinterpret_cast<void*>(jniDeviceHasDisconnected)},
        {"nativeDeviceNewData",         "(J[B)V", reinterpret_cast<void*>(jniDeviceNewData)},
        {"nativeDeviceException",       "(JLjava/lang/String;)V",
                                                  reinterpret_cast<void*>(jniDeviceException)},
    };

    QJniEnvironment env;
    if (!env.registerNativeMethods(kJniUsbSerialManagerClassName,
                                   javaMethods, std::size(javaMethods))) {
        qCWarning(AndroidSerialLog) << "Failed to register native methods";
        return;
    }

    if (!getSerialManagerClass()) {          // тут-таки кешують клас і всі jmethodID
        qCWarning(AndroidSerialLog) << "Failed to cache JNI method IDs";
        return;
    }
}
