import random
from datetime import datetime, timedelta

class MockData:
    def __init__(self):
        self.user_profile = {
            "name": "Alex Chen",
            "account_id": "8829-1102-4432",
            "credit_score": 742,
            "account_balance": 12450.50
        }
        
        self.transactions = self._generate_transactions()
        self.offers = [
            {
                "id": "offer_1",
                "title": "Premium Travel Card",
                "description": "Earn 3x points on all travel purchases. 50,000 bonus points.",
                "image": "travel_card.png",
                "match_score": 95
            },
            {
                "id": "offer_2",
                "title": "Home Improvement Loan",
                "description": "Low 4.5% APR for your renovation projects.",
                "image": "home_loan.png",
                "match_score": 82
            },
            {
                "id": "offer_3",
                "title": "High Yield Savings",
                "description": "4.2% APY guaranteed for 12 months.",
                "image": "savings.png",
                "match_score": 70
            }
        ]

    def _generate_transactions(self):
        categories = ["Food & Dining", "Shopping", "Transportation", "Bills & Utilities", "Entertainment", "Travel"]
        merchants = {
            "Food & Dining": ["Uber Eats", "Starbucks", "Whole Foods", "Local Bistro", "Pizza Hut"],
            "Shopping": ["Amazon", "Target", "Nike", "Apple Store", "Zara"],
            "Transportation": ["Uber", "Shell Gas", "Subway", "Delta Airlines"],
            "Bills & Utilities": ["Electric Co", "Water Dept", "Internet Provider", "Mobile Carrier"],
            "Entertainment": ["Netflix", "Spotify", "Cinema City", "Steam"],
            "Travel": ["Airbnb", "Hilton", "Expedia"]
        }
        
        transactions = []
        start_date = datetime.now() - timedelta(days=90)
        
        for _ in range(150):
            cat = random.choice(categories)
            merchant = random.choice(merchants[cat])
            amount = round(random.uniform(5.0, 300.0), 2)
            if cat == "Travel" or cat == "Shopping":
                if random.random() > 0.8:
                    amount = round(random.uniform(300.0, 1500.0), 2)
            
            date = start_date + timedelta(days=random.randint(0, 90))
            
            transactions.append({
                "date": date.strftime("%Y-%m-%d"),
                "merchant": merchant,
                "category": cat,
                "amount": amount
            })
            
        return sorted(transactions, key=lambda x: x['date'], reverse=True)

    def get_spend_analysis(self):
        analysis = {}
        for t in self.transactions:
            cat = t['category']
            analysis[cat] = analysis.get(cat, 0) + t['amount']
        
        # Format for chart
        return [{"name": k, "value": round(v, 2)} for k, v in analysis.items()]

    def get_credit_score_details(self):
        return {
            "score": self.user_profile["credit_score"],
            "history": [
                {"month": "Jan", "score": 710},
                {"month": "Feb", "score": 715},
                {"month": "Mar", "score": 712},
                {"month": "Apr", "score": 725},
                {"month": "May", "score": 730},
                {"month": "Jun", "score": 742}
            ],
            "factors": [
                {"name": "Payment History", "status": "Excellent", "impact": "High"},
                {"name": "Credit Usage", "status": "Good", "impact": "High"},
                {"name": "Credit Age", "status": "Average", "impact": "Medium"}
            ]
        }

    def get_recommendations(self):
        return sorted(self.offers, key=lambda x: x['match_score'], reverse=True)

mock_db = MockData()
