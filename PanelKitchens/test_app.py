import os
import sys
import traceback
from datetime import datetime


def test_imports():
    """בדיקת כל ה-imports הנדרשים"""
    print("🔍 בודק imports...")

    required_imports = [
        "flet",
        "pandas",
        "openpyxl",
        "reportlab",
        "PIL",
        "arabic_reshaper",
        "bidi",
    ]

    missing = []
    for module in required_imports:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - חסר!")
            missing.append(module)

    if missing:
        print(f"\n❌ חסרים מודולים: {', '.join(missing)}")
        print("הרץ: pip install " + " ".join(missing))
        return False

    print("✅ כל המודולים קיימים")
    return True


def test_files():
    """בדיקת קבצים נדרשים"""
    print("\n🔍 בודק קבצים...")

    required_files = [
        "main_flet_enhanced.py",
        "catalog_loader.py",
        "pdf_generator.py",
        "products_view_flet.py",
        "utils/helpers.py",
        "utils/rtl.py",
        "assets/logo.png",
        "assets/White_Logo.ico",
        "assets/Heebo-Regular.ttf",
    ]

    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - חסר!")
            missing.append(file)

    if missing:
        print(f"\n❌ חסרים קבצים: {len(missing)}")
        return False

    print("✅ כל הקבצים קיימים")
    return True


def test_app_launch():
    """בדיקת הרצת האפליקציה"""
    print("\n🔍 בודק הרצת אפליקציה...")

    try:
        import flet as ft
        from main_flet_enhanced import PanelKitchensApp

        # Test basic initialization
        test_passed = True

        def test_page(page: ft.Page):
            nonlocal test_passed
            try:
                app = PanelKitchensApp(page)
                print("✅ האפליקציה נטענה בהצלחה")
                page.window.close()
            except Exception as e:
                print(f"❌ שגיאה בטעינת האפליקציה: {e}")
                traceback.print_exc()
                test_passed = False
                page.window.close()

        # Run quick test
        ft.app(target=test_page, view=ft.AppView.FLET_APP_HIDDEN)

        return test_passed

    except Exception as e:
        print(f"❌ שגיאה: {e}")
        traceback.print_exc()
        return False


def test_catalog_loading():
    """בדיקת טעינת קטלוג"""
    print("\n🔍 בודק טעינת קטלוג...")

    try:
        from catalog_loader import load_catalog
        print("✅ מודול טעינת קטלוג זמין")
        return True
    except Exception as e:
        print(f"❌ שגיאה בטעינת מודול: {e}")
        return False


def test_pdf_generation():
    """בדיקת יצירת PDF"""
    print("\n🔍 בודק יצירת PDF...")

    try:
        from pdf_generator import create_enhanced_pdf
        import pandas as pd
        from datetime import date

        # Create test data
        customer_data = {
            'name': 'בדיקה',
            'phone': '050-1234567',
            'email': 'test@test.com',
            'address': 'רחוב הבדיקה 1',
            'date': date.today(),
            'discount': 10.0,
            'contractor': False,
            'contractor_discount': 0.0,
        }

        items_df = pd.DataFrame([
            {'הפריט': 'מוצר בדיקה', 'כמות': 2, 'מחיר יחידה': 100, 'סהכ': 200, 'הערות': '', 'קטגוריה': 'בדיקה'}
        ])

        # Try to generate PDF
        pdf_buffer = create_enhanced_pdf(customer_data, items_df)

        if pdf_buffer:
            print("✅ יצירת PDF עובדת")
            return True
        else:
            print("❌ נכשל ביצירת PDF")
            return False

    except Exception as e:
        print(f"❌ שגיאה ביצירת PDF: {e}")
        traceback.print_exc()
        return False


def create_test_report():
    """יצירת דוח בדיקה"""
    report_name = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(report_name, 'w', encoding='utf-8') as f:
        f.write("דוח בדיקת Panel Kitchens\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"תאריך: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Python version: {sys.version}\n")
        f.write(f"Platform: {sys.platform}\n\n")

        # Run all tests and write results
        tests = [
            ("Imports", test_imports),
            ("Files", test_files),
            ("App Launch", test_app_launch),
            ("Catalog Loading", test_catalog_loading),
            ("PDF Generation", test_pdf_generation),
        ]

        all_passed = True
        for test_name, test_func in tests:
            f.write(f"\n{test_name}:\n")
            print(f"\n{'=' * 50}")
            print(f"מריץ בדיקת {test_name}...")

            passed = test_func()
            all_passed &= passed

            f.write(f"Result: {'PASSED' if passed else 'FAILED'}\n")

        f.write(f"\n\nסיכום: {'כל הבדיקות עברו בהצלחה!' if all_passed else 'חלק מהבדיקות נכשלו'}\n")

    print(f"\n📄 דוח בדיקה נשמר ב: {report_name}")
    return all_passed


def main():
    print("🧪 Panel Kitchens - בדיקת מערכת")
    print("=" * 50)

    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Run tests and create report
    all_passed = create_test_report()

    if all_passed:
        print("\n✅ המערכת מוכנה לבנייה!")
        print("הרץ: python build_flet_exe.py")
    else:
        print("\n❌ יש לתקן את הבעיות לפני הבנייה")
        print("בדוק את דוח הבדיקה לפרטים")

    input("\nלחץ Enter לסיום...")


if __name__ == "__main__":
    main()