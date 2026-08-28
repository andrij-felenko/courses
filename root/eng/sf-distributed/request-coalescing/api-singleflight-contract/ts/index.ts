import DataLoader from 'dataloader';

interface User {
    id: string;
    name: string;
}

// Функція пакетного завантаження
async function batchGetUsers(ids: readonly string[]): Promise<(User | Error)[]> {
    const users = await db.users.findMany({ where: { id: { in: [...ids] } } });
    const userMap = new Map(users.map(u => [u.id, u]));
    return ids.map(id => userMap.get(id) || new Error(`User ${id} not found`));
}

const userLoader = new DataLoader<string, User>(batchGetUsers, {
    cache: true,              // Дедуплікація однакових ключів у межах одного такту
    maxBatchSize: 100,        // Максимальна кількість ключів в одному SQL-запиті
    batchScheduleFn: callback => setTimeout(callback, 5) // Часове вікно збирання 5 мс
});
