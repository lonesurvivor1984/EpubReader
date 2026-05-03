# -*- mode: python ; coding: utf-8 -*-
# Mac build spec — must be run on a Mac:
#   pip install pyinstaller
#   pyinstaller EpubReader_mac.spec --noconfirm
#
# Icon: Mac requires .icns format.
# Convert from epub.ico on Mac:
#   mkdir epub.iconset
#   sips -z 16 16   forexe/epub.ico --out epub.iconset/icon_16x16.png
#   sips -z 32 32   forexe/epub.ico --out epub.iconset/icon_16x16@2x.png
#   sips -z 32 32   forexe/epub.ico --out epub.iconset/icon_32x32.png
#   sips -z 64 64   forexe/epub.ico --out epub.iconset/icon_32x32@2x.png
#   sips -z 128 128 forexe/epub.ico --out epub.iconset/icon_128x128.png
#   sips -z 256 256 forexe/epub.ico --out epub.iconset/icon_128x128@2x.png
#   sips -z 256 256 forexe/epub.ico --out epub.iconset/icon_256x256.png
#   sips -z 512 512 forexe/epub.ico --out epub.iconset/icon_256x256@2x.png
#   iconutil -c icns epub.iconset -o forexe/epub.icns
# If you skip icon conversion, remove the icon= line from BUNDLE below.

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('app', 'app')],
    hiddenimports=[
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebEngineCore',
        'lxml',
        'lxml.etree',
        'chardet',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EpubReader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    argv_emulation=True,
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EpubReader',
)

app = BUNDLE(
    coll,
    name='EpubReader.app',
    icon='forexe/epub.icns',
    bundle_identifier='com.epubreader.app',
    info_plist={
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'CFBundleShortVersionString': '0.1.0',
        'CFBundleName': 'EpubReader',
        'CFBundleDisplayName': 'EpubReader',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'EPUB Document',
                'CFBundleTypeExtensions': ['epub'],
                'CFBundleTypeRole': 'Viewer',
            }
        ],
    },
)
