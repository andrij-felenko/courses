import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render, fitbox, textbox, line, arrow, text, rect, POS, NEG, FIELD, INK, MUTED, FILL, LINE

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)

def draw_nested_arch():
    w, h = 820, 440
    frags = []
    
    # L2 Layer
    frags.append(fitbox(50, 50, 720, 75, 
                        "L2: Вкладена віртуальна машина (Nested Guest)\n"
                        "Виконується у VMX Non-Root режимі (апаратний стан VMCS02)", 
                        size=14, fill="#e8f4f8", stroke="#2980b9", bold=True))
    
    # Arrow L2 -> L1
    frags.append(arrow(410, 125, 410, 160, color=LINE, sw=2))
    frags.append(text(420, 147, "Переривання / Trap в L1 або L0", size=12, color=MUTED, anchor="start"))
    
    # L1 Layer
    frags.append(fitbox(50, 160, 720, 105, 
                        "L1: Гостьовий гіпервізор (Guest Hypervisor — KVM / Xen / Hyper-V)\n"
                        "Думає, що керує VMX/SVM у VMX Root. Насправді працює у VMX Non-Root L0\n"
                        "Утримує VMCS12 для L2 та керує власною таблицею EPT12", 
                        size=14, fill="#fef9e7", stroke="#f39c12", bold=True))
    
    # Arrow L1 -> L0
    frags.append(arrow(410, 265, 410, 300, color=LINE, sw=2))
    frags.append(text(420, 287, "VM Exit у L0 (апаратний вихід)", size=12, color=POS, anchor="start", bold=True))
    
    # L0 Layer
    frags.append(fitbox(50, 300, 720, 105, 
                        "L0: Фізичний хостовий гіпервізор (Host KVM) + CPU (VT-x / AMD-V)\n"
                        "Працює у VMX Root. Фізично завантажує VMCS02 (злиття VMCS01 + VMCS12)\n"
                        "Будує Тіньовий EPT02 (EPT01 + EPT12) та обробляє фізичні переривання", 
                        size=14, fill="#eafaf1", stroke=FIELD, bold=True))
    
    path = os.path.join(IMG_DIR, "nested-arch.svg")
    render(path, w, h, *frags, title="Архітектура трирівневої віртуалізації (L0, L1, L2)")

def draw_vmcs_shadowing():
    w, h = 840, 420
    frags = []
    
    # Left Box: Without Shadowing
    frags.append(rect(40, 55, 360, 335, fill="#fdfefe", stroke="#bdc3c7", sw=1.5))
    frags.append(text(220, 80, "Без VMCS Shadowing", size=15, color=POS, bold=True))
    
    frags.append(fitbox(60, 105, 320, 50, "L1 виконує VMREAD / VMWRITE\nдо VMCS12", size=13, fill=FILL))
    frags.append(arrow(220, 155, 220, 195, color=POS, sw=2))
    frags.append(text(225, 180, "Кожен виклик = VM Exit!", size=12, color=POS, bold=True, anchor="start"))
    
    frags.append(fitbox(60, 195, 320, 55, "L0 (Host KVM) перехоплює trap,\nпрограмно емулює читання/запис", size=13, fill="#fdecea", stroke=POS))
    frags.append(arrow(220, 250, 220, 290, color=LINE, sw=1.5))
    
    frags.append(fitbox(60, 290, 320, 75, "Результат: сотні VM Exits\nна один цикл запуску L2\n(Колосальні накладні витрати)", size=13, fill="#fdf2e9", stroke="#e67e22"))
    
    # Right Box: With Shadowing
    frags.append(rect(440, 55, 360, 335, fill="#fdfefe", stroke="#bdc3c7", sw=1.5))
    frags.append(text(620, 80, "З VMCS Shadowing (Intel Haswell+)", size=15, color=FIELD, bold=True))
    
    frags.append(fitbox(460, 105, 320, 50, "L1 виконує VMREAD / VMWRITE\nдо VMCS12", size=13, fill=FILL))
    frags.append(arrow(620, 155, 620, 195, color=FIELD, sw=2))
    frags.append(text(625, 180, "Без VM Exit (HW direct)", size=12, color=FIELD, bold=True, anchor="start"))
    
    frags.append(fitbox(460, 195, 320, 55, "Процесор оновлює Shadow VMCS\nпрямо в пам'яті за VMCS Pointer", size=13, fill="#eafaf1", stroke=FIELD))
    frags.append(arrow(620, 250, 620, 290, color=LINE, sw=1.5))
    
    frags.append(fitbox(460, 290, 320, 75, "VM Exit викликається ЛИШЕ на\nVMLAUNCH / VMRESUME\n(Синхронізація VMCS02 в L0)", size=13, fill="#e8f8f5", stroke="#16a085"))
    
    path = os.path.join(IMG_DIR, "vmcs-shadowing.svg")
    render(path, w, h, *frags, title="Оптимізація VMCS Shadowing: скорочення трапів у L0")

