import flet as ft
from datetime import date
import os
import sys
import pandas as pd
import time

# Handle PyInstaller paths
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

if base_path not in sys.path:
    sys.path.insert(0, base_path)

# Import our existing modules
from catalog_loader import load_catalog
from pdf_generator import create_enhanced_pdf
from products_view_flet import create_products_view


class PanelKitchensApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.init_state()
        self.build_ui()

    def setup_page(self):
        """הגדרות בסיסיות של העמוד"""
        self.page.title = "Panel Kitchens - הצעות מחיר"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.rtl = True
        self.page.window_width = 1400
        self.page.window_height = 900
        self.page.window_min_width = 1200
        self.page.window_min_height = 700
        self.page.scroll = ft.ScrollMode.AUTO

        # אייקון לחלון
        if os.path.exists(os.path.join(base_path, 'assets', 'White_Logo.ico')):
            self.page.window_icon = os.path.join(base_path, 'assets', 'White_Logo.ico')

        # צבעי נושא מותאמים אישית
        self.page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary="#d32f2f",
                secondary="#ff6f00",
                surface="#f5f5f5",
                background="#ffffff",
                error="#f44336",
            ),
        )

        # Fonts
        self.page.fonts = {
            "Heebo": os.path.join(base_path, "assets", "Heebo-Regular.ttf"),
            "Heebo-Bold": os.path.join(base_path, "assets", "Heebo-Bold.ttf"),
        }
        self.page.theme = ft.Theme(font_family="Heebo")

    def init_state(self):
        """אתחול משתני state"""
        self.page.data = {
            'customer_data': {
                'name': '',
                'phone': '',
                'email': '',
                'address': '',
                'date': date.today(),
                'discount': 0.0,
                'contractor': False,
                'contractor_discount': 0.0,
            },
            'selected_items': [],
            'catalog_df': None,
            'demo1': None,
            'demo2': None,
            'form_fields': {},
            'loading': False,
        }

        # File pickers
        self.catalog_picker = ft.FilePicker(on_result=self.handle_catalog_picked)
        self.demo1_picker = ft.FilePicker(on_result=self.handle_demo1_picked)
        self.demo2_picker = ft.FilePicker(on_result=self.handle_demo2_picked)
        self.save_picker = ft.FilePicker(on_result=self.handle_save_pdf)

        self.page.overlay.extend([
            self.catalog_picker,
            self.demo1_picker,
            self.demo2_picker,
            self.save_picker,
        ])

    def build_ui(self):
        """בניית הממשק - גרסה מתוקנת עם גלילה נכונה"""
        # Progress bar
        self.progress_bar = ft.ProgressBar(
            visible=False,
            color="#d32f2f",
            bgcolor="#ffebee",
        )

        # Header - קבוע למעלה
        header = self.create_animated_header()

        # Main content area with tabs - זה החלק שיגלול
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            indicator_color="#d32f2f",
            label_color="#d32f2f",
            unselected_label_color="#666666",
            expand=1,
            tabs=[
                ft.Tab(
                    text="פרטי לקוח",
                    icon=ft.Icons.PERSON,
                    content=ft.Container(
                        content=ft.Column(
                            controls=[self.create_customer_form()],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        padding=20,
                    ),
                ),
                ft.Tab(
                    text="בחירת מוצרים",
                    icon=ft.Icons.SHOPPING_CART,
                    content=ft.Container(
                        content=self.create_catalog_section(),
                        padding=20,
                    ),
                ),
                ft.Tab(
                    text="יצירת הצעה",
                    icon=ft.Icons.DESCRIPTION,
                    content=ft.Container(
                        content=ft.Column(
                            controls=[self.create_pdf_section()],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        padding=20,
                    ),
                ),
            ],
            on_change=self.on_tab_change,
        )

        # Footer - קבוע למטה
        footer = self.create_footer()

        # Main layout
        self.page.add(
            ft.Column([
                self.progress_bar,
                header,
                ft.Container(
                    content=self.tabs,
                    expand=True,
                ),
                footer,
            ], expand=True, spacing=0)
        )

    def create_animated_header(self):
        """יצירת header עם אנימציה"""
        logo_path = os.path.join(base_path, 'assets', 'logo.png')
        if os.path.exists(logo_path):
            logo = ft.Image(
                src=logo_path,
                width=180,
                height=70,
                fit=ft.ImageFit.CONTAIN,
                animate_scale=ft.Animation(600, ft.AnimationCurve.BOUNCE_OUT),
            )
        else:
            logo = ft.Icon(
                ft.Icons.KITCHEN,
                size=60,
                color="#d32f2f",
                animate_scale=ft.Animation(600, ft.AnimationCurve.BOUNCE_OUT),
            )

        # Animate logo on hover
        def on_hover(e):
            e.control.scale = 1.1 if e.data == "true" else 1
            self.page.update()

        logo.on_hover = on_hover

        return ft.Container(
            content=ft.Row([
                logo,
                ft.Column([
                    ft.Text(
                        "מערכת הצעות מחיר",
                        size=36,
                        weight=ft.FontWeight.BOLD,
                        color="#d32f2f",
                        font_family="Heebo-Bold",
                        animate_opacity=ft.Animation(1000),
                    ),
                    ft.Text(
                        "Panel Kitchens - מטבחים באיכות גבוהה",
                        size=18,
                        color="#666666",
                        animate_opacity=ft.Animation(1500),
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER),
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=30,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=["#ffffff", "#ffebee"],
            ),
            border_radius=15,
            margin=ft.margin.only(bottom=20),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 5),
            ),
        )

    def create_customer_form(self):
        """טופס פרטי לקוח משופר"""
        # Text fields with enhanced styling
        name_field = self.create_styled_textfield(
            label="שם הלקוח",
            hint="הזן שם מלא",
            icon=ft.Icons.PERSON_OUTLINE,
            autofocus=True,
        )

        phone_field = self.create_styled_textfield(
            label="טלפון",
            hint="050-1234567",
            icon=ft.Icons.PHONE_OUTLINED,
            keyboard_type=ft.KeyboardType.PHONE,
        )

        email_field = self.create_styled_textfield(
            label='דוא"ל',
            hint="name@example.com",
            icon=ft.Icons.EMAIL_OUTLINED,
            keyboard_type=ft.KeyboardType.EMAIL,
        )

        # Date picker with custom styling
        date_button = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.CALENDAR_TODAY, size=20),
                ft.Text(f"תאריך: {self.page.data['customer_data']['date'].strftime('%d/%m/%Y')}"),
            ]),
            style=ft.ButtonStyle(
                color={ft.ControlState.DEFAULT: "#d32f2f"},
                bgcolor={ft.ControlState.DEFAULT: "#ffebee"},
                padding=20,
                animation_duration=300,
            ),
            on_click=lambda _: self.page.open(
                ft.DatePicker(
                    first_date=date(2020, 1, 1),
                    last_date=date(2030, 12, 31),
                    on_change=lambda e: self.update_date(e, date_button),
                )
            ),
        )

        discount_field = self.create_styled_textfield(
            label="אחוז הנחה",
            hint="0",
            suffix_text="%",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
            icon=ft.Icons.DISCOUNT_OUTLINED,
        )

        contractor_checkbox = ft.Checkbox(
            label="הנחת קבלן",
            value=False,
            active_color="#d32f2f",
            on_change=self.contractor_changed,
        )

        contractor_discount = self.create_styled_textfield(
            label="סכום הנחת קבלן (₪)",
            hint="0",
            width=250,
            keyboard_type=ft.KeyboardType.NUMBER,
            visible=False,
            icon=ft.Icons.MONEY_OFF,
        )

        address_field = self.create_styled_textfield(
            label="כתובת",
            hint="רחוב, מספר, עיר",
            multiline=True,
            min_lines=3,
            max_lines=3,
            icon=ft.Icons.LOCATION_ON_OUTLINED,
        )

        # Store references
        self.page.data['form_fields'] = {
            'name': name_field,
            'phone': phone_field,
            'email': email_field,
            'date': date_button,
            'discount': discount_field,
            'contractor': contractor_checkbox,
            'contractor_discount': contractor_discount,
            'address': address_field,
        }

        # Form validation indicator
        self.form_validation_text = ft.Text(
            "",
            size=14,
            color="#f44336",
            visible=False,
        )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.PERSON, size=30, color="#d32f2f"),
                    ft.Text("פרטי לקוח", size=28, weight=ft.FontWeight.BOLD),
                ]),
                ft.Divider(height=20, color="#e0e0e0"),
                ft.Row([
                    ft.Column([name_field, phone_field, email_field], expand=1, spacing=20),
                    ft.Column([date_button, discount_field, contractor_checkbox, contractor_discount], expand=1,
                              spacing=20),
                ]),
                address_field,
                self.form_validation_text,
            ], spacing=20),
            padding=30,
            bgcolor="#ffffff",
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

    def create_styled_textfield(self, label, hint, icon=None, **kwargs):
        """יצירת שדה טקסט מעוצב"""
        return ft.TextField(
            label=label,
            hint_text=hint,
            border_color="#e0e0e0",
            focused_border_color="#d32f2f",
            focused_border_width=2,
            text_size=16,
            content_padding=20,
            filled=True,
            fill_color="#fafafa",
            prefix_icon=icon,
            cursor_color="#d32f2f",
            selection_color="#ffebee",
            **kwargs,
        )

    def create_catalog_section(self):
        """סקציית בחירת קטלוג משופרת - עם גלילה מתוקנת"""
        # Upload area with animation
        self.upload_container = ft.Container(
            content=ft.Column([
                ft.Icon(
                    ft.Icons.CLOUD_UPLOAD,
                    size=80,
                    color="#d32f2f",
                    animate_scale=ft.Animation(2000, ft.AnimationCurve.EASE_IN_OUT),
                ),
                ft.Text(
                    "גרור קובץ קטלוג לכאן או לחץ לבחירה",
                    size=20,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Text(
                    "קובץ Excel עם רשימת המוצרים",
                    size=16,
                    color="#666666",
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#fff3e0", "#ffe0b2"],
            ),
            padding=60,
            border=ft.border.all(3, "#ff6f00"),
            border_radius=20,
            alignment=ft.alignment.center,
            height=250,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
            on_hover=self.on_upload_hover,
            on_click=lambda _: self.catalog_picker.pick_files(allowed_extensions=["xlsx", "xls"]),
        )

        # Products container - זה החלק שצריך לגלול
        self.products_container = ft.Container(
            visible=False,
            animate_opacity=ft.Animation(500),
            animate_scale=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
        )

        # Return scrollable column
        return ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SHOPPING_CART, size=30, color="#d32f2f"),
                ft.Text("בחירת מוצרים", size=28, weight=ft.FontWeight.BOLD),
            ]),
            ft.Divider(height=20, color="#e0e0e0"),
            self.upload_container,
            self.products_container,
        ], spacing=20, scroll=ft.ScrollMode.AUTO)

    def _on_generate_click(self, e):
        """Handler נקי שמוודא שהכפתור נקלט ואז מפעיל generate_pdf"""
        print("🔘 🔘 Button clicked — now calling generate_pdf")
        self.generate_pdf(e)

    def create_pdf_section(self):
        """סקציית יצירת PDF משופרת"""
        # Demo images upload
        demo1_container = self.create_image_upload_area(
            "הדמיה ראשית",
            "תמונת הדמיה של המטבח",
            self.demo1_picker,
            'demo1',
        )

        demo2_container = self.create_image_upload_area(
            "נקודות מים וחשמל",
            "תרשים טכני של המטבח",
            self.demo2_picker,
            'demo2',
        )

        # Generate button עם handler נקי
        generate_button = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.PICTURE_AS_PDF, size=24),
                ft.Text("צור הצעת מחיר", size=18, weight=ft.FontWeight.BOLD),
            ]),
            style=ft.ButtonStyle(
                color={ft.ControlState.DEFAULT: ft.Colors.WHITE},
                bgcolor={ft.ControlState.DEFAULT: "#d32f2f"},
                padding=25,
                animation_duration=300,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=self._on_generate_click,    # ← כאן
            width=300,
            height=60,
        )

        # Reset button
        reset_button = ft.OutlinedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.REFRESH, size=20),
                ft.Text("התחל מחדש", size=16),
            ]),
            style=ft.ButtonStyle(
                side={ft.ControlState.DEFAULT: ft.BorderSide(2, "#d32f2f")},
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=self.reset_form,
        )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.DESCRIPTION, size=30, color="#d32f2f"),
                    ft.Text("יצירת הצעת מחיר", size=28, weight=ft.FontWeight.BOLD),
                ]),
                ft.Divider(height=20, color="#e0e0e0"),
                ft.Text(
                    "הוסף תמונות הדמיה (אופציונלי)",
                    size=20,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Row([demo1_container, demo2_container], spacing=20),
                ft.Container(height=30),
                ft.Row(
                    [generate_button, reset_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
            ], spacing=20),
            padding=30,
            bgcolor="#ffffff",
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )


    def create_image_upload_area(self, title, subtitle, picker, image_key):
        """יצירת אזור העלאת תמונה"""
        container = ft.Container(
            content=ft.Column([
                ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                ft.Text(subtitle, size=12, color="#666666"),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ADD_PHOTO_ALTERNATE, size=50, color="#666666"),
                        ft.Text("לחץ להוספת תמונה", size=14, color="#666666"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    width=200,
                    height=150,
                    bgcolor="#f5f5f5",
                    border=ft.border.all(2, "#e0e0e0"),
                    border_radius=10,
                    alignment=ft.alignment.center,
                ),
            ], spacing=10),
            on_click=lambda _: picker.pick_files(
                allowed_extensions=["png", "jpg", "jpeg"],
                file_type=ft.FilePickerFileType.IMAGE,
            ),
        )

        setattr(self, f"{image_key}_container", container)
        return container

    def create_footer(self):
        """יצירת footer"""
        return ft.Container(
            content=ft.Row([
                ft.Text(
                    "Panel Kitchens © 2025",
                    size=14,
                    color="#999999",
                ),
                ft.Text("•", size=14, color="#999999"),
                ft.Text(
                    "מערכת הצעות מחיר",
                    size=14,
                    color="#999999",
                ),
                ft.Text("•", size=14, color="#999999"),
                ft.Icon(ft.Icons.PHONE, size=14, color="#999999"),
                ft.Text(
                    "072-393-3997",
                    size=14,
                    color="#999999",
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            padding=20,
            bgcolor="#f5f5f5",
            alignment=ft.alignment.center,
        )

    # Event handlers
    def on_upload_hover(self, e):
        """אפקט hover על אזור העלאה"""
        if e.data == "true":
            self.upload_container.scale = 1.02
            self.upload_container.elevation = 5
        else:
            self.upload_container.scale = 1
            self.upload_container.elevation = 0
        self.page.update()

    def contractor_changed(self, e):
        """שינוי סטטוס הנחת קבלן"""
        self.page.data['form_fields']['contractor_discount'].visible = e.control.value
        self.page.update()

    def update_date(self, e, button):
        """עדכון תאריך"""
        if e.control.value:
            self.page.data['customer_data']['date'] = e.control.value
            button.content.controls[1].value = f"תאריך: {e.control.value.strftime('%d/%m/%Y')}"
            self.page.update()

    def on_tab_change(self, e):
        """אנימציה בין טאבים"""
        # Can add validation or animation here
        pass

    def show_loading(self, show=True):
        """הצגת/הסתרת loading"""
        self.progress_bar.visible = show
        self.page.update()
        if show:
            time.sleep(0.1)  # Give UI time to update

    def handle_catalog_picked(self, e: ft.FilePickerResultEvent):
        """טיפול בקובץ קטלוג שנבחר"""
        if e.files:
            self.load_catalog(e.files[0].path)

    def load_catalog(self, file_path):
        """טעינת קטלוג עם loading animation"""
        self.show_loading(True)

        try:
            catalog_df = load_catalog(file_path)
            if catalog_df is not None:
                self.page.data['catalog_df'] = catalog_df
                self.show_products(catalog_df)
                self.show_success_message("הקטלוג נטען בהצלחה!")

                # Hide upload area with animation
                self.upload_container.visible = False
                self.page.update()
        except Exception as e:
            self.show_error_message(f"שגיאה בטעינת קטלוג: {str(e)}")
        finally:
            self.show_loading(False)

    def show_products(self, df):
        """הצגת מוצרים"""
        products_view = create_products_view(self.page, df)
        self.products_container.content = products_view
        self.products_container.visible = True
        self.page.update()

    def handle_demo1_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            print("📷 demo1 picked:", e.files[0].path)
            self.page.data['demo1'] = e.files[0].path
            self.update_image_preview(self.demo1_container, e.files[0].path)

    def handle_demo2_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            print("📷 demo2 picked:", e.files[0].path)
            self.page.data['demo2'] = e.files[0].path
            self.update_image_preview(self.demo2_container, e.files[0].path)

    def update_image_preview(self, container, image_path):
        """עדכון תצוגה מקדימה של תמונה"""
        container.content.controls[2] = ft.Container(
            content=ft.Stack([
                ft.Image(
                    src=image_path,
                    width=200,
                    height=150,
                    fit=ft.ImageFit.COVER,
                    border_radius=10,
                ),
                ft.Container(
                    content=ft.Icon(ft.Icons.CHECK_CIRCLE, color="white", size=30),
                    bgcolor="#4caf50",
                    border_radius=50,
                    padding=5,
                    right=10,
                    top=10,
                ),
            ]),
            width=200,
            height=150,
        )
        self.page.update()

    def generate_pdf(self, e):
        """יצירת PDF עם שמירה ופתיחה אוטומטית"""
        import os, re, traceback
        from datetime import date
        import pandas as pd

        # Debug: מציג את כל ה-state לפני הכל
       # print("🔘 generate_pdf invoked")
       # print("   • full page.data:", self.page.data)
       # print("   • form_fields:", self.page.data.get('form_fields'))
       # print("   • selected_items:", self.page.data.get('selected_items'))

        self.show_success_message("generate_pdf() called")
        self.show_loading(True)

        # איסוף שדות
       # print(">> collecting form fields...")
        form_fields = self.page.data.get('form_fields', {})
        customer_data = {
            'name': form_fields.get('name').value or '',
            'phone': form_fields.get('phone').value or '',
            'email': form_fields.get('email').value or '',
            'address': form_fields.get('address').value or '',
            'date': self.page.data.get('customer_data', {}).get('date'),
            'discount': float(form_fields.get('discount').value or 0),
            'contractor': form_fields.get('contractor').value or '',
            'contractor_discount': float(form_fields.get('contractor_discount').value or 0),
        }
        print(f">> customer_data collected: {customer_data!r}")

        # ולידציה
        ok = self.validate_form(customer_data)
        print(">> validate_form returned:", ok)
        if not ok:
            print(">> aborting after validate_form")
            self.show_loading(False)
            return

        # בדיקה של הפריטים הנבחרים
        items = self.page.data.get('selected_items')
        print(">> selected_items is:", items)
        if not items:
            print(">> aborting because no selected_items")
            self.show_error_message("יש לבחור מוצרים להצעה")
            self.show_loading(False)
            return

        try:
            # יצירת DataFrame
            print(">> creating DataFrame from selected_items...")
            selected_df = pd.DataFrame(items)
            print(f">> DataFrame created with {len(selected_df)} rows")

            # קריאת תמונות demo במידת הצורך
            demo1_data = demo2_data = None
            if self.page.data.get('demo1'):
                print(">> reading demo1 image from", self.page.data['demo1'])
                with open(self.page.data['demo1'], 'rb') as f:
                    demo1_data = f.read()
            if self.page.data.get('demo2'):
                print(">> reading demo2 image from", self.page.data['demo2'])
                with open(self.page.data['demo2'], 'rb') as f:
                    demo2_data = f.read()

            # יצירת PDF
            print(">> calling create_enhanced_pdf...")
            pdf_buffer = create_enhanced_pdf(customer_data, selected_df, demo1_data, demo2_data)
            pdf_bytes = pdf_buffer.getvalue()
            print(f">> PDF buffer length: {len(pdf_bytes)} bytes")
            print(">> PDF header:", pdf_bytes[:4], "…", "PDF trailer:", pdf_bytes[-6:])
            if not pdf_bytes.startswith(b'%PDF'):
                print("‼️ Warning: buffer does not start with '%PDF'")

            # שמירת הבופר ב-page.data
            self.page.data['generated_pdf'] = pdf_bytes

            # שמירת קובץ ה-PDF לדיסק
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.isdir(desktop):
                desktop = os.path.expanduser("~")
            print(f">> target save path: {desktop}")

            safe_name = re.sub(r'[\\/:*?"<>|]', '_', customer_data['name']) or 'לקוח'
            filename = f"הצעת_מחיר_{safe_name}_{date.today().strftime('%Y%m%d')}.pdf"
            save_path = os.path.join(desktop, filename)

            print(f">> writing PDF to: {save_path}")
            with open(save_path, 'wb') as f:
                f.write(pdf_bytes)
            print(f">> PDF saved: exists? {os.path.exists(save_path)}")
            self.show_success_message(f"PDF saved to {save_path}")

            self.show_loading(False)
            print(">> before show_pdf_success_dialog")
            self.show_pdf_success_dialog(save_path)
            print(">> after show_pdf_success_dialog")

        except Exception as ex:
            print("‼️ exception during PDF generation:", ex)
            traceback.print_exc()
            self.show_loading(False)
            self.show_error_message(f"שגיאה ביצירת PDF: {ex}")

    def show_pdf_success_dialog(self, file_path):
        print("✅ show_pdf_success_dialog() called with:", file_path)

        try:
            def close_dialog(e):
                print("🟨 dialog closed")
                self.page.dialog.open = False
                self.page.update()

            def open_pdf(e):
                print("🟩 trying to open PDF:", file_path)
                import subprocess, platform
                try:
                    if platform.system() == 'Windows':
                        os.startfile(file_path)
                    elif platform.system() == 'Darwin':
                        subprocess.call(['open', file_path])
                    else:
                        subprocess.call(['xdg-open', file_path])
                except Exception as ex:
                    print(f"❌ error opening file: {ex}")
                    self.show_error_message(f"שגיאה בפתיחת הקובץ: {str(ex)}")
                close_dialog(e)

            def open_folder(e):
                folder = os.path.dirname(file_path)
                print("🟦 trying to open folder:", folder)
                import subprocess, platform
                try:
                    if platform.system() == 'Windows':
                        subprocess.Popen(f'explorer /select,"{file_path}"')
                    elif platform.system() == 'Darwin':
                        subprocess.call(['open', '-R', file_path])
                    else:
                        subprocess.call(['xdg-open', folder])
                except Exception as ex:
                    print(f"❌ error opening folder: {ex}")
                    self.show_error_message(f"שגיאה בפתיחת התיקייה: {str(ex)}")
                close_dialog(e)

            def save_as(e):
                print("💾 save_as clicked")
                self.save_picker.save_file(
                    allowed_extensions=["pdf"],
                    file_name=os.path.basename(file_path),
                )

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color="#4caf50", size=30),
                    ft.Text("ההצעה נוצרה בהצלחה!", size=20),
                ]),
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("הקובץ נשמר ב:", size=16),
                        ft.Text(file_path, size=14, weight=ft.FontWeight.BOLD, selectable=True),
                        ft.Container(height=10),
                        ft.Text("מה תרצה לעשות?", size=16),
                    ], spacing=5),
                    width=500,
                ),
                actions=[
                    ft.TextButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PICTURE_AS_PDF, size=18),
                            ft.Text("פתח את ה-PDF"),
                        ]),
                        on_click=open_pdf,
                    ),
                    ft.TextButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.FOLDER_OPEN, size=18),
                            ft.Text("פתח תיקייה"),
                        ]),
                        on_click=open_folder,
                    ),
                    ft.TextButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.SAVE_AS, size=18),
                            ft.Text("שמור בשם"),
                        ]),
                        on_click=save_as,
                    ),
                    ft.TextButton("סגור", on_click=close_dialog),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            self.page.dialog = dlg
            dlg.open = True
            self.page.update()
            print("✅ Dialog shown successfully")

        except Exception as ex:
            print(f"❌ Error showing dialog: {ex}")
            self.show_error_message(f"שגיאה בהצגת חלון הצלחה: {str(ex)}")

    def handle_save_pdf(self, e: ft.FilePickerResultEvent):
        """שמירה של קובץ ה-PDF שנוצר"""
        if e.path and self.page.data.get('generated_pdf'):
            try:
                with open(e.path, 'wb') as f:
                    f.write(self.page.data['generated_pdf'])
                self.show_success_message("הקובץ נשמר בהצלחה")
            except Exception as ex:
                self.show_error_message(f"שגיאה בשמירת הקובץ: {str(ex)}")

    def validate_form(self, customer_data):
        """בדיקת תקינות הטופס"""
        errors = []

        if not customer_data['name'].strip():
            errors.append("חובה להזין שם לקוח")

        if not customer_data['phone'].strip():
            errors.append("חובה להזין מספר טלפון")

        if errors:
            self.form_validation_text.value = " • ".join(errors)
            self.form_validation_text.visible = True
            self.page.update()
            return False

        self.form_validation_text.visible = False
        self.page.update()
        return True

    def reset_form(self, e):
        """איפוס הטופס"""

        def close_reset_dialog(e):
            self.page.dialog.open = False
            self.page.update()

        def perform_reset_action(e):
            self.perform_reset()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("איפוס הטופס"),
            content=ft.Text("האם אתה בטוח שברצונך לאפס את כל הנתונים?"),
            actions=[
                ft.TextButton("ביטול", on_click=close_reset_dialog),
                ft.ElevatedButton(
                    "אפס",
                    color=ft.Colors.WHITE,
                    bgcolor="#f44336",
                    on_click=perform_reset_action,
                ),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def close_dialog(self):
        """סגירת דיאלוג"""
        self.page.dialog.open = False
        self.page.update()

    def perform_reset(self):
        """ביצוע איפוס"""
        # Reset form fields
        for field_name, field in self.page.data['form_fields'].items():
            if hasattr(field, 'value'):
                if field_name == 'contractor':
                    field.value = False
                elif field_name == 'date':
                    field.content.controls[1].value = f"תאריך: {date.today().strftime('%d/%m/%Y')}"
                else:
                    field.value = ""

        # Reset state
        self.page.data['selected_items'] = []
        self.page.data['catalog_df'] = None
        self.page.data['demo1'] = None
        self.page.data['demo2'] = None

        # Reset UI
        self.products_container.visible = False
        self.upload_container.visible = True
        self.tabs.selected_index = 0

        # Reset image previews
        if hasattr(self, 'demo1_container'):
            self.demo1_container.content.controls[2] = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ADD_PHOTO_ALTERNATE, size=50, color="#666666"),
                    ft.Text("לחץ להוספת תמונה", size=14, color="#666666"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                width=200,
                height=150,
                bgcolor="#f5f5f5",
                border=ft.border.all(2, "#e0e0e0"),
                border_radius=10,
                alignment=ft.alignment.center,
            )

        if hasattr(self, 'demo2_container'):
            self.demo2_container.content.controls[2] = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ADD_PHOTO_ALTERNATE, size=50, color="#666666"),
                    ft.Text("לחץ להוספת תמונה", size=14, color="#666666"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                width=200,
                height=150,
                bgcolor="#f5f5f5",
                border=ft.border.all(2, "#e0e0e0"),
                border_radius=10,
                alignment=ft.alignment.center,
            )

        self.close_dialog()
        self.show_success_message("הטופס אופס בהצלחה")

    def show_success_message(self, message):
        """הצגת הודעת הצלחה"""
        sb = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE, size=20),
                ft.Text(message, color=ft.Colors.WHITE),
            ]),
            bgcolor="#4caf50",
            duration=3000,
        )
        self.page.snack_bar = sb
        sb.open = True
        self.page.update()

    def show_error_message(self, message):
        """הצגת הודעת שגיאה"""
        sb = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.ERROR, color=ft.Colors.WHITE, size=20),
                ft.Text(message, color=ft.Colors.WHITE),
            ]),
            bgcolor="#f44336",
            duration=4000,
        )
        self.page.snack_bar = sb
        sb.open = True
        self.page.update()


def main(page: ft.Page):
    """נקודת כניסה ראשית"""
    app = PanelKitchensApp(page)


if __name__ == "__main__":
    # Run the app
    ft.app(
        target=main,
        assets_dir="assets",
    )