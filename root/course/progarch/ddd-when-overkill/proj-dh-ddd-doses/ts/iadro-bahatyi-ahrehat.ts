class DomainError extends Error {
  constructor(message: string) { super(message); this.name = "DomainError"; }
}

// Незмінний рецепт, названий по-людськи. Рівність — за вмістом, не за посиланням.
type ClimateIntent =
  | { readonly want: "heat"; readonly targetC: number }
  | { readonly want: "cool"; readonly targetC: number }
  | { readonly want: "off" };

interface Scenario {
  readonly name: string;            // "Ніч", "Прихід додому", "Провітрити"
  readonly climate: ClimateIntent;
  readonly lightsOn: boolean;
}
