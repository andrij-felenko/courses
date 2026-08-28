// Сценарій, що пройшов рев'ю, стає стоячою фітнес-функцією:
// «шлях аварійного стопу НЕ залежить від черги телеметрії».
// Порушиш межу — впаде CI, а не поле через пів року.
import { moduleGraph } from "./arch";

const STOP = "control/estop";
const TELEMETRY_QUEUE = "telemetry/queue";

test("аварійний стоп не тече крізь чергу телеметрії", () => {
  const reachable = moduleGraph.dependenciesOf(STOP); // усі транзитивні залежності
  expect(reachable).not.toContain(TELEMETRY_QUEUE);
});
