// роль → дозволені дії (гість лише читає, сім'я керує, засновник — усе)
const GRANTS: Record<Role, ReadonlySet<Action>> = {
  guest:   new Set(["read"]),
  family:  new Set(["read", "write"]),
  founder: new Set(["read", "write", "manage"]),
};

function can(subject: Subject, action: Action, home: Home): boolean {
  const role = memberships.roleOf(subject.id, home.id);   // Role | undefined
  if (!role) return false;                                // не член → відмова
  return GRANTS[role].has(action);
}