def draw_ept_routing():
    w, h = 840, 460
    frags = []
    
    # Translation path
    frags.append(fitbox(40, 50, 160, 60, "L2 GVA\n(Віртуальна L2)", size=13, fill="#ebf5fb", stroke="#3498db"))
    frags.append(arrow(200, 80, 240, 80, color=LINE, sw=2))
    frags.append(text(220, 70, "Page Tables", size=11, color=MUTED))
    
    frags.append(fitbox(240, 50, 160, 60, "L2 GPA\n(Фізична L2)", size=13, fill="#ebf5fb", stroke="#3498db"))
    frags.append(arrow(400, 80, 440, 80, color=LINE, sw=2))
    frags.append(text(420, 70, "EPT12 (L1)", size=11, color="#f39c12", bold=True))
    
    frags.append(fitbox(440, 50, 160, 60, "L1 GPA\n(Фізична L1)", size=13, fill="#fef9e7", stroke="#f39c12"))
    frags.append(arrow(600, 80, 640, 80, color=LINE, sw=2))
    frags.append(text(620, 70, "EPT01 (L0)", size=11, color=FIELD, bold=True))
    
    frags.append(fitbox(640, 50, 160, 60, "L0 HPA\n(Дійсна DRAM)", size=13, fill="#eafaf1", stroke=FIELD, bold=True))
    
    # Shadow EPT box
    frags.append(fitbox(180, 150, 480, 65, 
                        "Злиття в L0: Тіньовий EPT (EPT02 = EPT12 + EPT01)\n"
                        "Апаратне забезпечення MMU використовує єдиний EPTP02 для трансляції L2 GPA -> L0 HPA", 
                        size=13, fill="#f4f6f7", stroke="#7f8c8d", bold=True))
    
    # EPT Violation Decision Tree
    frags.append(arrow(420, 215, 420, 255, color=POS, sw=2))
    frags.append(text(430, 240, "Порушення EPT (EPT Violation) під час виконання L2", size=12, color=POS, bold=True, anchor="start"))
    
    frags.append(fitbox(220, 255, 400, 45, "Апаратний VM Exit до L0 (Host KVM)", size=14, fill="#fdecea", stroke=POS, bold=True))
    
    # Split paths
    frags.append(arrow(320, 300, 200, 345, color=LINE, sw=1.8))
    frags.append(arrow(520, 300, 640, 345, color=LINE, sw=1.8))
    
    frags.append(fitbox(40, 345, 320, 95, 
                        "Сценарій А: Помилка у мапінгу EPT01\n"
                        "(Хостовий swap / розширення пам'яті L1)\n"
                        "L0 виправляє мапінг, оновлює EPT02,\n"
                        "повертає управління L2 (L1 не залучається)", 
                        size=12, fill="#eafaf1", stroke=FIELD))
    
    frags.append(fitbox(480, 345, 320, 95, 
                        "Сценарій Б: Помилка у мапінгу EPT12\n"
                        "(Пам'ять не виділена у L1 для L2)\n"
                        "L0 впорскує синтетичний EPT Exit у L1.\n"
                        "L1 обробляє помилку та робить VMRESUME", 
                        size=12, fill="#fef9e7", stroke="#f39c12"))
    
    path = os.path.join(IMG_DIR, "ept-routing.svg")
    render(path, w, h, *frags, title="Маршрутизація EPT Violations та злиття EPT02 у KVM")

if __name__ == '__main__':
    draw_nested_arch()
    draw_vmcs_shadowing()
    draw_ept_routing()
    print("All figures generated successfully.")
