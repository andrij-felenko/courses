// В'ю, у яких елемент може проявитися.
type View =
  | 'functional' | 'information' | 'concurrency'
  | 'development' | 'deployment'  | 'operational';

// Прояв елемента в ОДНІЙ в'ю. Ключ унікальний, напр. "deployment:svc-order".
interface Manifestation { id: string; view: View; label: string; }

// Відповідність (ISO 42010): «це той самий логічний елемент у двох в'ю». Ненапрямлена.
interface Correspondence { a: string; b: string; }

// Деталь розгортання: де живе прояв і які вузли з'єднані мережею.
interface Deployment {
  hosts: Record<string, string[]>;   // id прояву-розгортання → вузли (>1 = репліки)
  links: Array<[string, string]>;    // мережеві зв'язки між вузлами (пари)
}

// Деталь функційної в'ю: виклик між двома елементами, оголошений local|remote.
interface Call { from: string; to: string; kind: 'local' | 'remote'; }

// Увесь опис як дані.
interface Description {
  manifestations: Manifestation[];
  correspondences: Correspondence[];
  deployment: Deployment;
  calls: Call[];
  requiredViews: View[];             // в'ю, у які МУСИТЬ дотягнутися кожен елемент
}
