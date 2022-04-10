# -*- mode: python ; coding: utf-8 -*-
# python -m PyInstaller --distpath ../dist --workpath ../build .\fsl.spec

block_cipher = None

a = Analysis(['fsl.py'],
             pathex=[],
             binaries=[],
             datas=[('logo.icns', '.')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

splash = Splash('logo.png',
                binaries=a.binaries,
                datas=a.datas,
                text_pos=(10, 50),
                text_size=6,
                text_color='black')

exe = EXE(pyz,
          a.scripts,
          splash,
          splash.binaries,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='FarmingSimulatorLauncher',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

app = BUNDLE(
          exe,
          name = 'FarmingSimulatorLauncher.app',
          icon = 'logo.icns',
          bundle_identifier = None,
          version = '1.0.0',
          info_plist = {
              'NSPrincipalClass': 'NSApplication',
              'NSHighResolutionCapable': 'True',
              'NSAppleScriptEnabled': False
          }
)
