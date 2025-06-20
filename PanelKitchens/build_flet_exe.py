import os
import shutil
import subprocess
import sys


def clean_build_dirs():
    """ניקוי תיקיות build קודמות"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"מוחק {dir_name}...")
            shutil.rmtree(dir_name)


def create_requirements():
    """יצירת קובץ requirements.txt"""
    requirements = """flet>=0.21.0
pandas>=1.5.0
openpyxl>=3.0.0
reportlab>=3.6.0
pillow>=9.0.0
arabic-reshaper>=3.0.0
python-bidi>=0.4.2
"""

    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    print("נוצר קובץ requirements.txt")


def build_exe():
    """בניית ה-EXE באמצעות flet pack"""
    print("בונה את האפליקציה...")

    # flet pack command with all options
    cmd = [
        sys.executable, "-m", "flet", "pack",
        "main_flet_enhanced.py",
        "--name", "PanelKitchens",
        "--icon", "assets/White_Logo.ico",
        "--product-name", "Panel Kitchens - מערכת הצעות מחיר",
        "--product-version", "2.0.0",
        "--file-version", "2.0.0",
        "--copyright", "Copyright © 2025 Panel Kitchens",
        "--company-name", "Panel Kitchens",
        "--add-data", "assets;assets",
        "--add-data", "static;static",
        "--add-data", "catalog_loader.py;.",
        "--add-data", "pdf_generator.py;.",
        "--add-data", "products_view_flet.py;.",
        "--add-data", "utils;utils",
        "--hidden-import", "catalog_loader",
        "--hidden-import", "pdf_generator",
        "--hidden-import", "products_view_flet",
        "--hidden-import", "utils.helpers",
        "--hidden-import", "utils.rtl",
        "--hidden-import", "reportlab.lib.pagesizes",
        "--hidden-import", "reportlab.pdfgen.canvas",
        "--hidden-import", "reportlab.pdfbase.ttfonts",
        "--hidden-import", "reportlab.pdfbase.pdfmetrics",
        "--hidden-import", "reportlab.lib.utils",
        "--hidden-import", "reportlab.lib.units",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "PIL.ImageDraw",
        "--hidden-import", "arabic_reshaper",
        "--hidden-import", "bidi.algorithm",
        "--distpath", "dist",
        "--onefile",
    ]

    # Run the command
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ הבנייה הושלמה בהצלחה!")
        print(f"📁 הקובץ נמצא ב: dist/PanelKitchens.exe")

        # Get file size
        exe_path = "dist/PanelKitchens.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📊 גודל הקובץ: {size_mb:.1f} MB")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ שגיאה בבנייה: {e}")
        sys.exit(1)


def create_installer_script():
    """יצירת סקריפט Inno Setup להתקנה מקצועית"""
    inno_script = """[Setup]
AppName=Panel Kitchens - מערכת הצעות מחיר
AppVersion=2.0.0
AppPublisher=Panel Kitchens
AppPublisherURL=https://panel-k.co.il
DefaultDirName={autopf}\Panel Kitchens
DefaultGroupName=Panel Kitchens
UninstallDisplayIcon={app}\PanelKitchens.exe
OutputDir=installer
OutputBaseFilename=PanelKitchens_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableDirPage=no
DisableProgramGroupPage=no
SetupIconFile=assets\White_Logo.ico

[Languages]
Name: "hebrew"; MessagesFile: "compiler:Languages\Hebrew.isl"

[Files]
Source: "dist\PanelKitchens.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Panel Kitchens"; Filename: "{app}\PanelKitchens.exe"
Name: "{group}\הסר את Panel Kitchens"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Panel Kitchens"; Filename: "{app}\PanelKitchens.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "צור קיצור דרך על שולחן העבודה"; GroupDescription: "אפשרויות נוספות:"; Flags: unchecked

[Run]
Filename: "{app}\PanelKitchens.exe"; Description: "הפעל את Panel Kitchens"; Flags: nowait postinstall skipifsilent
"""

    with open('setup.iss', 'w', encoding='utf-8') as f:
        f.write(inno_script)
    print("\n📝 נוצר קובץ setup.iss להתקנה מקצועית")
    print("💡 כדי ליצור installer, התקן Inno Setup והרץ את setup.iss")


def main():
    print("🚀 מתחיל בניית Panel Kitchens EXE...")
    print("=" * 50)

    # Check if main file exists
    if not os.path.exists("main_flet_enhanced.py"):
        print("❌ הקובץ main_flet_enhanced.py לא נמצא!")
        sys.exit(1)

    # Clean previous builds
    clean_build_dirs()

    # Create requirements
    create_requirements()

    # Install flet with pyinstaller support
    print("\nמתקין תלויות...")
    subprocess.run([sys.executable, "-m", "pip", "install", "flet[pyinstaller]", "--upgrade"], check=True)

    # Build the exe
    build_exe()

    # Create installer script
    create_installer_script()

    print("\n✨ הסתיים! האפליקציה מוכנה להפצה")
    print("\nשלבים הבאים:")
    print("1. בדוק את הקובץ ב-dist/PanelKitchens.exe")
    print("2. אופציונלי: צור installer עם Inno Setup")
    print("3. שתף עם משתמשים!")

    # Open output folder
    if sys.platform == "win32":
        os.startfile("dist")


if __name__ == "__main__":
    main()