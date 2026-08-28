// tests/fitness/exactly-once.test.ts
import { Hub } from "../../hub";

test("замок актуйовано рівно раз при повторі", () => {
  const hub = new Hub();
  const cmd = { id: "c-42", target: "front-door", action: "open" } as const;
  hub.handle(cmd);                      // доставка №1
  hub.handle(cmd);                      // той самий id: повтор після втраченого ack
  expect(hub.lock("front-door").actuations).toBe(1);
});
