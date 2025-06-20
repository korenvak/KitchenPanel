import os
import json
from datetime import datetime
import flet as ft


class DashboardView:
    def __init__(self, page: ft.Page, on_action_selected):
        self.page = page
        self.on_action_selected = on_action_selected
        self.stats_file = "panel_stats.json"
        self.stats = {}
        self.load_statistics()

    def load_statistics(self):
        """Load or initialize statistics from a local JSON file."""
        if os.path.exists(self.stats_file):
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                self.stats = json.load(f)
        else:
            self.stats = {
                'total_quotes': 0,
                'monthly_quotes': {},
                'this_month': 0,
                'last_customers': [],
                'popular_products': {},
                'total_revenue': 0
            }

    def save_statistics(self):
        """Save current statistics to the JSON file."""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)

    def get_daily_tip(self) -> str:
        """Return a daily tip in Hebrew."""
        tips = [
            "💡 אתה יכול לשמור טיוטות של הצעות מחיר ולחזור אליהן מאוחר יותר",
            "⌨️ השתמש בקיצורי מקלדת: Ctrl+N להצעה חדשה, Ctrl+S לשמירה",
            "📊 בדוק את הסטטיסטיקות שלך כדי לראות אילו מוצרים הכי פופולריים",
            "📧 ניתן לשלוח הצעות ישירות במייל ללקוחות",
            "🎨 התאם את העיצוב של ההצעות שלך בהגדרות",
        ]
        day_index = datetime.now().day % len(tips)
        return tips[day_index]

    def create_action_card(self, action: dict) -> ft.Container:
        """Create a clickable action card."""
        def on_click(e):
            self.on_action_selected(action['action'])

        return ft.Container(
            content=ft.Column([
                ft.Icon(action['icon'], size=48, color=action['color']),
                ft.Text(action['title'], size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text(action['subtitle'], size=14, color="#666666", text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            width=200,
            height=180,
            padding=20,
            bgcolor="#ffffff",
            border_radius=15,
            on_click=on_click,
            on_hover=self.on_card_hover,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=5,
                                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK), offset=ft.Offset(0, 2)),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        )

    def create_stat_card(self, title: str, value: str, icon: str, color: str) -> ft.Container:
        """Create a statistic summary card."""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, size=32, color=ft.Colors.WHITE),
                    bgcolor=color,
                    padding=15,
                    border_radius=10,
                ),
                ft.Column([
                    ft.Text(title, size=14, color="#666666"),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
                ], spacing=5),
            ], spacing=15),
            padding=20,
            bgcolor="#ffffff",
            border_radius=10,
            width=250,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=3,
                                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK), offset=ft.Offset(0, 1)),
        )

    def create_recent_activity(self) -> ft.Container:
        """Create a panel showing the last 5 quotes."""
        activities = []
        recent_quotes = self.stats.get('recent_quotes', [])

        if not recent_quotes:
            # Fallback mock data
            recent_quotes = [
                {"customer": "דוד כהן", "date": "20/06/2025", "amount": "₪12,500"},
                {"customer": "שרה לוי", "date": "19/06/2025", "amount": "₪8,300"},
                {"customer": "משה אברהם", "date": "18/06/2025", "amount": "₪15,200"},
            ]

        for quote in recent_quotes[:5]:
            activities.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DESCRIPTION),
                    title=ft.Text(f"הצעה ל{quote['customer']}"),
                    subtitle=ft.Text(quote['date']),
                    trailing=ft.Text(quote['amount'], weight=ft.FontWeight.BOLD),
                )
            )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.HISTORY, color="#2196f3"),
                    ft.Text("פעילות אחרונה", size=18, weight=ft.FontWeight.BOLD),
                ]),
                ft.Column(activities) if activities else ft.Text("אין פעילות אחרונה", color="#666666"),
            ], spacing=10),
            padding=20,
            bgcolor="#ffffff",
            border_radius=10,
            width=self.page.window_width - 100,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=3,
                                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK), offset=ft.Offset(0, 1)),
        )

    def on_card_hover(self, e):
        """Hover effect for action cards."""
        if e.data == "true":
            e.control.scale = 1.05
            e.control.elevation = 8
        else:
            e.control.scale = 1.0
            e.control.elevation = 2
        self.page.update()

    def update_statistics(self, quote_data: dict):
        """Update statistics after creating a new quote and save."""
        self.stats['total_quotes'] += 1
        current_month = datetime.now().strftime("%Y-%m")
        self.stats['monthly_quotes'].setdefault(current_month, 0)
        self.stats['monthly_quotes'][current_month] += 1
        self.stats['this_month'] = self.stats['monthly_quotes'][current_month]

        # Update last customers list
        name = quote_data.get('customer_name')
        if name and name not in self.stats['last_customers']:
            self.stats['last_customers'].append(name)
            if len(self.stats['last_customers']) > 100:
                self.stats['last_customers'].pop(0)

        # Update revenue and products
        self.stats['total_revenue'] += quote_data.get('total_amount', 0)
        for item in quote_data.get('items', []):
            pname = item['name']
            self.stats['popular_products'].setdefault(pname, 0)
            self.stats['popular_products'][pname] += item.get('quantity', 0)

        # Store recent quotes for UI
        self.stats['recent_quotes'] = [
            {'customer': name, 'date': datetime.now().strftime('%d/%m/%Y'), 'amount': f"₪{quote_data.get('total_amount', 0):,}"}
        ] + self.stats.get('recent_quotes', [])
        self.stats['recent_quotes'] = self.stats['recent_quotes'][:5]

        self.save_statistics()

    def create_dashboard(self) -> ft.Column:
        """Assemble all components into the dashboard layout."""
        # Actions
        actions = [
            {'icon': ft.Icons.ADD_CIRCLE, 'title': 'הצעה חדשה', 'subtitle': 'צור הצעת מחיר חדשה', 'color': '#4caf50', 'action': 'new_quote'},
            {'icon': ft.Icons.HISTORY, 'title': 'הצעות קודמות', 'subtitle': 'צפה בהצעות שנוצרו', 'color': '#2196f3', 'action': 'history'},
            {'icon': ft.Icons.PEOPLE, 'title': 'לקוחות', 'subtitle': 'נהל רשימת לקוחות', 'color': '#ff9800', 'action': 'customers'},
            {'icon': ft.Icons.ANALYTICS, 'title': 'סטטיסטיקות', 'subtitle': 'נתונים וגרפים', 'color': '#9c27b0', 'action': 'stats'},
        ]
        action_cards = ft.Row(controls=[self.create_action_card(a) for a in actions], spacing=20, wrap=True,
                              alignment=ft.MainAxisAlignment.CENTER)

        # Stats summary
        stats_cards = ft.Row([
            self.create_stat_card("הצעות החודש", str(self.stats.get('this_month', 0)), ft.Icons.CALENDAR_MONTH, "#4caf50"),
            self.create_stat_card("סה״כ הצעות", str(self.stats.get('total_quotes', 0)), ft.Icons.DESCRIPTION, "#2196f3"),
            self.create_stat_card("לקוחות פעילים", str(len(set(self.stats.get('last_customers', [])))), ft.Icons.PEOPLE, "#ff9800"),
            self.create_stat_card("הכנסות משוערות", f"₪{self.stats.get('total_revenue', 0):,}", ft.Icons.ATTACH_MONEY, "#9c27b0"),
        ], spacing=20, wrap=True, alignment=ft.MainAxisAlignment.CENTER)

        # Components
        welcome = ft.Container(
            content=ft.Column([
                ft.Text(f"שלום, {datetime.now().strftime('%A')} טוב!", size=32, weight=ft.FontWeight.BOLD, color="#d32f2f"),
                ft.Text("מה תרצה לעשות היום?", size=20, color="#666666"),
            ]), padding=30, bgcolor="#ffffff",
            border_radius=15, width=self.page.window_width - 100,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=5,
                                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK), offset=ft.Offset(0, 2))
        )

        tips = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.LIGHTBULB, color="#ffc107"),
                    ft.Text("טיפ היום", size=18, weight=ft.FontWeight.BOLD),
                ]),
                ft.Text(self.get_daily_tip(), size=14, color="#666666"),
            ], spacing=10), padding=20, bgcolor="#fffbf0",
            border_radius=10, width=self.page.window_width - 100
        )

        recent_activity = self.create_recent_activity()

        return ft.Column([
            welcome,
            ft.Container(height=20),
            action_cards,
            ft.Container(height=20),
            stats_cards,
            ft.Container(height=20),
            recent_activity,
            ft.Container(height=20),
            tips,
        ], spacing=10, scroll=ft.ScrollMode.AUTO)