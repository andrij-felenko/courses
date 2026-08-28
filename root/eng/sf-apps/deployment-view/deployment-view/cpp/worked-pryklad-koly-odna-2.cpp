static const Container API{ "api" };
static const Container DB { "db"  };

// dev: усе на одному вузлі, по одній копії.
const std::vector<Deployment> DEV = {
    { "laptop", &API, 1 },
    { "laptop", &DB,  1 },
};

// prod: три копії api на трьох вузлах, одна db окремо.
const std::vector<Deployment> PROD = {
    { "eu-node-1", &API, 1 },
    { "eu-node-2", &API, 1 },
    { "eu-node-3", &API, 1 },
    { "eu-db-1",   &DB,  1 },
};
