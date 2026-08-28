// DTO сутностей для TypeScript / Node.js реалізації
interface ProductRecord {
  id: number;
  title: string;
  category: string;
  price: number;
  version: number;
  isDeleted: boolean;
}

interface OutboxEvent {
  seqId: number;
  aggregateId: number;
  eventType: 'UPSERT' | 'DELETE';
  payload: Record<string, unknown>;
  version: number;
  processed: boolean;
}

interface IndexedDocument {
  id: number;
  title: string;
  category: string;
  price: number;
  version: number;
}

// Пошуковий індекс з оптимістичним контролем версій
class SearchIndex {
  private storage = new Map<number, IndexedDocument>();

  constructor(public readonly name: string) {}

  public indexDocument(doc: IndexedDocument): boolean {
    const existing = this.storage.get(doc.id);
    if (existing && doc.version < existing.version) {
      console.log(`[${this.name}] Відкинуто застарілу версію doc#${doc.id} (поточна: ${existing.version}, вхідна: ${doc.version})`);
      return false;
    }
    this.storage.set(doc.id, doc);
    console.log(`[${this.name}] Проіндексовано doc#${doc.id} (v${doc.version}: '${doc.title}')`);
    return true;
  }

  public get(id: number): IndexedDocument | undefined {
    return this.storage.get(id);
  }

  public size(): number {
    return this.storage.size;
  }
}

// Кластер із підтримкою аліасів
class SearchCluster {
  private indices = new Map<string, SearchIndex>();
  private aliases = new Map<string, string>();

  public registerIndex(index: SearchIndex): void {
    this.indices.set(index.name, index);
  }

  public setAlias(alias: string, targetIndexName: string): void {
    if (!this.indices.has(targetIndexName)) {
      throw new Error(`Цільовий індекс ${targetIndexName} не зареєстровано`);
    }
    this.aliases.set(alias, targetIndexName);
    console.log(`[CLUSTER] Аліас '${alias}' перемкнуто на '${targetIndexName}'`);
  }

  public getByAlias(alias: string): SearchIndex | undefined {
    const target = this.aliases.get(alias);
    return target ? this.indices.get(target) : undefined;
  }
}

// Реляційна база з Transactional Outbox
class RelationalDatabase {
  private products = new Map<number, ProductRecord>();
  private outbox: OutboxEvent[] = [];

  public saveProduct(id: number, title: string, category: string, price: number): void {
    const current = this.products.get(id);
    const nextVer = current ? current.version + 1 : 1;

    const record: ProductRecord = {
      id,
      title,
      category,
      price,
      version: nextVer,
      isDeleted: false,
    };
    this.products.set(id, record);

    const seqId = this.outbox.length + 1;
    this.outbox.push({
      seqId,
      aggregateId: id,
      eventType: 'UPSERT',
      payload: { title, category, price },
      version: nextVer,
      processed: false,
    });

    console.log(`[DB] Збережено товар #${id} v${nextVer}, додано outbox seq#${seqId}`);
  }

  public fetchUnprocessedOutbox(limit: number): OutboxEvent[] {
    return this.outbox.filter((e) => !e.processed).slice(0, limit);
  }

  public markProcessed(seqId: number): void {
    const ev = this.outbox.find((e) => e.seqId === seqId);
    if (ev) ev.processed = true;
  }

  public getAllActiveProducts(): ProductRecord[] {
    return Array.from(this.products.values()).filter((p) => !p.isDeleted);
  }

  public getCurrentMaxSeq(): number {
    return this.outbox.length;
  }

  public getEventsAfter(seq: number): OutboxEvent[] {
    return this.outbox.filter((e) => e.seqId > seq);
  }
}

// Конвеєр живої міграції та синхронізації
class SearchSyncPipeline {
  constructor(
    private db: RelationalDatabase,
    private cluster: SearchCluster,
  ) {}

  public processOutbox(aliasName: string): void {
    const index = this.cluster.getByAlias(aliasName);
    if (!index) throw new Error(`Аліас ${aliasName} не знайдено`);

    const batch = this.db.fetchUnprocessedOutbox(10);
    for (const ev of batch) {
      if (ev.eventType === 'UPSERT') {
        index.indexDocument({
          id: ev.aggregateId,
          title: String(ev.payload.title),
          category: String(ev.payload.category),
          price: Number(ev.payload.price),
          version: ev.version,
        });
      }
      this.db.markProcessed(ev.seqId);
    }
  }

  public executeZeroDowntimeReindex(aliasName: string, newIndexName: string): void {
    console.log(`\n=== СТАРТ МІГРАЦІЇ В ${newIndexName} ===`);
    const newIndex = new SearchIndex(newIndexName);
    this.cluster.registerIndex(newIndex);

    const snapshotSeq = this.db.getCurrentMaxSeq();
    const items = this.db.getAllActiveProducts();

    console.log(`[MIGRATION] Бекфіл: перенесення ${items.length} записів...`);
    for (const item of items) {
      newIndex.indexDocument({
        id: item.id,
        title: item.title,
        category: item.category,
        price: item.price,
        version: item.version,
      });
    }

    const delta = this.db.getEventsAfter(snapshotSeq);
    console.log(`[MIGRATION] Доганяння: застосування ${delta.length} подій...`);
    for (const ev of delta) {
      newIndex.indexDocument({
        id: ev.aggregateId,
        title: String(ev.payload.title),
        category: String(ev.payload.category),
        price: Number(ev.payload.price),
        version: ev.version,
      });
    }

    this.cluster.setAlias(aliasName, newIndexName);
    console.log(`=== МІГРАЦІЮ ЗАВЕРШЕНО ===\n`);
  }
}
