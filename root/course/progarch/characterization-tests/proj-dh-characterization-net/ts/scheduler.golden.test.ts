// scheduler.golden.test.ts — той самий задум знімком Jest
import { renderDay, DAY } from "./scheduler_day";

test("день правил DH — золотий еталон", () => {
  // Jest дає обидва дублери з коробки: фейковий годинник і кероване зерно
  const out = renderDay(DAY, {
    clockAt: new Date("2026-01-15T00:00:00"),   // застиглий час (jest.setSystemTime)
    seed: 0,                                     // сталий генератор
  });
  // перший прогін ЗАПИСУЄ .snap поруч; наступні — звіряють байт у байт
  expect(out).toMatchSnapshot();
  // свідома зміна поведінки згодом → jest -u перезатверджує знімок
});
