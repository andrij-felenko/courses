// Піраміда вкладень: горизонтальне розростання замість вертикального
loadConfig((err, config) => {
  if (err) return handleError(err);
  connectDatabase(config.dbUrl, (err, db) => {
    if (err) return handleError(err);
    authenticateUser(db, token, (err, user) => {
      if (err) return handleError(err);
      fetchAccount(db, user.id, (err, account) => {
        if (err) return handleError(err);
        sendResponse({ user, account });
      });
    });
  });
});
