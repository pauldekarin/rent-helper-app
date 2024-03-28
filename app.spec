# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/data/*.db', 'assets/data'),
        ('assets/fonts/Piazzolla/*.ttf', 'assets/fonts/Piazzolla'),
        ('assets/images/icons/*.png', 'assets/images/icons'),
        ('assets/images/*.png','assets/images'), 
        ('assets/json/*.json', 'assets/json')
        ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='main',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )

app = BUNDLE(exe,
             name='Rent Helper.app',
             icon=None,
             bundle_identifier=None)