
from replit import db
import discord
from typing import List, Union

def ensure_token_data_exists():
    """S'assure que la structure des données de jetons existe"""
    if "token_balances" not in db:
        db["token_balances"] = {}

def get_balance(user_id: str) -> int:
    """Récupère le solde de jetons d'un utilisateur"""
    ensure_token_data_exists()
    return db["token_balances"].get(str(user_id), 0)

def add_tokens(user_id: str, amount: int) -> bool:
    """Ajoute des jetons au solde d'un utilisateur"""
    ensure_token_data_exists()
    balances = db["token_balances"]
    user_id = str(user_id)
    current_balance = balances.get(user_id, 0)
    balances[user_id] = current_balance + amount
    db["token_balances"] = balances
    return True

def remove_tokens(user_id: str, amount: int) -> bool:
    """Retire des jetons du solde d'un utilisateur"""
    ensure_token_data_exists()
    balances = db["token_balances"]
    user_id = str(user_id)
    current_balance = balances.get(user_id, 0)

    if current_balance < amount:
        return False

    balances[user_id] = current_balance - amount
    db["token_balances"] = balances
    return True

def transfer_tokens(from_user: str, to_user: str, amount: int) -> bool:
    """Transfère des jetons entre deux utilisateurs"""
    if remove_tokens(from_user, amount):
        add_tokens(to_user, amount)
        return True
    return False
