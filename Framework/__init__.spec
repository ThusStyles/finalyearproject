# -*- mode: python -*-

block_cipher = None


a = Analysis(['__init__.py'],
             pathex=['F:\\Users\\Theo\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages\\PyQt5\\Qt\\bin', 'F:\\Users\\Theo\\Desktop\\fyp\\Framework'],
             binaries=[],
             datas=[("F:\\Users\\Theo\\Desktop\\fyp\\Framework\\GUI\\Stylesheets\\default.qss", "GUI/Stylesheets"), ("F:\\Users\\Theo\\Desktop\\fyp\\Framework\\images", "images")],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='NeuralNet',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='NeuralNet')
