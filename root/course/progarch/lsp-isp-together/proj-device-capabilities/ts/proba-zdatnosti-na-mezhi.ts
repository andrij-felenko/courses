function isReadable(d: unknown): d is Readable {
  return typeof (d as Readable)?.read === "function";
}
function isSwitchable(d: unknown): d is Switchable {
  const s = d as Switchable;
  return typeof s?.turnOn === "function" && typeof s?.turnOff === "function";
}
function isLockable(d: unknown): d is Lockable {
  const l = d as Lockable;
  return typeof l?.lock === "function" && typeof l?.unlock === "function";
}
function isStreamable(d: unknown): d is Streamable {
  return typeof (d as Streamable)?.startStream === "function";
}
