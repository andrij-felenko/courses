// Класична реалізація запиту дозволів для платформи Android
public class CameraActivityLegacy extends AppCompatActivity {

    private static final int PERMISSION_REQUEST_CAMERA = 101;

    private void checkAndRequestCamera() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                == PackageManager.PERMISSION_GRANTED) {
            startCameraStream();
        } else if (ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.CAMERA)) {
            showRationaleDialog(() -> ActivityCompat.requestPermissions(
                CameraActivityLegacy.this,
                new String[]{Manifest.permission.CAMERA},
                PERMISSION_REQUEST_CAMERA
            ));
        } else {
            ActivityCompat.requestPermissions(
                this,
                new String[]{Manifest.permission.CAMERA},
                PERMISSION_REQUEST_CAMERA
            );
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST_CAMERA) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                startCameraStream();
            } else {
                showPermissionDeniedExplanation();
            }
        }
    }

    private void startCameraStream() {}
    private void showRationaleDialog(Runnable onAccept) {}
    private void showPermissionDeniedExplanation() {}
}
