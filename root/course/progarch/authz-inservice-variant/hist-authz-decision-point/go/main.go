import "github.com/open-policy-agent/opa/rego"

// той самий вердикт — але тепер локальний виклик, без стрибка в мережу
r := rego.New(
    rego.Query("data.authz.allow"),
    rego.Module("authz.rego", policy),        // політика як код, поруч у процесі
)
query, _ := r.PrepareForEval(ctx)
rs, _ := query.Eval(ctx, rego.EvalInput(map[string]any{
    "user": "bohdan", "action": "unlock", "resource": "lock:42",
}))
allow := rs.Allowed()                          // рішення — тут, у цьому ж процесі
