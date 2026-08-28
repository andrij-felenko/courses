from dataclasses import dataclass
from typing import Dict, List, Set, Optional

@dataclass(frozen=True)
class Tuple:
    object_id: str   # Наприклад, "camera:704"
    relation: str    # Наприклад, "viewer"
    subject_id: str  # Наприклад, "user:alice" або "home:101#owner"

@dataclass
class EvalContext:
    current_time_hour: int
    allowed_start_hour: int = 8
    allowed_end_hour: int = 22

class RebacAbacEngine:
    def __init__(self):
        # Сховище кортежів: object_id -> список кортежів стосунків
        self._tuples: Dict[str, List[Tuple]] = {}

    def add_tuple(self, obj: str, relation: str, subject: str) -> None:
        t = Tuple(object_id=obj, relation=relation, subject_id=subject)
        self._tuples.setdefault(obj, []).append(t)

    def check_rebac(self, subject: str, relation: str, obj: str, visited: Optional[Set[str]] = None) -> bool:
        """Рекурсивний обхід графа стосунків з відстеженням відвіданих вузлів."""
        if visited is None:
            visited = set()
        
        state_key = f"{obj}#{relation}@{subject}"
        if state_key in visited:
            return False  # Запобігання циклам у реляційному графі
        visited.add(state_key)

        tuples = self._tuples.get(obj, [])
        for t in tuples:
            if t.relation != relation:
                continue
            
            # 1. Прямий збіг ідентифікатора суб'єкта
            if t.subject_id == subject:
                return True
            
            # 2. Непрямий зв'язок через Userset Rewrite (наприклад, home:101#owner)
            if "#" in t.subject_id:
                parent_obj, parent_rel = t.subject_id.split("#")
                if self.check_rebac(subject, parent_rel, parent_obj, visited):
                    return True
        
        return False

    def evaluate(self, subject: str, action: str, obj: str, ctx: EvalContext) -> bool:
        # Фаза 1: ReBAC перевірка зв'язку у графі
        if not self.check_rebac(subject, action, obj):
            return False
        
        # Фаза 2: ABAC перевірка часового вікна
        if not (ctx.allowed_start_hour <= ctx.current_time_hour <= ctx.allowed_end_hour):
            return False  # Доступ заборонено за часом
        
        return True

# --- Демонстраційний прогон ---
if __name__ == "__main__":
    engine = RebacAbacEngine()
    
    # 1. Аліса є власником будинку 101
    engine.add_tuple("home:101", "owner", "user:alice")
    # 2. Камера 704 належить будинку 101
    engine.add_tuple("camera:704", "parent", "home:101")
    # 3. Переглядачем камери є власник її батьківського будинку
    engine.add_tuple("camera:704", "viewer", "home:101#owner")

    # Перевірка о 14:00 (у дозволений час)
    ctx_day = EvalContext(current_time_hour=14)
    print("День 14:00 ->", engine.evaluate("user:alice", "viewer", "camera:704", ctx_day))  # True

    # Перевірка о 23:00 (поза вікном)
    ctx_night = EvalContext(current_time_hour=23)
    print("Ніч 23:00 ->", engine.evaluate("user:alice", "viewer", "camera:704", ctx_night))  # False
