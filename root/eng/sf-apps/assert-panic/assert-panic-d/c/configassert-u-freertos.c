// FreeRTOSConfig.h — варіант із записом контексту
extern void vAssertCalled( const char *pcFile, unsigned long ulLine );
#define configASSERT( x )  if( ( x ) == 0 ) vAssertCalled( __FILE__, __LINE__ )

// десь у коді застосунку
void vAssertCalled( const char *pcFile, unsigned long ulLine ) {
    log_to_flash("RTOS ASSERT %s:%lu", pcFile, ulLine);   // зафіксувати
    taskDISABLE_INTERRUPTS();                              // зупинити тік
    for( ;; );                                            // не йти далі
}
