#include <jni.h>
#include <android/log.h>
#include <string.h>
#include <stdlib.h>

#define LOG_TAG "NativeEngine"
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)

JNIEXPORT jstring JNICALL
Java_com_example_app_NativeBridge_processPayload(
    JNIEnv *env,
    jobject thiz,
    jstring input_str)
{
    if (input_str == NULL) {
        LOGE("Отримано нульовий покажчик на рядок з Java");
        return NULL;
    }

    const char *native_chars = (*env)->GetStringUTFChars(env, input_str, NULL);
    if (native_chars == NULL) {
        LOGE("Помилка виділення пам'яті під UTF-8 рядок");
        return NULL;
    }

    size_t len = strlen(native_chars);
    LOGI("Обробка корисного навантаження довжиною %zu байтів", len);

    char *buffer = (char *)malloc(len + 32);
    if (buffer == NULL) {
        (*env)->ReleaseStringUTFChars(env, input_str, native_chars);
        LOGE("Не вдалося виділити буфер обробки");
        return NULL;
    }

    strcpy(buffer, "Android NDK Output: ");
    strcat(buffer, native_chars);

    jstring result = (*env)->NewStringUTF(env, buffer);

    free(buffer);
    (*env)->ReleaseStringUTFChars(env, input_str, native_chars);

    return result;
}
