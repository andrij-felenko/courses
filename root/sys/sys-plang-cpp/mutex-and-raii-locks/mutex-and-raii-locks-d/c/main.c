#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int balance;
    pthread_mutex_t lock;
} BankAccount;

void deposit(BankAccount* account, int amount) {
    pthread_mutex_lock(&account->lock);
    
    if (amount <= 0) {
        // Помилка! Раннє повернення без звільнення м'ютекса
        return; 
    }
    
    account->balance += amount;
    
    pthread_mutex_unlock(&account->lock);
}
