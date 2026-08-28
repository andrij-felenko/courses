// acl/crmOrderSource.ts — реалізація ПОРТУ. Склеює фасад + перекладач.
import { OrderSource, Order } from "../domain/order";
import { CrmOrderFacade } from "./crmFacade";
import { translateOrder } from "./orderTranslator";

export class CrmOrderSource implements OrderSource {
  constructor(private facade: CrmOrderFacade) {}

  // Порт синхронний (як оголосив домен); async-фасад мостимо буфером —
  // деталі мосту опущено, суть тут — склейка фасаду з перекладачем.
  next(): Order | null {
    const dto = this.facade.nextBuffered();   // сирий CrmOrderDto або null
    return dto === null ? null : translateOrder(dto);
  }
}
