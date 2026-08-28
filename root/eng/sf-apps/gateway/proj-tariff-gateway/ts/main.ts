// main.ts — точка збірки. Поза доменом. Тут абстракція стає конкретикою.
import { HttpТарифШлюз } from "./http/httpTariffGateway";
import { ДоставкаСервіс } from "./domain/доставкаСервіс";
import { Напрямок } from "./domain/tariff";

// ↓ ЄДИНЕ місце, що знає і про HTTP-шлюз, і про домен — і зшиває їх
const шлюз  = new HttpТарифШлюз(process.env.TARIFF_URL!, process.env.TARIFF_TOKEN!);
const домен = new ДоставкаСервіс(шлюз);   // домен дістав шлюз через інтерфейс

console.log(await домен.порадитиСпосіб(new Напрямок("SEG_A")));
