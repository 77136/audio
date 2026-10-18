"""Cria o pacote portatil Windows 10/11 x86_64 usando um Zig ja instalado.

Somente para recriar o pacote durante o desenvolvimento:
    python3 windows-launcher/criar_exe.py --zig /caminho/para/zig
    MERCADO_ZIG=/caminho/para/zig python3 windows-launcher/criar_exe.py

O usuario final abre Mercado SQL.exe e nao precisa de Python, Node ou Zig.
Este script nao baixa compiladores nem instala componentes.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import zipfile


SOURCE = Path(__file__).resolve().parent
KIT = SOURCE.parent
APP = KIT / 'windows-app'
ARCHIVE = KIT.parent / 'Mercado-SQL-Windows.zip'
ARCHIVE_FOLDER = 'Mercado SQL Windows'
RESOURCES = (
    'LEIA-ME.html', 'mercado.db', '01_mercado.sql', '02_exercicios.sql',
    '03_gabarito.sql', '04_resultados_esperados.html', 'esquema.sql',
    'validacao.txt', 'teste-sqliteonline.png', 'aprendizagem.json',
    'validacao-aprendizagem.txt', 'gerar_banco.py', 'validar_banco.py',
    'atualizar_aprendizagem.py',
)


def find_zig(value: str | None) -> Path:
    candidate = value or os.environ.get('MERCADO_ZIG') or shutil.which('zig')
    if not candidate:
        raise FileNotFoundError(
            'Informe um Zig local com --zig ou MERCADO_ZIG. '
            'Nenhum compilador sera baixado automaticamente.'
        )
    compiler = Path(candidate).expanduser()
    if compiler.is_dir():
        compiler = compiler / ('zig.exe' if os.name == 'nt' else 'zig')
    if not compiler.is_file():
        found = shutil.which(str(compiler))
        if found:
            compiler = Path(found)
    if not compiler.is_file():
        raise FileNotFoundError(f'Executavel Zig nao encontrado: {compiler}')
    return compiler.resolve()


def check_inputs() -> None:
    missing = [name for name in RESOURCES if not (KIT / name).is_file()]
    if missing:
        raise FileNotFoundError('Recursos ausentes: ' + ', '.join(missing))
    if not (SOURCE / 'main.c').is_file():
        raise FileNotFoundError(SOURCE / 'main.c')


def check_windows_binary(path: Path) -> None:
    """Confirma PE32+ x86_64 com subsistema GUI, sem executar codigo Windows."""
    data = path.read_bytes()
    if len(data) < 64 or data[:2] != b'MZ':
        raise ValueError('O compilador nao produziu um executavel Windows PE.')
    pe_offset = struct.unpack_from('<I', data, 0x3C)[0]
    if pe_offset + 94 > len(data) or data[pe_offset:pe_offset + 4] != b'PE\0\0':
        raise ValueError('Cabecalho PE invalido.')
    machine = struct.unpack_from('<H', data, pe_offset + 4)[0]
    optional_offset = pe_offset + 24
    magic = struct.unpack_from('<H', data, optional_offset)[0]
    subsystem = struct.unpack_from('<H', data, optional_offset + 68)[0]
    if machine != 0x8664 or magic != 0x20B or subsystem != 2:
        raise ValueError('Esperado: Windows x86_64, PE32+ e subsistema GUI.')


def build(zig: Path) -> None:
    check_inputs()
    # O pacote anterior permanece intacto se a compilacao falhar.
    with tempfile.TemporaryDirectory(prefix='.windows-build-', dir=KIT) as stage:
        stage_directory = Path(stage)
        staged_app = stage_directory / 'windows-app'
        assets = staged_app / 'conteudo'
        assets.mkdir(parents=True)
        for name in RESOURCES:
            shutil.copy2(KIT / name, assets / name)
        executable = staged_app / 'Mercado SQL.exe'
        subprocess.run([
            str(zig), 'cc', '-target', 'x86_64-windows-gnu', '-std=c11',
            '-Os', '-s', '-Wl,--subsystem,windows', '-Wall', '-Wextra', '-Werror',
            str(SOURCE / 'main.c'), '-o', str(executable),
            '-lshell32', '-lshlwapi', '-lole32',
        ], check=True)
        check_windows_binary(executable)
        (staged_app / 'LEIA-ME.txt').write_text(
            'Extraia todo o ZIP. Abra Mercado SQL.exe.\n'
            'Para executar SQL, importe conteudo\\mercado.db em https://sqliteonline.com/.\n',
            encoding='utf-8',
        )
        staged_archive = stage_directory / ARCHIVE.name
        with zipfile.ZipFile(staged_archive, 'w', zipfile.ZIP_DEFLATED) as package:
            for path in sorted(staged_app.rglob('*')):
                if path.is_file():
                    relative = path.relative_to(staged_app).as_posix()
                    package.write(path, f'{ARCHIVE_FOLDER}/{relative}')
        with zipfile.ZipFile(staged_archive) as package:
            bad_member = package.testzip()
            expected = {
                f'{ARCHIVE_FOLDER}/Mercado SQL.exe',
                f'{ARCHIVE_FOLDER}/LEIA-ME.txt',
                *(f'{ARCHIVE_FOLDER}/conteudo/{name}' for name in RESOURCES),
            }
            if bad_member or set(package.namelist()) != expected:
                raise ValueError('O ZIP gerado nao passou na verificacao dos arquivos.')
        shutil.copytree(staged_app, APP, dirs_exist_ok=True)
        os.replace(staged_archive, ARCHIVE)
    print(f'Aplicativo: {APP / "Mercado SQL.exe"}')
    print(f'ZIP: {ARCHIVE} ({ARCHIVE.stat().st_size:,} bytes)')
    print(f'Recursos: {len(RESOURCES)}; alvo Windows 10/11 x86_64; PE GUI validado.')
    print('Abertura no navegador requer verificacao em um computador Windows.')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zig', help='Caminho do executavel ou da pasta do Zig local.')
    parser.add_argument('--check', action='store_true',
                        help='Verifica recursos e localiza Zig sem compilar nem copiar arquivos.')
    args = parser.parse_args()
    try:
        check_inputs()
        compiler = find_zig(args.zig)
        if args.check:
            print(f'Zig local: {compiler}')
            print(f'Recursos conferidos: {len(RESOURCES)}')
            print('Nenhum arquivo foi compilado ou copiado.')
            return
        build(compiler)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Nao foi possivel criar o pacote Windows: {error}\n')


if __name__ == '__main__':
    main()
