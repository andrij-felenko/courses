interface RelationTuple {
  objectId: string;   // e.g., "camera:704"
  relation: string;   // e.g., "viewer"
  subjectId: string;  // e.g., "user:alice" or "home:101#owner"
}

interface EvalContext {
  currentTimeHour: number;
  allowedStartHour: number;
  allowedEndHour: number;
}

export class RebacAbacEngine {
  private tuples: Map<string, RelationTuple[]> = new Map();

  public addTuple(objectId: string, relation: string, subjectId: string): void {
    const list = this.tuples.get(objectId) ?? [];
    list.push({ objectId, relation, subjectId });
    this.tuples.set(objectId, list);
  }

  public checkRebac(subjectId: string, relation: string, objectId: string, visited = new Set<string>()): boolean {
    const stateKey = `${objectId}#${relation}@${subjectId}`;
    if (visited.has(stateKey)) return false;
    visited.add(stateKey);

    const list = this.tuples.get(objectId) ?? [];
    for (const t of list) {
      if (t.relation !== relation) continue;

      if (t.subjectId === subjectId) return true;

      if (t.subjectId.includes("#")) {
        const [parentObj, parentRel] = t.subjectId.split("#");
        if (this.checkRebac(subjectId, parentRel, parentObj, visited)) {
          return true;
        }
      }
    }
    return false;
  }

  public evaluate(subjectId: string, action: string, objectId: string, ctx: EvalContext): boolean {
    if (!this.checkRebac(subjectId, action, objectId)) {
      return false;
    }
    if (ctx.currentTimeHour < ctx.allowedStartHour || ctx.currentTimeHour > ctx.allowedEndHour) {
      return false;
    }
    return true;
  }
}
