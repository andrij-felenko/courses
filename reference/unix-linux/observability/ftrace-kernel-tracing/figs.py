import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def render_dynamic_ftrace(path):
    frags = []
    
    # Title is passed to render()
    
    # 4 horizontal boxes / stages
    # Stage 1: Compiling
    b1 = fitbox(40, 60, 160, 90, "1. Компіляція\n-mfentry\nЗапис у __mcount_loc\ncall __fentry__", fill="#e8f4f8", stroke="#2b7b98")
    frags.append(b1)
    
    # Stage 2: Boot init
    b2 = fitbox(240, 60, 160, 90, "2. Раннє завантаження\nftrace_init()\nЗаміна CALL -> NOP\n(5-байтовий NOP)", fill="#f9f2e7", stroke="#d98c21")
    frags.append(b2)
    
    # Stage 3: Disabled tracing
    b3 = fitbox(440, 60, 160, 90, "3. Пасивний стан\nТрасування ВИМКНЕНО\nВиконується NOP\n(0% оверхеду)", fill="#eef7e9", stroke="#4b9932")
    frags.append(b3)
    
    # Stage 4: Active tracing
    b4 = fitbox(640, 60, 160, 90, "4. Активація\ntext_poke_bp()\nЗаміна NOP -> CALL\ncall ftrace_caller", fill="#fceaea", stroke="#c9302c")
    frags.append(b4)
    
    # Arrows connecting stages
    frags.append(arrow(200, 105, 240, 105))
    frags.append(arrow(400, 105, 440, 105))
    frags.append(arrow(600, 105, 640, 105))
    
    # Annotations below
    frags.append(fitbox(40, 180, 360, 60, "Захист від викривлення продуктивності:\nУсі точки трасування NOP-нуті до запиту користувача", fill="#f4f6f8", stroke="#888888", size=12))
    frags.append(fitbox(440, 180, 360, 60, "Атомарний патчинг коду:\nВикористання int3 breakpoint для запобігання race condition", fill="#f4f6f8", stroke="#888888", size=12))
    
    render(path, 840, 270, *frags, title="Механізм Dynamic Ftrace: етапи патчингу машинного коду")

def render_tracefs(path):
    frags = []
    
    # User level
    u1 = fitbox(40, 60, 220, 80, "Юзерпростір\ntrace-cmd / cat / echo\nKernelShark / bpftrace", fill="#e8f4f8", stroke="#2b7b98")
    frags.append(u1)
    
    # VFS / tracefs interface
    v1 = fitbox(310, 60, 220, 80, "Інтерфейс VFS\n/sys/kernel/tracing/\ncurrent_tracer, trace_pipe", fill="#f9f2e7", stroke="#d98c21")
    frags.append(v1)
    
    # Kernel ring buffer
    k1 = fitbox(580, 60, 220, 80, "Кільцевий буфер ядра\nPer-CPU Ring Buffers\nLockless pages (commit/reader)", fill="#eef7e9", stroke="#4b9932")
    frags.append(k1)
    
    frags.append(arrow(260, 100, 310, 100))
    frags.append(arrow(530, 100, 580, 100))
    
    # Sub-files details
    files_box = fitbox(40, 170, 760, 90, "Ключові файли керування vfs tracefs:\n• current_tracer: вибір плагіна (function, function_graph, hwlat, nop)\n• tracing_on: глобальний вимикач запису подій (1 / 0)\n• set_ftrace_filter / set_ftrace_notrace: білий та чорний списки функцій\n• trace_pipe: потоковий бінарний/текстовий вивід у реальному часі", fill="#ffffff", stroke="#cccccc", size=12)
    frags.append(files_box)
    
    render(path, 840, 290, *frags, title="Інтерфейс tracefs та підсистема кільцевих буферів ftrace")

def render_function_graph_stack(path):
    frags = []
    
    # Box 1: Entry
    b1 = fitbox(40, 60, 230, 110, "1. Вхід у функцію\nftrace_caller перехоплює виклик\nftrace_push_return_trace()\nЗбереження orig_ret + ts\nу тіньовому стеку task_struct", fill="#e8f4f8", stroke="#2b7b98")
    frags.append(b1)
    
    # Box 2: Return address rewrite
    b2 = fitbox(305, 60, 230, 110, "2. Підміна стеку\nАдреса повернення на стеку\nперезаписується на\nreturn_to_handler", fill="#f9f2e7", stroke="#d98c21")
    frags.append(b2)
    
    # Box 3: Exit & Restore
    b3 = fitbox(570, 60, 230, 110, "3. Вихід з функції\nІнструкція RET повертає в\nreturn_to_handler\nЗапис тривалості в буфер\nВідновлення orig_ret", fill="#eef7e9", stroke="#4b9932")
    frags.append(b3)
    
    frags.append(arrow(270, 115, 305, 115))
    frags.append(arrow(535, 115, 570, 115))
    
    render(path, 840, 200, *frags, title="Механізм function_graph: підміна адреси повернення на стеку")

def build_svgs():
    render_dynamic_ftrace(os.path.join(IMG, "dynamic-ftrace.svg"))
    render_tracefs(os.path.join(IMG, "tracefs.svg"))
    render_function_graph_stack(os.path.join(IMG, "function-graph-stack.svg"))
    print("ftrace SVG figures generated successfully in img/.")

if __name__ == "__main__":
    build_svgs()
