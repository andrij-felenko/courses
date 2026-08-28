const MethodDef defs[] = {
    {&s_methods.availableDevicesInfo, "availableDevicesInfo", "()[Ljava/lang/String;"},
    {&s_methods.open,                 "open",                 "(Ljava/lang/String;J)I"},
    {&s_methods.close,                "close",                "(I)Z"},
    {&s_methods.read,                 "read",                 "(III)[B"},
    {&s_methods.write,                "write",                "(I[BII)I"},
    {&s_methods.writeAsync,           "writeAsync",           "(I[BI)I"},
    {&s_methods.setParameters,        "setParameters",        "(IIIII)Z"},
    // …ще півтора десятка: лінії керування, потік, буфери
};

for (const auto& def : defs) {
    *def.target = env->GetStaticMethodID(javaClass, def.name, def.sig);
    if (!*def.target) {
        qCWarning(AndroidSerialLog) << "Failed to cache method:" << def.name << def.sig;
        (void)QJniEnvironment::checkAndClearExceptions(env);
        return false;
    }
}
