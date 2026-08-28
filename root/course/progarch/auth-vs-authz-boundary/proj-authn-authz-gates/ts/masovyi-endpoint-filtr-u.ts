// ✗ підняти все, відсіяти в памʼяті — повільно й крихко
app.get("/homes", authenticate, (req, res) => {
  const mine = homes.all().filter(h => can(req.subject!, "read", h));
  res.json(mine);
});

// ✓ авторизація як умова запиту — чужі рядки не залишають БД
app.get("/homes", authenticate, (req, res) => {
  res.json(homes.listForMember(req.subject!.id));    // JOIN membership …
});
