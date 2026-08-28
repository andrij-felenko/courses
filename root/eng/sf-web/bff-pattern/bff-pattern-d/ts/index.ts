// BFF-ендпоінт головного екрана: усе за один запит клієнта
app.get("/home", async (req, res) => {
  const uid = req.user.id;

  // три виклики СТАРТУЮТЬ ОДНОЧАСНО, а не один за одним;
  // allSettled — щоб один провал не зірвав решту
  const [profile, orders, recs] = await Promise.allSettled([
    fetch(`http://profile/users/${uid}`).then(r => r.json()),
    fetch(`http://orders/users/${uid}/recent`).then(r => r.json()),
    fetch(`http://recs/users/${uid}/today`).then(r => r.json()),
  ]);

  // BFF віддає екрану рівно його форму — не сирі відповіді сервісів
  res.json({
    name:   profile.status === "fulfilled" ? profile.value.name  : "друже",
    orders: orders.status  === "fulfilled" ? orders.value.items  : [],
    recs:   recs.status    === "fulfilled" ? recs.value.list     : null,
  });
});
