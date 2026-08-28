// status.ts — журнал команд: де зараз кожна команда
export type CommandRecord =
  | { commandId: CommandId; state: "accepted" }                   // у черзі, ще не взято
  | { commandId: CommandId; state: "processing" }                 // споживач узяв
  | { commandId: CommandId; state: "done"; lock: LockState }      // виконано, ось стан
  | { commandId: CommandId; state: "failed"; reason: string };    // впало остаточно

export interface StatusStore {
  put(r: CommandRecord): Promise<void>;
  get(id: CommandId): Promise<CommandRecord | undefined>;
}

// Твін дому — «остання відома правда» про дім, яку читає весь інтерфейс.
export interface Twin {
  merge(home: HomeId, patch: { lock: LockState }): Promise<void>;
}
