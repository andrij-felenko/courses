from dataclasses import dataclass

View = str  # 'functional'|'information'|'concurrency'|'development'|'deployment'|'operational'

# Прояв елемента в ОДНІЙ в'ю. Ключ унікальний, напр. "deployment:svc-order".
@dataclass(frozen=True)
class Manifestation:
    id: str
    view: View
    label: str

# Відповідність (ISO 42010): «це той самий логічний елемент у двох в'ю». Ненапрямлена.
@dataclass(frozen=True)
class Correspondence:
    a: str
    b: str

# Деталь розгортання: де живе прояв і які вузли з'єднані мережею.
@dataclass
class Deployment:
    hosts: dict[str, list[str]]           # id прояву-розгортання → вузли (>1 = репліки)
    links: list[tuple[str, str]]          # мережеві зв'язки між вузлами

# Деталь функційної в'ю: виклик між двома елементами, оголошений local|remote.
@dataclass(frozen=True)
class Call:
    frm: str
    to: str
    kind: str    # 'local' | 'remote'

# Увесь опис як дані.
@dataclass
class Description:
    manifestations: list[Manifestation]
    correspondences: list[Correspondence]
    deployment: Deployment
    calls: list[Call]
    required_views: list[View]           # в'ю, у які МУСИТЬ дотягнутися кожен елемент
