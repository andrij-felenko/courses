import os
import sys

# Add scripts/ to sys.path (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render as svg_render, rect, text, mtext, line, arrow, FILL, INK, LINE, MUTED, POS, NEG, FIELD

def render_expansion_flow(img_dir):
    w, h = 760, 560
    frags = []
    
    frags.append(text(w / 2, 25, "Послідовність етапів розгортання рядка в командній оболонці", size=15, bold=True))
    
    # Input box
    frags.append(rect(180, 50, 400, 45, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(380, 68, "Сирий текстовий рядок від користувача", size=12, color="#92400e", bold=True))
    frags.append(text(380, 85, 'echo ~user/${VAR:-dir}/$(date +%Y)/*.txt', size=11, color="#78350f"))
    
    frags.append(arrow(380, 95, 380, 115, color=MUTED, sw=2))
    
    # Step 1: Brace Expansion
    frags.append(rect(130, 115, 500, 50, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    frags.append(text(380, 134, "1. Brace Expansion (Фігурні дужки)", size=12, color="#075985", bold=True))
    frags.append(text(380, 153, "Розгортання списків {a,b} та діапазонів {1..5} (Bash/Zsh розширення до POSIX)", size=10, color="#0c4a6e"))
    
    frags.append(arrow(380, 165, 380, 185, color=MUTED, sw=2))
    
    # Step 2: Tilde Expansion
    frags.append(rect(130, 185, 500, 50, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    frags.append(text(380, 204, "2. Tilde Expansion (Тильда)", size=12, color="#075985", bold=True))
    frags.append(text(380, 223, "~ розгортається у $HOME (/home/user), ~+ у $PWD, ~- у $OLDPWD", size=10, color="#0c4a6e"))
    
    frags.append(arrow(380, 235, 380, 255, color=MUTED, sw=2))
    
    # Step 3: Parameter, Cmd & Arithmetic
    frags.append(rect(130, 255, 500, 55, fill="#dcfce7", stroke="#16a34a", sw=1.5))
    frags.append(text(380, 274, "3. Parameter, Command & Arithmetic Expansion", size=12, color="#166534", bold=True))
    frags.append(text(380, 293, "Підстановка $VAR, $(cmd), $((expr)) зліва направо в один прохід", size=10, color="#14532d"))
    
    frags.append(arrow(380, 310, 380, 330, color=MUTED, sw=2))
    
    # Step 4: Word Splitting
    frags.append(rect(130, 330, 500, 55, fill="#f3e8ff", stroke="#9333ea", sw=1.5))
    frags.append(text(380, 349, "4. Word Splitting (Поділ на слова)", size=12, color="#6b21a8", bold=True))
    frags.append(text(380, 368, "Розбиття незахищених подвійними лапками підстановок за роздільниками IFS", size=10, color="#581c87"))
    
    frags.append(arrow(380, 385, 380, 405, color=MUTED, sw=2))
    
    # Step 5: Filename Expansion
    frags.append(rect(130, 405, 500, 50, fill="#ffe4e6", stroke="#e11d48", sw=1.5))
    frags.append(text(380, 424, "5. Filename Expansion / Globbing", size=12, color="#9f1239", bold=True))
    frags.append(text(380, 443, "Заміна масок *, ?, [...] на список реальних імен файлів з VFS", size=10, color="#881337"))
    
    frags.append(arrow(380, 455, 380, 475, color=MUTED, sw=2))
    
    # Step 6: Quote Removal & Output
    frags.append(rect(130, 475, 500, 50, fill="#f3f4f6", stroke="#4b5563", sw=1.5))
    frags.append(text(380, 494, "6. Quote Removal (Видалення лапок) ──► Сформований argv[]", size=12, color="#1f2937", bold=True))
    frags.append(text(380, 513, "Видалення не закерованих ', \", \\ та виклики execve(path, argv, envp)", size=10, color="#374151"))
    
    os.makedirs(img_dir, exist_ok=True)
    path = os.path.join(img_dir, "expansion-flow.svg")
    svg_render(path, w, h, *frags)

if __name__ == '__main__':
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    render_expansion_flow(img_dir)
