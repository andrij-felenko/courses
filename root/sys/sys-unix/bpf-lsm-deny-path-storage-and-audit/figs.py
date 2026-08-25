import sys
import os

# Insert path to scripts directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
from svgkit import (
    textbox, rect, text, mtext, line, arrow, render,
    FILL, LINE, INK, MUTED, POS, NEG, FIELD, BG
)

def draw_hooks_flow():
    frags = []
    
    # Syscall Entry
    b1, w1, h1 = textbox(140, 60, "Системний виклик\n(open, execve, socket)", size=12, pad=10, fill="#eef2ff", stroke="#3b82f6", bold=True)
    frags.append(b1)
    
    # DAC Check
    b2, w2, h2 = textbox(410, 60, "Перевірка DAC\n(UID/GID, chmod, ACL)", size=12, pad=10, fill="#f8fafc", stroke=LINE, bold=True)
    frags.append(b2)
    
    # LSM Hook Entry
    b3, w3, h3 = textbox(680, 60, "LSM Hook Chain\n(security_file_open)", size=12, pad=10, fill="#fef3c7", stroke="#d97706", bold=True)
    frags.append(b3)
    
    # Top level flow arrows
    frags.append(arrow(140 + w1/2, 60, 410 - w2/2, 60))
    frags.append(arrow(410 + w2/2, 60, 680 - w3/2, 60))
    
    # Down Arrow to BPF LSM
    frags.append(arrow(680, 60 + h3/2, 680, 160))
    
    # BPF LSM Execution Container
    b_bpf, w_bpf, h_bpf = textbox(680, 210, "BPF LSM Program\nSEC(\"lsm/file_open\")\n- Перевірка контексту BTF\n- Аналіз стану локального сховища", size=12, pad=12, fill="#ecfdf5", stroke="#10b981", bold=True)
    frags.append(b_bpf)
    
    # Audit Buffer (right)
    b_audit, w_audit, h_audit = textbox(920, 210, "BPF Ring Buffer\n(Запис аудиту в Userspace)", size=11, pad=10, fill="#f3e8ff", stroke="#9333ea", bold=True)
    frags.append(b_audit)
    frags.append(arrow(680 + w_bpf/2, 210, 920 - w_audit/2, 210))
    
    # Path down for decision
    frags.append(line(680, 210 + h_bpf/2, 680, 310))
    
    # Branch 1: Deny (-EACCES)
    frags.append(arrow(680, 310, 830, 310))
    b_deny, w_deny, h_deny = textbox(950, 310, "Відмова (Return -EACCES)\nНегайне переривання виклику\nта повернення EACCES", size=11, pad=10, fill="#fef2f2", stroke="#dc2626", bold=True)
    frags.append(b_deny)
    
    # Branch 2: Allow (Return 0)
    frags.append(arrow(680, 310, 500, 310))
    b_allow, w_allow, h_allow = textbox(360, 310, "Дозвіл (Return 0)\nНаступні LSM у ланцюжку", size=11, pad=10, fill="#ecfdf5", stroke="#059669", bold=True)
    frags.append(b_allow)
    
    # Final VFS execution
    frags.append(arrow(360 - w_allow/2, 310, 180, 310))
    b_exec, w_exec, h_exec = textbox(100, 310, "Операція VFS\n(відкриття ресурсу)", size=11, pad=10, fill="#f0fdf4", stroke="#16a34a", bold=True)
    frags.append(b_exec)
    
    return frags

def draw_storage_override():
    frags = []
    
    # Kernel Object (inode / task_struct)
    b_obj, w_obj, h_obj = textbox(160, 140, "Об'єкт ядра Linux\n(struct inode / task_struct)\n\n+-----------------------+\n| void *security        |\n+-----------------------+", size=11, pad=12, fill="#f8fafc", stroke=LINE, bold=True)
    frags.append(b_obj)
    
    # LSM Security Blob
    b_blob, w_blob, h_blob = textbox(450, 140, "LSM Security Blob\n(Пам'ять за security_blob_sizes)\n\n- SELinux context blob\n- BPF Local Storage Pointer", size=11, pad=12, fill="#fef3c7", stroke="#d97706", bold=True)
    frags.append(b_blob)
    frags.append(arrow(160 + w_obj/2, 140, 450 - w_blob/2, 140))
    
    # BPF Local Storage Table
    b_bpf_st, w_bpf_st, h_bpf_st = textbox(770, 140, "BPF Local Storage Map\n(bpf_inode_storage / task_storage)\n\n- policy_flags: 0x01 (Restricted)\n- access_counter: 42\n- owner_tgid: 1042", size=11, pad=12, fill="#ecfdf5", stroke="#10b981", bold=True)
    frags.append(b_bpf_st)
    frags.append(arrow(450 + w_blob/2, 140, 770 - w_bpf_st/2, 140))
    
    # Bottom section: BPF LSM hook decision engine
    b_hook, w_hook, h_hook = textbox(450, 310, "BPF LSM Hook (bpf_inode_storage_get)\nЗчитування мітки з локального сховища об'єкта\nПорівняння PID/UID з поточним task_struct", size=11, pad=12, fill="#eef2ff", stroke="#3b82f6", bold=True)
    frags.append(b_hook)
    
    frags.append(arrow(770, 140 + h_bpf_st/2, 450 + w_hook/2, 310))
    
    # Override result outputs
    b_out1, w_out1, h_out1 = textbox(160, 310, "Результат: -EPERM\n(Override / Блокування)", size=11, pad=10, fill="#fef2f2", stroke="#dc2626", bold=True)
    frags.append(b_out1)
    frags.append(arrow(450 - w_hook/2, 310, 160 + w_out1/2, 310))
    
    b_out2, w_out2, h_out2 = textbox(770, 310, "Результат: 0 (Pass)\n+ bpf_ringbuf_output()", size=11, pad=10, fill="#f3e8ff", stroke="#9333ea", bold=True)
    frags.append(b_out2)
    frags.append(arrow(450 + w_hook/2, 310, 770 - w_out2/2, 310))
    
    return frags

def main():
    img_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
    os.makedirs(img_dir, exist_ok=True)
    
    # Render hooks flow
    render(os.path.join(img_dir, 'bpf-lsm-hooks-flow.svg'), 1100, 400, *draw_hooks_flow())
    
    # Render storage override
    render(os.path.join(img_dir, 'bpf-lsm-storage-override.svg'), 1000, 420, *draw_storage_override())
    print("Successfully generated figures in img/")

if __name__ == '__main__':
    main()
