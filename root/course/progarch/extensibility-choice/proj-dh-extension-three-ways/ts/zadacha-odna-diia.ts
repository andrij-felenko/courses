type MotionEvent = {
  sensor: string;   // "hallway-pir"
  room: string;     // "коридор"
  at: number;       // Unix-час, мілісекунди
};

// контекст — вузька поверхня: лише те, що дія має право робити
interface HubContext {
  home: { mode: "home" | "away" | "night" };
  light: { blink(room: string, times: number): void };
  notify: { push(text: string): void };
}
