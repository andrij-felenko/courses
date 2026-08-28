int write(int deviceId, const char* data, int length, int timeout, bool async)
{
    JniContext ctx;                     // всередині — QJniEnvironment, тобто приєднання
    if (!getContext(ctx, "write")) {
        return -1;
    }

    AndroidInterface::JniLocalRef<jbyteArray> jarray(
        ctx.env.jniEnv(), ctx.env->NewByteArray(static_cast<jsize>(length)));
    ctx.env->SetByteArrayRegion(jarray.get(), 0, static_cast<jsize>(length),
                                reinterpret_cast<const jbyte*>(data));
    if (ctx.env.checkAndClearExceptions()) {
        return -1;
    }

    jint result;
    if (async) {
        result = ctx.env->CallStaticIntMethod(ctx.cls, s_methods.writeAsync,
                                              static_cast<jint>(deviceId), jarray.get(),
                                              static_cast<jint>(timeout));
    } else {
        result = ctx.env->CallStaticIntMethod(ctx.cls, s_methods.write,
                                              static_cast<jint>(deviceId), jarray.get(),
                                              static_cast<jint>(length), static_cast<jint>(timeout));
    }
    if (ctx.env.checkAndClearExceptions()) {
        return -1;
    }
    return static_cast<int>(result);
}
