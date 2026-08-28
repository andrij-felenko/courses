// main.ts — composition root. Поза доменом. Єдине місце, що бачить обидва світи.
import { CrmHttpClient } from "./crm/httpClient";
import { CrmOrderFacade } from "./acl/crmFacade";
import { CrmOrderSource } from "./acl/crmOrderSource";
import { OrderService } from "./domain/orderService";

const http   = new CrmHttpClient(process.env.CRM_URL!);
const facade = new CrmOrderFacade(http);
const source = new CrmOrderSource(facade);   // ← ось де CRM стає OrderSource
const service = new OrderService(source);    // домен бачить лише порт

service.processBatch();
