# exportJson.spec
# Generado para el proyecto siscont_json con NiceGUI + FastAPI + uvicorn
# Uso: pyinstaller --clean exportJson.spec

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# ── Datos de paquetes externos ───────────────────────────────
nicegui_datas    = collect_data_files('nicegui')
uvicorn_datas    = collect_data_files('uvicorn')
pydantic_datas   = collect_data_files('pydantic')
certifi_datas    = collect_data_files('certifi')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # ── Módulos del proyecto ─────────────────────────────
        ('api',      'api'),
        ('db',       'db'),
        ('services', 'services'),
        ('state',    'state'),
        ('ui',       'ui'),
        ('utils',    'utils'),
        ('static',   'static'),
        # ── Archivos raíz ────────────────────────────────────
        ('config.py', '.'),
        ('debug_startup.py', '.'), 
        # ── Datos de librerías externas ──────────────────────
        *nicegui_datas,
        *uvicorn_datas,
        *pydantic_datas,
        *certifi_datas,
    ],
    hiddenimports=[
        # ── Submódulos del proyecto ──────────────────────────
        *collect_submodules('api'),
        *collect_submodules('db'),
        *collect_submodules('services'),
        *collect_submodules('state'),
        *collect_submodules('ui'),
        *collect_submodules('utils'),

        # ── uvicorn internals ────────────────────────────────
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.loops.asyncio',
        'uvicorn.loops.uvloop',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.http.httptools_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.websockets_impl',
        'uvicorn.protocols.websockets.wsproto_impl',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',

        # ── pydantic / pydantic_settings ────────────────────
        'pydantic',
        'pydantic.v1',
        'pydantic_settings',

        # ── nicegui / fastapi / starlette ────────────────────
        'nicegui',
        'fastapi',
        'starlette',
        'starlette.routing',
        'starlette.middleware',
        'starlette.middleware.sessions',

        # ── SQLAlchemy / drivers BD ──────────────────────────
        'sqlalchemy',
        'sqlalchemy.dialects.mssql',
        'sqlalchemy.dialects.mssql.pyodbc',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.dialects.postgresql',
        'pyodbc',

        # ── Otros ────────────────────────────────────────────
        'dotenv',
        'python_dotenv',
        'anyio',
        'anyio._backends._asyncio',
        'anyio._backends._trio',
        'h11',
        'httptools',
        'websockets',
        'orjson',
        'jinja2',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Excluir lo que no usas para reducir tamaño
        'tkinter',
        'matplotlib',
        'scipy',
        'PIL',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='exportJson',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,           # True = ver logs en terminal (útil para debug)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)