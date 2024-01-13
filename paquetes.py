import os
import subprocess
import requests
import tarfile
from zipfile import ZipFile
from io import BytesIO

#sudo pip install flet requests
#sudo chmod +x sdk/android-sdk/tools/bin/sdkmanager
#sudo python paquetes.py
#nano ~/.bashrc
#export PATH="$PATH:sdk/flutter-sdk/flutter/bin"
#/workspaces/FletSheet/sdk/flutter-sdk/flutter
#control+o  enter y control+x
#source ~/.bashrc


def download_and_extract(url, extract_to):
    # Verifica si el directorio ya existe y tiene contenido
    if not os.path.exists(extract_to) or not os.listdir(extract_to):
        response = requests.get(url)
        if url.endswith(".zip"):
            with ZipFile(BytesIO(response.content)) as zip_file:
                zip_file.extractall(extract_to)
        elif url.endswith(".tar.xz"):
            with tarfile.open(fileobj=BytesIO(response.content), mode="r:xz") as tar:
                tar.extractall(path=extract_to)

# Instalar Flutter SDK
flutter_url = "https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.16.7-stable.tar.xz"
flutter_extract_to = "sdk/flutter-sdk"
download_and_extract(flutter_url, flutter_extract_to)
# Actualizar PATH para incluir Flutter y Dart
flutter_bin_path = "/workspaces/FletSheet/sdk/flutter-sdk/flutter/bin"
print(f"flutter_bin_path: {flutter_bin_path}")
os.environ["PATH"] += os.pathsep + flutter_bin_path


# Instalar Android SDK
android_sdk_url = "https://dl.google.com/android/repository/commandlinetools-linux-6609375_latest.zip"
android_sdk_extract_to = "sdk/android-sdk"
download_and_extract(android_sdk_url, android_sdk_extract_to)
# Verificar si ANDROID_HOME existe, si no, crearlo
android_sdk_path  = "/workspaces/FletSheet/sdk/android-sdk/tools"
os.environ["ANDROID_HOME"] = android_sdk_path
os.environ["ANDROID_SDK_ROOT"] = android_sdk_path
os.environ["PATH"] += os.pathsep + android_sdk_path

# Busca la ubicación de sdkmanager
# Ejecutar sdkmanager para instalar componentes del SDK de Android y aceptar licencias
sdkmanager_path = os.path.join(android_sdk_extract_to, "tools/bin/sdkmanager")
if not os.path.isfile(sdkmanager_path):
    raise FileNotFoundError(f"No se pudo encontrar sdkmanager en la ruta {sdkmanager_path}")

# Aceptar licencias y descargar componentes necesarios
subprocess.run([sdkmanager_path, "--licenses"])
subprocess.run([sdkmanager_path, "platform-tools", "platforms;android-30", "build-tools;30.0.2"])


# Configurar Flutter para usar Android SDK
subprocess.run(["flutter", "config", "--android-sdk", android_sdk_extract_to])

# Ejecutar Flutter Doctor
subprocess.run(["flutter", "doctor"])

def build_flet(target_platform):
    try:
        subprocess.run(["flet", "build", target_platform], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al construir para {target_platform}: {e}")

# Lista de plataformas objetivo para construir
platforms = ["apk", "aab", "windows", "linux", "ipa", "macos", "web"]

# Ejecutar la construcción para cada plataforma
for platform in platforms:
    print(f"Construyendo para {platform}...")
    build_flet(platform)