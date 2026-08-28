// Класичний патерн зворотного виклику з обробкою помилок першим аргументом
function loadUserData(userId: string, callback: (err: Error | null, data?: User) => void): void {
  db.findUser(userId, (err, user) => {
    if (err) {
      callback(err);
      return;
    }
    fetchPermissions(user.roleId, (err, perms) => {
      if (err) {
        callback(err);
        return;
      }
      callback(null, { ...user, permissions: perms });
    });
  });
}
