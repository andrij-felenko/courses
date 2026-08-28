// Сучасний ідіоматичний запит дозволу через Activity Result API
class CameraActivity : AppCompatActivity() {

    private val requestCameraPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            startCameraStream()
        } else {
            // Користувач відмовив у доступі: вимикаємо функцію без падіння
            showPermissionDeniedExplanation()
        }
    }

    private fun checkAndRequestCamera() {
        when {
            ContextCompat.checkSelfPermission(
                this, Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED -> {
                startCameraStream()
            }
            ActivityCompat.shouldShowRequestPermissionRationale(
                this, Manifest.permission.CAMERA
            ) -> {
                // Показуємо користувачеві контекстне пояснення перед системним діалогом
                showRationaleDialog {
                    requestCameraPermissionLauncher.launch(Manifest.permission.CAMERA)
                }
            }
            else -> {
                // Прямий системний запит
                requestCameraPermissionLauncher.launch(Manifest.permission.CAMERA)
            }
        }
    }

    private fun startCameraStream() { /* Ініціалізація CameraX / NDK */ }
    private fun showRationaleDialog(onAccept: () -> Unit) { /* Діалог */ }
    private fun showPermissionDeniedExplanation() { /* Сповіщення */ }
}
