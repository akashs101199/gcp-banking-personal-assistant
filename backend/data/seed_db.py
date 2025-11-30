from data.db import init_db, SessionLocal, User, Transaction, Offer
from data.mock_data import mock_db

def seed_data():
    print("Initializing Database...")
    init_db()
    
    db = SessionLocal()
    
    # Check if data exists
    if db.query(User).first():
        print("Data already exists.")
        return

    print("Seeding Data...")
    
    # Create User
    user = User(
        name=mock_db.user_profile["name"],
        credit_score=mock_db.user_profile["credit_score"],
        account_balance=mock_db.user_profile["account_balance"]
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create Transactions
    for t in mock_db.transactions:
        trans = Transaction(
            user_id=user.id,
            date=t["date"],
            merchant=t["merchant"],
            category=t["category"],
            amount=t["amount"]
        )
        db.add(trans)
    
    # Create Offers
    for o in mock_db.offers:
        offer = Offer(
            title=o["title"],
            description=o["description"],
            match_score=o["match_score"]
        )
        db.add(offer)
        
    db.commit()
    print("Seeding Complete!")
    db.close()

if __name__ == "__main__":
    seed_data()
