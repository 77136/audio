"""Cria um .app leve e universal: usuario final nao precisa de Python ou Node.

Recriacao (somente para desenvolvimento, em macOS com Command Line Tools):
    python3 macos-launcher/criar_app.py
"""
from pathlib import Path
import plistlib
import shutil
import subprocess

SOURCE = Path(__file__).resolve().parent
KIT = SOURCE.parent
APP = KIT / 'Mercado SQL.app'
ARCHIVE = KIT.parent / 'Mercado-SQL-Mac.zip'
RESOURCES = [
    'LEIA-ME.html', 'mercado.db', '01_mercado.sql', '02_exercicios.sql',
    '03_gabarito.sql', '04_resultados_esperados.html', 'esquema.sql',
    'validacao.txt', 'teste-sqliteonline.png', 'aprendizagem.json',
    'validacao-aprendizagem.txt', 'gerar_banco.py', 'validar_banco.py',
    'atualizar_aprendizagem.py',
]


def build():
    for name in RESOURCES:
        if not (KIT / name).is_file():
            raise FileNotFoundError(name)
    (APP / 'Contents' / 'MacOS').mkdir(parents=True, exist_ok=True)
    assets = APP / 'Contents' / 'Resources'
    assets.mkdir(parents=True, exist_ok=True)
    for name in RESOURCES:
        shutil.copy2(KIT / name, assets / name)
    info = {
        'CFBundleExecutable': 'MercadoSQL',
        'CFBundleIdentifier': 'br.estudo.mercadosql',
        'CFBundleName': 'Mercado SQL',
        'CFBundleDisplayName': 'Mercado SQL',
        'CFBundlePackageType': 'APPL',
        'CFBundleShortVersionString': '1.1.0',
        'CFBundleVersion': '2',
        'CFBundleDevelopmentRegion': 'pt-BR',
        'LSMinimumSystemVersion': '11.0',
        'LSUIElement': True,
        'NSHighResolutionCapable': True,
    }
    with (APP / 'Contents' / 'Info.plist').open('wb') as file:
        plistlib.dump(info, file)
    (APP / 'Contents' / 'PkgInfo').write_bytes(b'APPL????')
    binary = APP / 'Contents' / 'MacOS' / 'MercadoSQL'
    subprocess.run([
        '/usr/bin/clang', '-arch', 'arm64', '-arch', 'x86_64',
        '-mmacosx-version-min=11.0', '-fobjc-arc', '-Os',
        '-framework', 'AppKit', str(SOURCE / 'main.m'), '-o', str(binary),
    ], check=True)
    binary.chmod(0o755)
    subprocess.run(['/usr/bin/codesign', '--force', '--sign', '-', str(APP)], check=True)
    subprocess.run(['/usr/bin/codesign', '--verify', '--deep', '--strict', str(APP)], check=True)
    subprocess.run([str(binary), '--check'], check=True)
    if ARCHIVE.exists():
        ARCHIVE.unlink()
    subprocess.run([
        '/usr/bin/ditto', '-c', '-k', '--sequesterRsrc', '--keepParent',
        str(APP), str(ARCHIVE),
    ], check=True)
    print(f'Aplicativo: {APP}')
    print(f'ZIP: {ARCHIVE} ({ARCHIVE.stat().st_size:,} bytes)')


if __name__ == '__main__':
    build()
