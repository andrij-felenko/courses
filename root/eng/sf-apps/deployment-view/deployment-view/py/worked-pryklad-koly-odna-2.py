API = Container("api")
DB  = Container("db")

# dev: усе на одному вузлі, по одній копії.
DEV = [
    Deployment("laptop", API, 1),
    Deployment("laptop", DB,  1),
]

# prod: три копії api на трьох вузлах, одна db окремо.
PROD = [
    Deployment("eu-node-1", API, 1),
    Deployment("eu-node-2", API, 1),
    Deployment("eu-node-3", API, 1),
    Deployment("eu-db-1",   DB,  1),
]
