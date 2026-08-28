import json
import hashlib

def build_cyclonedx_sbom(firmware_name: str, assets: list) -> dict:
    components = []
    
    for asset in assets:
        if asset["type"] == "TFLiteModel":
            comp = {
                "type": "machine-learning-model",
                "bom-ref": f"model-tflite-{asset['offset']:08x}",
                "name": "EdgeDetectionQuantizedModel",
                "version": "1.2.0",
                "description": "INT8 quantized convolutional neural network for anomaly detection",
                "modelCard": {
                    "modelParameters": {
                        "approach": { "type": "supervised" },
                        "task": "anomaly-detection",
                        "architectureFamily": "MobileNetV2-Lite"
                    },
                    "datasets": [
                        {
                            "type": "training",
                            "name": "IndustrialVibrationDataset-v2",
                            "governance": {
                                "licenses": [ { "license": { "id": "CC-BY-4.0" } } ]
                            }
                        }
                    ]
                },
                "licenses": [ { "license": { "id": "Apache-2.0" } } ],
                "hashes": [ { "alg": "SHA-256", "content": asset["sha256"] } ]
            }
            components.append(comp)
            
        elif asset["type"] == "FontTrueType":
            comp = {
                "type": "data",
                "bom-ref": f"font-embedded-{asset['offset']:08x}",
                "name": "Inter-Regular",
                "version": "4.0",
                "description": "Embedded TrueType Typography Font Software for GUI",
                "licenses": [
                    {
                        "license": {
                            "id": "OFL-1.1",
                            "url": "https://spdx.org/licenses/OFL-1.1.html"
                        }
                    }
                ],
                "properties": [
                    { "name": "font:embedding-type", "value": "flash-rom" },
                    { "name": "font:reserved-font-name", "value": "Inter" }
                ],
                "hashes": [ { "alg": "SHA-256", "content": asset["sha256"] } ]
            }
            components.append(comp)

    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": "urn:uuid:3e671687-395b-41f5-a30f-a58921a69b79",
        "version": 1,
        "metadata": {
            "component": {
                "type": "device",
                "name": firmware_name,
                "version": "2.4.0-production"
            }
        },
        "components": components
    }
