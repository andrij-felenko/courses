# scripts/inject_custom_ld.py
import os

Import("env")

def inject_linker_script():
    project_dir = env.get("PROJECT_DIR")
    custom_ld = os.path.join(project_dir, "ldscripts", "stm32f401_dma_custom.ld")
    
    if os.path.exists(custom_ld):
        print(f"[PRE-BUILD] Застосування кастомного скрипта лінкера: {custom_ld}")
        # Перевизначення шляху до LD-скрипта в об'єкті SCons
        env.Replace(LDSCRIPT_PATH=custom_ld)
        # Додавання прапорця для виводу детальної мапи розподілу пам'яті
        env.Append(LINKFLAGS=["-Wl,--print-memory-usage"])
    else:
        print("[PRE-BUILD] Використовується стандартний скрипт лінкера з SDK.")

inject_linker_script()
