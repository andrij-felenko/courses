android {
    defaultConfig {
        ndk {
            abiFilters.addAll(listOf("arm64-v8a", "armeabi-v7a", "x86_64"))
        }
        externalNativeBuild {
            cmake {
                arguments(
                    "-DANDROID_STL=c++_shared",
                    "-DANDROID_ARM_NEON=ON",
                    "-DANDROID_ARM_MODE=thumb",
                    "-DANDROID_ALLOW_UNDEFINED_SYMBOLS=OFF"
                )
                cFlags("-O3", "-fvisibility=hidden")
                cppFlags("-std=c++20", "-fexceptions", "-frtti")
            }
        }
    }
    externalNativeBuild {
        cmake {
            path = file("src/main/cpp/CMakeLists.txt")
            version = "3.22.1"
        }
    }
}
