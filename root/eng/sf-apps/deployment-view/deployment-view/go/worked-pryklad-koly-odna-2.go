var (
	API = Container{Name: "api"}
	DB  = Container{Name: "db"}
)

// dev: усе на одному вузлі, по одній копії.
var DEV = []Deployment{
	{Node: "laptop", Of: &API, Replicas: 1},
	{Node: "laptop", Of: &DB, Replicas: 1},
}

// prod: три копії api на трьох вузлах, одна db окремо.
var PROD = []Deployment{
	{Node: "eu-node-1", Of: &API, Replicas: 1},
	{Node: "eu-node-2", Of: &API, Replicas: 1},
	{Node: "eu-node-3", Of: &API, Replicas: 1},
	{Node: "eu-db-1", Of: &DB, Replicas: 1},
}
