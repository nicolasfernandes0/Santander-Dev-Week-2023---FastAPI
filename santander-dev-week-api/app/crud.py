from sqlalchemy.orm import Session
from app import models
from app.models import UserDB, AccountDB, CardDB, FeatureDB, NewsDB

# ========== OPERAÇÕES BÁSICAS ==========

def get_user(db: Session, user_id: int):
    return db.query(UserDB).filter(UserDB.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(UserDB).offset(skip).limit(limit).all()

def create_user(db: Session, user_data: dict):
    # Extrair dados relacionados
    account_data = user_data.pop('account')
    card_data = user_data.pop('card')
    features_data = user_data.pop('features')
    news_data = user_data.pop('news')
    
    # Criar usuário
    db_user = UserDB(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Criar conta
    db_account = AccountDB(**account_data, user_id=db_user.id)
    db.add(db_account)
    
    # Criar cartão
    db_card = CardDB(**card_data, user_id=db_user.id)
    db.add(db_card)
    
    # Criar features
    for feature in features_data:
        db_feature = FeatureDB(**feature, user_id=db_user.id)
        db.add(db_feature)
    
    # Criar news
    for news_item in news_data:
        db_news = NewsDB(**news_item, user_id=db_user.id)
        db.add(db_news)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, update_data: dict):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    for key, value in update_data.items():
        if hasattr(db_user, key) and value is not None:
            setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# ========== OPERAÇÕES BANCÁRIAS ==========

def get_user_account(db: Session, user_id: int):
    user = get_user(db, user_id)
    return user.account if user else None

def deposit_money(db: Session, user_id: int, amount: float):
    account = get_user_account(db, user_id)
    if account:
        account.balance += amount
        db.commit()
        db.refresh(account)
    return account

def withdraw_money(db: Session, user_id: int, amount: float):
    account = get_user_account(db, user_id)
    if account:
        # Verificar saldo suficiente
        if amount > (account.balance + account.limit):
            raise ValueError("Saldo insuficiente")
        
        account.balance -= amount
        db.commit()
        db.refresh(account)
    return account

def transfer_money(db: Session, from_user_id: int, to_user_id: int, amount: float):
    from_account = get_user_account(db, from_user_id)
    to_account = get_user_account(db, to_user_id)
    
    if not from_account or not to_account:
        raise ValueError("Uma das contas não existe")
    
    # Verificar saldo suficiente
    if amount > (from_account.balance + from_account.limit):
        raise ValueError("Saldo insuficiente para transferência")
    
    # Realizar transferência
    from_account.balance -= amount
    to_account.balance += amount
    
    db.commit()
    
    return {
        "from_user": from_user_id,
        "to_user": to_user_id,
        "amount": amount,
        "new_balance_from": from_account.balance,
        "new_balance_to": to_account.balance
    }

# ========== DADOS INICIAIS ==========

def seed_initial_data(db: Session):
    """Popula o banco com dados iniciais"""
    # Verificar se já existem usuários
    if db.query(UserDB).count() > 0:
        return db.query(UserDB).all()
    
    # Dados do usuário 1 (igual API original)
    mock_user_1 = {
        "name": "Devweekerson",
        "email": "devweekerson@santander.com",
        "account": {
            "number": "01.097954-4",
            "agency": "2030",
            "balance": 624.12,
            "limit": 1000.0
        },
        "card": {
            "number": "**** **** **** 1111",
            "limit": 2000.0
        },
        "features": [
            {"icon": "💰", "description": "Pix"},
            {"icon": "💸", "description": "Transfer"},
            {"icon": "🛒", "description": "Pay"}
        ],
        "news": [
            {"icon": "🎉", "description": "New feature released!"},
            {"icon": "📢", "description": "System maintenance scheduled"}
        ]
    }
    
    # Dados do usuário 2
    mock_user_2 = {
        "name": "Maria Silva",
        "email": "maria.silva@email.com",
        "account": {
            "number": "02.123456-7",
            "agency": "2031",
            "balance": 1500.50,
            "limit": 2000.0
        },
        "card": {
            "number": "**** **** **** 2222",
            "limit": 3000.0
        },
        "features": [
            {"icon": "💰", "description": "Pix"},
            {"icon": "📊", "description": "Investimentos"}
        ],
        "news": [
            {"icon": "🎉", "description": "Bem-vinda ao Santander!"}
        ]
    }
    
    # Criar usuários
    user1 = create_user(db, mock_user_1)
    user2 = create_user(db, mock_user_2)
    
    return [user1, user2]