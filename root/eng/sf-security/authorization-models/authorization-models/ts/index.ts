// одні ворота: рішення тут, а не розсіяне по місцях застосування
type Perm = `${string}:${string}`;                 // "client:delete"

const rolePerms: Record<string, Perm[]> = {
  manager:  ["client:delete", "client:read"],
  operator: ["client:read"],
};

function can(user: { roles: string[] }, perm: Perm): boolean {
  // deny-by-default: доки жодна роль не дала право — «ні»
  return user.roles.some(r => (rolePerms[r] ?? []).includes(perm));
}

// місце застосування лише питає й кориться:
if (!can(current, "client:delete")) throw new Forbidden();
