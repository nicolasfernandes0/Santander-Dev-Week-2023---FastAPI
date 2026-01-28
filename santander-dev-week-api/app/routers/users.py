from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import time

from app import crud
from app.database import get_db
from app.models import (
    UserResponse, UserCreate, UserUpdate,
    DepositRequest, WithdrawRequest, TransferRequest, SimpleUserCreate
)

router = APIRouter(prefix="/users", tags=["users"])

# ========== GET ENDPOINTS ==========

@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Retorna lista de usuários"""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Retorna usuário pelo ID"""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário {user_id} não encontrado"
        )
    return db_user

@router.get("/{user_id}/balance")
def get_user_balance(user_id: int, db: Session = Depends(get_db)):
    """Retorna saldo do usuário"""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário {user_id} não encontrado"
        )
    
    return {
        "user_id": user_id,
        "balance": db_user.account.balance,
        "available_limit": db_user.account.limit,
        "total_available": db_user.account.balance + db_user.account.limit
    }

# ========== POST ENDPOINTS ==========

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Cria novo usuário completo"""
    user_data = user.model_dump()
    db_user = crud.create_user(db, user_data)
    return db_user

@router.post("/simple", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_simple_user(user: SimpleUserCreate, db: Session = Depends(get_db)):
    """Cria usuário simplificado"""
    import random
    
    user_data = {
        "name": user.name,
        "email": user.email,
        "account": {
            "number": f"{random.randint(10000, 99999)}-{random.randint(0, 9)}",
            "agency": "0001",
            "balance": user.initial_balance,
            "limit": 1000.0
        },
        "card": {
            "number": f"**** **** **** {random.randint(1000, 9999)}",
            "limit": 2000.0
        },
        "features": [
            {"icon": "💰", "description": "Pix"},
            {"icon": "💸", "description": "Transferência"},
            {"icon": "🛒", "description": "Pagamentos"}
        ],
        "news": [
            {"icon": "🎉", "description": "Bem-vindo ao Santander Dev Week!"}
        ]
    }
    
    db_user = crud.create_user(db, user_data)
    return db_user

@router.post("/{user_id}/deposit", status_code=status.HTTP_200_OK)
def deposit_money(
    user_id: int,
    deposit: DepositRequest,
    db: Session = Depends(get_db)
):
    """Realiza depósito"""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário {user_id} não encontrado"
        )
    
    crud.deposit_money(db, user_id, deposit.amount)
    db_user = crud.get_user(db, user_id=user_id)
    
    return {
        "message": "Depósito realizado com sucesso",
        "user_id": user_id,
        "amount": deposit.amount,
        "new_balance": db_user.account.balance,
        "transaction_id": f"DEP{int(time.time())}{user_id}"
    }

@router.post("/{user_id}/withdraw", status_code=status.HTTP_200_OK)
def withdraw_money(
    user_id: int,
    withdraw: WithdrawRequest,
    db: Session = Depends(get_db)
):
    """Realiza saque"""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário {user_id} não encontrado"
        )
    
    try:
        crud.withdraw_money(db, user_id, withdraw.amount)
        db_user = crud.get_user(db, user_id=user_id)
        
        return {
            "message": "Saque realizado com sucesso",
            "user_id": user_id,
            "amount": withdraw.amount,
            "new_balance": db_user.account.balance,
            "transaction_id": f"SAQ{int(time.time())}{user_id}"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{user_id}/transfer", status_code=status.HTTP_200_OK)
def transfer_money(
    user_id: int,
    transfer: TransferRequest,
    db: Session = Depends(get_db)
):
    """Realiza transferência"""
    try:
        result = crud.transfer_money(db, user_id, transfer.to_user_id, transfer.amount)
        
        return {
            "message": "Transferência realizada com sucesso",
            "from_user_id": user_id,
            "to_user_id": transfer.to_user_id,
            "amount": transfer.amount,
            "new_balance_from": result["new_balance_from"],
            "new_balance_to": result["new_balance_to"],
            "transaction_id": f"TRF{int(time.time())}{user_id}"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ========== PUT ENDPOINTS ==========

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza usuário"""
    db_user = crud.update_user(db, user_id, user_update.model_dump(exclude_unset=True))
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário {user_id} não encontrado"
        )
    return db_user

# ========== DELETE ENDPOINTS ==========

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Remove usuário"""
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário {user_id} não encontrado"
        )
    return None