export enum ActionType {
  NOOP = "NOOP",
  CREATE = "CREATE",
  UPDATE = "UPDATE",
  REPLACE = "REPLACE",
  DESTROY = "DESTROY"
}

export interface ResourceConfig {
  rType: string;
  name: string;
  props: Record<string, any>;
  deps?: string[];
  immutableKeys?: string[];
}

export class Resource {
  public readonly urn: string;
  constructor(public readonly config: ResourceConfig) {
    this.urn = `${config.rType}.${config.name}`;
  }
}

export interface ResourceState {
  urn: string;
  physicalId: string;
  props: Record<string, any>;
}

export interface PlanItem {
  urn: string;
  action: ActionType;
  oldProps?: Record<string, any>;
  newProps?: Record<string, any>;
  physicalId?: string;
}

export class MockCloudProvider {
  private cloudResources = new Map<string, Record<string, any>>();
  private idCounter = 1000;

  async create(rType: string, props: Record<string, any>): Promise<string> {
    this.idCounter += 1;
    const physId = `${rType.toLowerCase()}-${this.idCounter}`;
    this.cloudResources.set(physId, JSON.parse(JSON.stringify(props)));
    return physId;
  }

  async update(physId: string, props: Record<string, any>): Promise<void> {
    if (!this.cloudResources.has(physId)) {
      throw new Error(`Хмарний ресурс ${physId} не знайдено`);
    }
    const current = this.cloudResources.get(physId)!;
    this.cloudResources.set(physId, { ...current, ...props });
  }

  async delete(physId: string): Promise<void> {
    this.cloudResources.delete(physId);
  }

  async read(physId: string): Promise<Record<string, any> | null> {
    return this.cloudResources.get(physId) ? { ...this.cloudResources.get(physId)! } : null;
  }
}

export class StateStore {
  private resources = new Map<string, ResourceState>();
  private locked = false;

  acquireLock(): boolean {
    if (this.locked) return false;
    this.locked = true;
    return true;
  }

  releaseLock(): void {
    this.locked = false;
  }

  get(urn: string): ResourceState | undefined {
    return this.resources.get(urn);
  }

  set(state: ResourceState): void {
    this.resources.set(state.urn, state);
  }

  remove(urn: string): void {
    this.resources.delete(urn);
  }

  getAll(): ResourceState[] {
    return Array.from(this.resources.values());
  }
}

export class IaCEngine {
  constructor(private provider: MockCloudProvider, private state: StateStore) {}

  buildDagAndSort(desired: Map<string, Resource>): string[] {
    const inDegree = new Map<string, number>();
    const adj = new Map<string, string[]>();

    for (const urn of desired.keys()) {
      inDegree.set(urn, 0);
      adj.set(urn, []);
    }

    for (const [urn, res] of desired.entries()) {
      const deps = res.config.deps || [];
      for (const dep of deps) {
        if (!desired.has(dep)) {
          throw new Error(`Ресурс ${urn} посилається на невідому залежність ${dep}`);
        }
        adj.get(dep)!.push(urn);
        inDegree.set(urn, (inDegree.get(urn) || 0) + 1);
      }
    }

    const queue: string[] = [];
    for (const [urn, deg] of inDegree.entries()) {
      if (deg === 0) queue.push(urn);
    }

    const order: string[] = [];
    while (queue.length > 0) {
      const node = queue.shift()!;
      order.push(node);
      for (const neighbor of adj.get(node)!) {
        const nextDeg = inDegree.get(neighbor)! - 1;
        inDegree.set(neighbor, nextDeg);
        if (nextDeg === 0) queue.push(neighbor);
      }
    }

    if (order.length !== desired.size) {
      throw new Error("Виявлено циклічну залежність в графі ресурсів!");
    }

    return order;
  }

  async computePlan(desired: Map<string, Resource>): Promise<PlanItem[]> {
    const plan: PlanItem[] = [];
    const visited = new Set<string>();

    for (const [urn, res] of desired.entries()) {
      visited.add(urn);
      const currState = this.state.get(urn);

      if (!currState) {
        plan.push({ urn, action: ActionType.CREATE, newProps: res.config.props });
      } else {
        const realProps = await this.provider.read(currState.physicalId);
        if (!realProps) {
          plan.push({ urn, action: ActionType.CREATE, newProps: res.config.props });
          continue;
        }

        const isSame = JSON.stringify(realProps) === JSON.stringify(res.config.props);
        if (isSame) {
          plan.push({ urn, action: ActionType.NOOP, oldProps: realProps, newProps: res.config.props, physicalId: currState.physicalId });
        } else {
          const immKeys = res.config.immutableKeys || [];
          const needsReplace = immKeys.some((k) => realProps[k] !== res.config.props[k]);
          const action = needsReplace ? ActionType.REPLACE : ActionType.UPDATE;
          plan.push({ urn, action, oldProps: realProps, newProps: res.config.props, physicalId: currState.physicalId });
        }
      }
    }

    for (const st of this.state.getAll()) {
      if (!visited.has(st.urn)) {
        plan.push({ urn: st.urn, action: ActionType.DESTROY, oldProps: st.props, physicalId: st.physicalId });
      }
    }

    return plan;
  }

  async apply(desired: Map<string, Resource>): Promise<void> {
    if (!this.state.acquireLock()) {
      throw new Error("Помилка: файл стану заблокований іншим процесом");
    }

    try {
      const order = this.buildDagAndSort(desired);
      const plan = await this.computePlan(desired);
      const planMap = new Map(plan.map((p) => [p.urn, p]));

      for (const item of plan) {
        if (item.action === ActionType.DESTROY && item.physicalId) {
          await this.provider.delete(item.physicalId);
          this.state.remove(item.urn);
        }
      }

      for (const urn of order) {
        const item = planMap.get(urn);
        if (!item) continue;

        if (item.action === ActionType.CREATE) {
          const res = desired.get(urn)!;
          const physId = await this.provider.create(res.config.rType, item.newProps!);
          this.state.set({ urn, physicalId: physId, props: item.newProps! });
        } else if (item.action === ActionType.UPDATE && item.physicalId) {
          await this.provider.update(item.physicalId, item.newProps!);
          this.state.set({ urn, physicalId: item.physicalId, props: item.newProps! });
        } else if (item.action === ActionType.REPLACE && item.physicalId) {
          const res = desired.get(urn)!;
          await this.provider.delete(item.physicalId);
          const newPhysId = await this.provider.create(res.config.rType, item.newProps!);
          this.state.set({ urn, physicalId: newPhysId, props: item.newProps! });
        }
      }
    } finally {
      this.state.releaseLock();
    }
  }
}
