def build_ota_package(target, source, env):
    bin_file = env.subst("$BUILD_DIR/${PROGNAME}.bin")
    ota_output = os.path.join(env.get("PROJECT_DIR"), "releases", "firmware_ota.bin")
    os.makedirs(os.path.dirname(ota_output), exist_ok=True)
    
    print(f"[CUSTOM TARGET] Пакування OTA-образу: {bin_file} -> {ota_output}")
    # Тут можна виконати виклик утиліт шифрування AES або підпису криптографічним ключем RSA/ECDSA

env.AddCustomTarget(
    name="package_ota",
    dependencies=["$BUILD_DIR/${PROGNAME}.bin"],
    actions=[build_ota_package],
    title="Генерація підписаного OTA-пакета",
    description="Створює зашифрований образ прошивки для бездротового оновлення"
)
