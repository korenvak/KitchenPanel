# file: panel_app/catalog_loader.py
import pandas as pd
from functools import lru_cache


@lru_cache(maxsize=32)
def load_catalog(file_path):
    """טוען קטלוג מקובץ Excel עם caching"""
    try:
        # קריאת הקובץ
        df = pd.read_excel(file_path, sheet_name='גיליון1', header=8, engine='openpyxl')
        df.columns = df.columns.str.strip()

        # שינוי שמות עמודות
        rename_dict = {
            "מס'": "מספר",
            'סה"כ': 'סהכ'
        }
        df.rename(columns=rename_dict, inplace=True)

        # חיפוש עמודת פריט
        for col in df.columns:
            if 'פריט' in col and col != 'הפריט':
                df.rename(columns={col: 'הפריט'}, inplace=True)
                break

        # הוספת עמודות
        df['כמות'] = 0
        df['קטגוריה'] = ''
        current_category = ''

        # זיהוי קטגוריות
        for idx in df.index:
            if pd.isna(df.at[idx, 'מחיר יחידה']) or df.at[idx, 'מחיר יחידה'] == '':
                # זו כנראה שורת קטגוריה
                for col in df.columns:
                    if pd.notna(df.at[idx, col]) and str(df.at[idx, col]).strip() != '':
                        current_category = str(df.at[idx, col]).strip()
                        break
            else:
                # זו שורת מוצר
                df.at[idx, 'קטגוריה'] = current_category

        # סינון רק שורות עם מחיר
        df = df[pd.notna(df['מחיר יחידה'])].copy()

        # המרת מחירים למספרים
        df['מחיר יחידה'] = pd.to_numeric(df['מחיר יחידה'], errors='coerce').fillna(0)

        # וידוא שעמודת הערות קיימת
        if 'הערות' not in df.columns:
            df['הערות'] = ''
        df['הערות'] = df['הערות'].fillna('')

        return df

    except Exception as e:
        print(f"שגיאה בטעינת הקובץ: {str(e)}")
        raise e