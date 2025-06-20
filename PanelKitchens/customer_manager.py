import os
import json
from datetime import datetime
from typing import List, Dict, Optional


class CustomerManager:
    def __init__(self, data_dir: str = "panel_data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.customers_file = os.path.join(self.data_dir, "customers.json")
        self.quotes_file = os.path.join(self.data_dir, "quotes_history.json")
        self.drafts_file = os.path.join(self.data_dir, "drafts.json")

        self.customers: Dict[str, dict] = self._load_json(self.customers_file, {})
        self.quotes_history: List[dict] = self._load_json(self.quotes_file, [])
        self.drafts: Dict[str, dict] = self._load_json(self.drafts_file, {})

    def _load_json(self, filepath: str, default):
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return default
        return default

    def _save_json(self, filepath: str, data) -> None:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # Customers
    def add_customer(self, data: Dict) -> str:
        customer_id = data.get('phone', '').replace('-', '') or f"customer_{len(self.customers)}"
        now = datetime.now().isoformat()
        existing = self.customers.get(customer_id, {})

        self.customers[customer_id] = {
            'id': customer_id,
            'name': data.get('name', existing.get('name', '')),
            'phone': data.get('phone', existing.get('phone', '')),
            'email': data.get('email', existing.get('email', '')),
            'address': data.get('address', existing.get('address', '')),
            'created_at': existing.get('created_at', now),
            'updated_at': now,
            'quotes_count': existing.get('quotes_count', 0),
            'total_amount': existing.get('total_amount', 0),
            'notes': data.get('notes', existing.get('notes', '')),
        }
        self._save_json(self.customers_file, self.customers)
        return customer_id

    def get_customer(self, customer_id: str) -> Optional[dict]:
        return self.customers.get(customer_id)

    def search_customers(self, query: str) -> List[dict]:
        query = query.lower()
        return [c for c in self.customers.values() if query in c['name'].lower() or query in c['phone']]

    def get_all_customers(self) -> List[dict]:
        return sorted(self.customers.values(), key=lambda x: x['name'])

    # Quotes
    def save_quote(self, quote: Dict) -> str:
        quote_id = f"quote_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        customer_id = self.add_customer(quote['customer_data'])
        now = datetime.now().isoformat()
        record = {
            'id': quote_id,
            'customer_id': customer_id,
            'customer_name': quote['customer_data']['name'],
            'date': quote['customer_data'].get('date', now),
            'items': quote.get('items', []),
            'total_amount': quote.get('total_amount', 0),
            'discount': quote['customer_data'].get('discount', 0),
            'created_at': now,
            'pdf_path': quote.get('pdf_path', ''),
            'notes': quote.get('notes', ''),
        }
        self.quotes_history.append(record)
        # update customer stats
        cust = self.customers[customer_id]
        cust['quotes_count'] += 1
        cust['total_amount'] += record['total_amount']
        cust['updated_at'] = now

        self._save_json(self.quotes_file, self.quotes_history)
        self._save_json(self.customers_file, self.customers)
        return quote_id

    def get_quote_history(self, customer_id: Optional[str] = None) -> List[dict]:
        quotes = self.quotes_history
        if customer_id:
            quotes = [q for q in quotes if q['customer_id'] == customer_id]
        return sorted(quotes, key=lambda x: x['created_at'], reverse=True)

    # Drafts
    def save_draft(self, draft: Dict) -> str:
        draft_id = draft.get('id', f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        now = datetime.now().isoformat()
        existing = self.drafts.get(draft_id, {})
        self.drafts[draft_id] = {
            'id': draft_id,
            'customer_data': draft.get('customer_data', existing.get('customer_data', {})),
            'items': draft.get('items', existing.get('items', [])),
            'created_at': existing.get('created_at', now),
            'updated_at': now,
            'title': draft.get('title', existing.get('title', '')),
        }
        self._save_json(self.drafts_file, self.drafts)
        return draft_id

    def get_all_drafts(self) -> List[dict]:
        return sorted(self.drafts.values(), key=lambda x: x['updated_at'], reverse=True)

    def delete_draft(self, draft_id: str) -> bool:
        if draft_id in self.drafts:
            del self.drafts[draft_id]
            self._save_json(self.drafts_file, self.drafts)
            return True
        return False

    # Statistics & Export
    def get_statistics(self) -> dict:
        stats = {
            'total_customers': len(self.customers),
            'total_quotes': len(self.quotes_history),
            'total_revenue': sum(q['total_amount'] for q in self.quotes_history),
        }
        if stats['total_quotes']:
            stats['average_quote'] = stats['total_revenue'] / stats['total_quotes']
        else:
            stats['average_quote'] = 0

        # this month stats
        current_month = datetime.now().strftime('%Y-%m')
        stats['this_month_quotes'] = sum(1 for q in self.quotes_history if q['created_at'][:7] == current_month)
        stats['this_month_revenue'] = sum(q['total_amount'] for q in self.quotes_history if q['created_at'][:7] == current_month)

        # popular products and top customers
        popular = {}
        customer_totals = {}
        for q in self.quotes_history:
            cid = q['customer_id']
            customer_totals[cid] = customer_totals.get(cid, 0) + q['total_amount']
            for item in q.get('items', []):
                name = item.get('name', '')
                if name:
                    popular.setdefault(name, {'count': 0, 'quantity': 0})
                    popular[name]['count'] += 1
                    popular[name]['quantity'] += item.get('quantity', 0)
        stats['popular_products'] = popular
        stats['top_customers'] = sorted(
            [{'name': self.customers[cid]['name'], 'total_amount': amt} for cid, amt in customer_totals.items()],
            key=lambda x: x['total_amount'], reverse=True)[:5]

        return stats

    def export_to_excel(self, filepath: str) -> None:
        import pandas as pd
        writer = pd.ExcelWriter(filepath, engine='openpyxl')
        pd.DataFrame.from_dict(self.customers, orient='index').to_excel(writer, sheet_name='לקוחות', index=False)
        pd.DataFrame(self.quotes_history).to_excel(writer, sheet_name='הצעות מחיר', index=False)
        stats = self.get_statistics()
        stats_df = pd.DataFrame({
            'מדד': ['סה"כ לקוחות', 'סה"כ הצעות', 'סה"כ הכנסות', 'ממוצע הצעה', 'הצעות החודש', 'הכנסות החודש'],
            'ערך': [
                stats['total_customers'], stats['total_quotes'], f"₪{stats['total_revenue']:,.2f}",
                f"₪{stats['average_quote']:,.2f}", stats['this_month_quotes'], f"₪{stats['this_month_revenue']:,.2f}"
            ]
        })
        stats_df.to_excel(writer, sheet_name='סטטיסטיקות', index=False)
        writer.save()

    def create_backup(self) -> None:
        import shutil
        backup_dir = os.path.join(self.data_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        for fname in [self.customers_file, self.quotes_file, self.drafts_file]:
            if os.path.exists(fname):
                dst = os.path.join(backup_dir, f"{timestamp}_{os.path.basename(fname)}")
                shutil.copy2(fname, dst)
        # keep last 30 backups
        backups = sorted(os.listdir(backup_dir))
        for old in backups[:-30]:
            os.remove(os.path.join(backup_dir, old))
