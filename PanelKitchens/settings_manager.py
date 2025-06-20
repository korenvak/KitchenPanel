import json
import os
from typing import Dict, Any


class SettingsManager:
    def __init__(self, settings_file="panel_settings.json"):
        self.settings_file = settings_file
        self.default_settings = {
            'company': {
                'name': 'Panel Kitchens',
                'logo': 'assets/logo.png',
                'phone': '072-393-3997',
                'email': 'info@panel-k.co.il',
                'address': 'הנגרים 1 (מתחם הורדוס), באר שבע',
                'website': 'https://panel-k.co.il',
            },
            'pdf': {
                'primary_color': '#d32f2f',
                'secondary_color': '#ff6f00',
                'font_regular': 'Heebo-Regular.ttf',
                'font_bold': 'Heebo-Bold.ttf',
                'watermark': True,
                'footer_text': 'כל הזכויות שמורות',
                'terms': [
                    "הצעת המחיר תקפה ל-14 ימים ממועד הפקתה.",
                    "ההצעה מיועדת ללקוח הספציפי בלבד ולא להעברה לחוץ.",
                    "המחירים עשויים להשתנות והחברה אינה אחראית לטעויות.",
                    "אישור ההצעה מהווה התחייבות לתשלום 10% מקדמה.",
                    "הלקוח מתחייב לפנות נקודות מים וחשמל בהתאם לתכניות.",
                    "אי עמידה בתנאים עלולה לגרור עיכובים וחריגות."
                ],
            },
            'ui': {
                'theme': 'light',
                'primary_color': '#d32f2f',
                'secondary_color': '#ff6f00',
                'language': 'he',
                'rtl': True,
                'animations': True,
            },
            'features': {
                'auto_backup': True,
                'backup_interval_days': 7,
                'save_drafts': True,
                'email_integration': False,
                'statistics': True,
                'customer_history': True,
            },
            'shortcuts': {
                'new_quote': 'Ctrl+N',
                'save_draft': 'Ctrl+S',
                'open_file': 'Ctrl+O',
                'print': 'Ctrl+P',
                'search': 'Ctrl+F',
            },
            'email': {
                'enabled': False,
                'server': 'smtp.gmail.com',
                'port': 587,
                'email': '',
                'password': '',
                'signature': '',
            }
        }

        self.settings = self.load_settings()

    def load_settings(self) -> Dict:
        """טעינת הגדרות"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return self.merge_settings(self.default_settings, loaded_settings)
            except:
                return self.default_settings.copy()
        return self.default_settings.copy()

    def merge_settings(self, default: Dict, loaded: Dict) -> Dict:
        """מיזוג הגדרות טעונות עם ברירת מחדל"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_settings(result[key], value)
            else:
                result[key] = value
        return result

    def save_settings(self):
        """שמירת הגדרות"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        קבלת ערך הגדרה לפי נתיב
        Example: settings.get('company.name')
        """
        keys = key_path.split('.')
        value = self.settings
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, key_path: str, value: Any):
        """
        הגדרת ערך לפי נתיב
        Example: settings.set('company.name', 'My Company')
        """
        keys = key_path.split('.')
        target = self.settings
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value
        self.save_settings()

    def get_company_info(self) -> Dict:
        """קבלת פרטי החברה"""
        return self.settings['company']

    def update_company_info(self, info: Dict):
        """עדכון פרטי החברה"""
        self.settings['company'].update(info)
        self.save_settings()

    def get_pdf_settings(self) -> Dict:
        """קבלת הגדרות PDF"""
        return self.settings['pdf']

    def update_pdf_settings(self, settings: Dict):
        """עדכון הגדרות PDF"""
        self.settings['pdf'].update(settings)
        self.save_settings()

    def get_ui_settings(self) -> Dict:
        """קבלת הגדרות ממשק"""
        return self.settings['ui']

    def update_ui_settings(self, settings: Dict):
        """עדכון הגדרות ממשק"""
        self.settings['ui'].update(settings)
        self.save_settings()

    def is_feature_enabled(self, feature: str) -> bool:
        """בדיקה אם פיצ'ר מופעל"""
        return self.settings['features'].get(feature, False)

    def toggle_feature(self, feature: str):
        """הפעלה/כיבוי פיצ'ר"""
        if feature in self.settings['features']:
            self.settings['features'][feature] = not self.settings['features'][feature]
            self.save_settings()

    def get_shortcuts(self) -> Dict[str, str]:
        """קבלת קיצורי מקלדת"""
        return self.settings['shortcuts']

    def update_shortcut(self, action: str, shortcut: str):
        """עדכון קיצור מקלדת"""
        if action in self.settings['shortcuts']:
            self.settings['shortcuts'][action] = shortcut
            self.save_settings()

    def reset_to_defaults(self):
        """איפוס להגדרות ברירת מחדל"""
        self.settings = self.default_settings.copy()
        self.save_settings()

    def export_settings(self, filepath: str):
        """ייצוא הגדרות לקובץ"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def import_settings(self, filepath: str) -> bool:
        """ייבוא הגדרות מקובץ"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported = json.load(f)
                self.settings = self.merge_settings(self.default_settings, imported)
                self.save_settings()
                return True
        except:
            return False