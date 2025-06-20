import flet as ft
import pandas as pd


def create_products_view(page: ft.Page, catalog_df: pd.DataFrame):
    """יוצר את תצוגת המוצרים עם אפשרות בחירת כמויות - עיצוב משופר"""

    # Dictionary to store quantity controls
    quantity_controls = {}
    selected_items = []

    def update_quantity(index, change):
        """מעדכן כמות של מוצר עם אנימציה"""
        current = int(quantity_controls[index]['text'].value or 0)
        new_value = max(0, current + change)
        quantity_controls[index]['text'].value = str(new_value)

        # Update total with animation
        total_control = quantity_controls[index]['total']
        total_control.value = calculate_item_total(index, new_value)

        # Highlight effect
        if new_value > 0:
            quantity_controls[index]['container'].bgcolor = "#e3f2fd"
            quantity_controls[index]['container'].border = ft.border.all(2, "#2196f3")
        else:
            quantity_controls[index]['container'].bgcolor = "#fafafa"
            quantity_controls[index]['container'].border = ft.border.all(1, "#e0e0e0")

        update_summary()
        page.update()

    def calculate_item_total(index, quantity):
        """מחשב סה\"כ למוצר"""
        if quantity == 0:
            return ""
        price = catalog_df.iloc[index]['מחיר יחידה']
        if pd.notna(price) and price != 0:
            total = quantity * price
            return f"₪{total:,.0f}"
        return "לפי מידה"

    def update_summary():
        """מעדכן את סיכום ההזמנה עם אנימציה"""
        selected_items.clear()
        subtotal = 0
        items_count = 0

        for idx, controls in quantity_controls.items():
            qty = int(controls['text'].value or 0)
            if qty > 0:
                items_count += 1
                row = catalog_df.iloc[idx].copy()
                row['כמות'] = qty
                price = row['מחיר יחידה']
                if pd.notna(price) and price != 0:
                    row['סהכ'] = qty * price
                    subtotal += row['סהכ']
                else:
                    row['סהכ'] = 0
                selected_items.append(row)

        # Update page data
        page.data['selected_items'] = selected_items

        # Update summary display with animation
        if subtotal > 0:
            # Get discount from form if available
            discount_pct = 0
            if 'form_fields' in page.data and 'discount' in page.data['form_fields']:
                discount_field = page.data['form_fields']['discount']
                if hasattr(discount_field, 'value'):
                    discount_pct = float(discount_field.value or 0)

            vat = subtotal * 0.17
            discount = (subtotal + vat) * (discount_pct / 100)
            total = subtotal + vat - discount

            summary_content.controls = [
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.SHOPPING_CART, size=24, color="#2196f3"),
                        ft.Text(f"נבחרו {items_count} פריטים", size=16, weight=ft.FontWeight.W_500),
                    ]),
                    padding=10,
                ),
                ft.Divider(thickness=1),
                create_summary_row("סכום ביניים:", f"₪{subtotal:,.2f}"),
                create_summary_row("מע\"מ (17%):", f"₪{vat:,.2f}", color="#666666"),
                create_summary_row(f"הנחה ({discount_pct}%):", f"-₪{discount:,.2f}",
                                   color="#4caf50") if discount > 0 else ft.Container(),
                ft.Divider(thickness=2, color="#d32f2f"),
                create_summary_row(
                    "סה\"כ לתשלום:",
                    f"₪{total:,.2f}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color="#d32f2f"
                ),
            ]
            summary_container.visible = True
            summary_container.scale = 0.95
            page.update()
            summary_container.scale = 1
        else:
            summary_container.visible = False

        page.update()

    def create_summary_row(label, value, size=18, weight=ft.FontWeight.NORMAL, color="#000000"):
        """יצירת שורת סיכום מעוצבת"""
        return ft.Container(
            content=ft.Row([
                ft.Text(label, size=size, weight=weight),
                ft.Text(value, size=size, weight=weight, color=color),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
        )

    # Search functionality
    search_field = ft.TextField(
        label="חיפוש מוצר",
        hint_text="הקלד שם מוצר...",
        prefix_icon=ft.icons.SEARCH,
        border_radius=10,
        filled=True,
        fill_color="#f5f5f5",
        on_change=lambda e: filter_products(e.control.value),
        width=400,
    )

    def filter_products(search_term):
        """סינון מוצרים לפי חיפוש"""
        search_term = search_term.lower()
        for idx, controls in quantity_controls.items():
            product_name = catalog_df.iloc[idx]['הפריט'].lower()
            if search_term in product_name:
                controls['container'].visible = True
            else:
                controls['container'].visible = False
        page.update()

    # Main container for products
    products_column = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=15,
        height=500,
    )

    # Group products by category
    categories = catalog_df['קטגוריה'].unique()

    for category in categories:
        if category:
            # Category header with icon
            category_icon = get_category_icon(category)
            category_header = ft.Container(
                content=ft.Row([
                    ft.Icon(category_icon, size=24, color=ft.colors.WHITE),
                    ft.Text(
                        category,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.WHITE,
                    ),
                ]),
                gradient=ft.LinearGradient(
                    begin=ft.alignment.center_left,
                    end=ft.alignment.center_right,
                    colors=["#d32f2f", "#ff6f00"],
                ),
                padding=15,
                border_radius=10,
                margin=ft.margin.only(top=20, bottom=10),
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=5,
                    color=ft.colors.with_opacity(0.2, ft.colors.BLACK),
                    offset=ft.Offset(0, 2),
                ),
            )
            products_column.controls.append(category_header)

        # Products in category
        category_df = catalog_df[catalog_df['קטגוריה'] == category]

        for idx in category_df.index:
            row = catalog_df.loc[idx]

            # Product container with hover effect
            product_container = ft.Container(
                animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
                on_hover=lambda e, i=idx: on_product_hover(e, i),
            )

            # Quantity controls with better styling
            qty_text = ft.TextField(
                value="0",
                width=70,
                text_align=ft.TextAlign.CENTER,
                keyboard_type=ft.KeyboardType.NUMBER,
                border_radius=5,
                filled=True,
                fill_color="#ffffff",
                text_size=16,
                on_change=lambda e, i=idx: update_summary(),
            )

            minus_btn = ft.IconButton(
                icon=ft.icons.REMOVE_CIRCLE_OUTLINE,
                icon_color="#d32f2f",
                icon_size=28,
                on_click=lambda e, i=idx: update_quantity(i, -1),
                tooltip="הפחת כמות",
            )

            plus_btn = ft.IconButton(
                icon=ft.icons.ADD_CIRCLE_OUTLINE,
                icon_color="#4caf50",
                icon_size=28,
                on_click=lambda e, i=idx: update_quantity(i, 1),
                tooltip="הוסף כמות",
            )

            # Price display with styling
            price = row['מחיר יחידה']
            if pd.notna(price) and price != 0:
                price_display = ft.Container(
                    content=ft.Text(
                        f"₪{price:,.0f}",
                        size=16,
                        weight=ft.FontWeight.W_500,
                    ),
                    bgcolor="#e8f5e9",
                    padding=10,
                    border_radius=5,
                )
            else:
                price_display = ft.Container(
                    content=ft.Text(
                        "לפי מידה",
                        size=14,
                        italic=True,
                        color="#666666",
                    ),
                    bgcolor="#f5f5f5",
                    padding=10,
                    border_radius=5,
                )

            # Total display
            total_text = ft.Text(
                "",
                size=18,
                weight=ft.FontWeight.BOLD,
                color="#d32f2f",
            )

            # Store controls
            quantity_controls[idx] = {
                'text': qty_text,
                'total': total_text,
                'container': product_container,
            }

            # Product row layout
            product_content = ft.Row([
                # Product info (60% width)
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            row['הפריט'],
                            size=18,
                            weight=ft.FontWeight.W_500,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(
                            row['הערות'] if pd.notna(row['הערות']) and row['הערות'] else "",
                            size=14,
                            color="#666666",
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ) if pd.notna(row['הערות']) and row['הערות'] else ft.Container(),
                    ], spacing=5),
                    expand=6,
                    padding=ft.padding.only(right=20),
                ),
                # Price (15% width)
                ft.Container(
                    content=price_display,
                    expand=2,
                    alignment=ft.alignment.center,
                ),
                # Quantity controls (15% width)
                ft.Container(
                    content=ft.Row([
                        minus_btn,
                        qty_text,
                        plus_btn,
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                    expand=2,
                ),
                # Total (10% width)
                ft.Container(
                    content=total_text,
                    expand=1,
                    alignment=ft.alignment.center,
                ),
            ], alignment=ft.MainAxisAlignment.START)

            # Set container content
            product_container.content = product_content
            product_container.padding = 15
            product_container.border_radius = 10
            product_container.bgcolor = "#fafafa"
            product_container.border = ft.border.all(1, "#e0e0e0")

            products_column.controls.append(product_container)

    def on_product_hover(e, idx):
        """אפקט hover על מוצר"""
        container = quantity_controls[idx]['container']
        if e.data == "true":
            container.elevation = 3
            container.scale = 1.01
        else:
            container.elevation = 0
            container.scale = 1
        page.update()

    # Summary section with modern design
    summary_content = ft.Column(spacing=10)

    summary_container = ft.Container(
        content=summary_content,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=["#ffffff", "#f5f5f5"],
        ),
        padding=20,
        border_radius=15,
        border=ft.border.all(2, "#d32f2f"),
        margin=ft.margin.only(top=20),
        visible=False,
        animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.colors.with_opacity(0.1, ft.colors.BLACK),
            offset=ft.Offset(0, 5),
        ),
    )

    # Header row with column titles
    header_row = ft.Container(
        content=ft.Row([
            ft.Text("מוצר", expand=6, weight=ft.FontWeight.BOLD, size=16),
            ft.Text("מחיר", expand=2, weight=ft.FontWeight.BOLD, size=16, text_align=ft.TextAlign.CENTER),
            ft.Text("כמות", expand=2, weight=ft.FontWeight.BOLD, size=16, text_align=ft.TextAlign.CENTER),
            ft.Text("סה\"כ", expand=1, weight=ft.FontWeight.BOLD, size=16, text_align=ft.TextAlign.CENTER),
        ]),
        padding=ft.padding.symmetric(horizontal=15, vertical=10),
        bgcolor="#f5f5f5",
        border_radius=10,
    )

    # Main layout
    return ft.Container(
        content=ft.Column([
            search_field,
            header_row,
            ft.Divider(thickness=2, color="#e0e0e0"),
            products_column,
            summary_container,
        ], spacing=10),
        padding=20,
    )


def get_category_icon(category):
    """החזרת אייקון מתאים לקטגוריה"""
    # Map categories to icons - customize based on your categories
    icon_map = {
        "מטבח": ft.icons.KITCHEN,
        "ארונות": ft.icons.DOOR_SLIDING,
        "משטחים": ft.icons.COUNTERTOPS,
        "אביזרים": ft.icons.BUILD,
        "כיורים": ft.icons.WASH,
        "ברזים": ft.icons.WATER_DROP,
    }

    # Search for matching keyword in category
    for keyword, icon in icon_map.items():
        if keyword in category:
            return icon

    # Default icon
    return ft.icons.CATEGORY