// acl/crmFacade.ts — ховає незручний доступ. Усе ще в ЧУЖИХ типах.
import { CrmOrderDto } from "../crm/dto";
import { CrmHttpClient } from "../crm/httpClient"; // сира HTTP-обгортка CRM

export class CrmOrderFacade {
  private buffer: CrmOrderDto[] = [];
  private page = 0;
  private exhausted = false;

  constructor(private http: CrmHttpClient) {}

  // Один чесний виклик замість пагінації, ретраїв і формату відповіді.
  async fetchNext(): Promise<CrmOrderDto | null> {
    if (this.buffer.length === 0 && !this.exhausted) {
      await this.loadPage();
    }
    return this.buffer.shift() ?? null;
  }

  private async loadPage(): Promise<void> {
    const resp = await this.retry(() =>
      this.http.get(`/orders?page=${this.page}&size=100`));
    this.buffer = resp.items;          // сирі CrmOrderDto
    this.exhausted = resp.items.length === 0;
    this.page += 1;
  }

  private async retry<T>(fn: () => Promise<T>, tries = 3): Promise<T> {
    for (let i = 0; ; i++) {
      try { return await fn(); }
      catch (e) { if (i >= tries - 1) throw e; }
    }
  }
}
