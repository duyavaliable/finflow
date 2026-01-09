import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

# Load .env một lần duy nhất
load_dotenv()

class Database:
    """Database connection handler - SQLite only"""
    
    def __init__(self, db_path: str = None):
        # Đọc DATABASE_PATH từ .env
        self.db_path = db_path or os.getenv('DATABASE_PATH', 'dev.db')

    def get_connection(self):
        """Tạo kết nối SQLite với row_factory để trả về dict-like objects"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute(self, query: str, params: tuple = ()):
        """Thực thi query và trả về tất cả rows"""
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(query, params or ())
            try:
                rows = cur.fetchall()
            except Exception:
                rows = []
            conn.commit()
            conn.close()
            return rows
        except Exception:
            conn.rollback()
            conn.close()
            raise

    def execute_one(self, query: str, params: tuple = ()):
        """Thực thi query và trả về 1 row"""
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(query, params or ())
            row = cur.fetchone()
            conn.commit()
            conn.close()
            return row
        except Exception:
            conn.rollback()
            conn.close()
            raise

    def execute_insert(self, query, params=()):
        """Thực thi INSERT và trả về lastrowid"""
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(query, params or ())
            conn.commit()
            last_id = cur.lastrowid
            conn.close()
            return last_id
        except Exception:
            conn.rollback()
            conn.close()
            raise

# Global database instance
db = Database()
print(f"[DEBUG] Using SQLite: {db.db_path}")

class SavingsGoal:
    """Savings Goal model - giữ nguyên"""
    
    @staticmethod
    def create(name: str, target_amount: float, deadline: Optional[str] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Tạo mục tiêu tiết kiệm mới"""
        now = datetime.now().isoformat()
        query = '''
            INSERT INTO SavingsGoal (name, targetAmount, currentAmount, deadline, userId, createdAt, updatedAt)
            VALUES (?, ?, 0, ?, ?, ?, ?)
        '''
        new_id = db.execute_insert(query, (name, target_amount, deadline, user_id, now, now))
        return SavingsGoal.find_by_id(new_id)
    
    @staticmethod
    def find_all(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lấy tất cả mục tiêu"""
        if user_id:
            query = 'SELECT * FROM SavingsGoal WHERE userId = ? ORDER BY createdAt DESC'
            results = db.execute(query, (user_id,))
        else:
            query = 'SELECT * FROM SavingsGoal ORDER BY createdAt DESC'
            results = db.execute(query)
        
        return [dict(row) for row in results]
    
    @staticmethod
    def find_by_id(goal_id: str) -> Optional[Dict[str, Any]]:
        """Tìm mục tiêu theo ID"""
        query = 'SELECT * FROM SavingsGoal WHERE id = ?'
        result = db.execute_one(query, (goal_id,))
        return dict(result) if result else None
    
    @staticmethod
    def update(goal_id: str, name: Optional[str] = None, target_amount: Optional[float] = None, 
               current_amount: Optional[float] = None, deadline: Optional[str] = None) -> Dict[str, Any]:
        """Cập nhật mục tiêu"""
        updates = []
        params = []
        
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        if target_amount is not None:
            updates.append('targetAmount = ?')
            params.append(target_amount)
        if current_amount is not None:
            updates.append('currentAmount = ?')
            params.append(current_amount)
        if deadline is not None:
            updates.append('deadline = ?')
            params.append(deadline)
        
        updates.append('updatedAt = ?')
        params.append(datetime.now().isoformat())
        params.append(goal_id)
        
        query = f"UPDATE SavingsGoal SET {', '.join(updates)} WHERE id = ?"
        db.execute(query, tuple(params))
        
        return SavingsGoal.find_by_id(goal_id)
    
    @staticmethod
    def delete(goal_id: str) -> bool:
        """Xóa mục tiêu"""
        query = 'DELETE FROM SavingsGoal WHERE id = ?'
        db.execute(query, (goal_id,))
        return True
    
    @staticmethod
    def add_amount(goal_id: str, amount: float) -> Dict[str, Any]:
        """Thêm tiền vào mục tiêu"""
        query = '''
            UPDATE SavingsGoal 
            SET currentAmount = currentAmount + ?, updatedAt = ?
            WHERE id = ?
        '''
        db.execute(query, (amount, datetime.now().isoformat(), goal_id))
        return SavingsGoal.find_by_id(goal_id)

class Account:
    """Account model - Tài khoản ngân hàng"""
    
    @staticmethod
    def create(name: str, bank: str, account_number: str, starting_balance: float = 0) -> Dict[str, Any]:
        """Tạo tài khoản mới"""
        now = datetime.now().isoformat()
        query = '''
            INSERT INTO Account (name, bank, accountNumber, currentBalance, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        new_id = db.execute_insert(query, (name, bank, account_number, starting_balance, now, now))
        return Account.find_by_id(new_id)
    
    @staticmethod
    def find_all() -> List[Dict[str, Any]]:
        """Lấy tất cả tài khoản"""
        query = 'SELECT * FROM Account ORDER BY name'
        results = db.execute(query)
        return [dict(row) for row in results]
    
    @staticmethod
    def find_by_id(account_id: str) -> Optional[Dict[str, Any]]:
        """Tìm tài khoản theo ID"""
        query = 'SELECT * FROM Account WHERE id = ?'
        result = db.execute_one(query, (account_id,))
        return dict(result) if result else None
    
    @staticmethod
    def update_balance(account_id: str, new_balance: float) -> bool:
        """Cập nhật số dư"""
        query = 'UPDATE Account SET currentBalance = ?, updatedAt = ? WHERE id = ?'
        db.execute(query, (new_balance, datetime.now().isoformat(), account_id))
        return True

class Transaction:
    """Transaction model - Giao dịch thu chi"""
    
    @staticmethod
    def create(account_id: Optional[int], amount: float, category: str, description: str, 
               date: str, trans_type: str) -> Dict[str, Any]:
        """Tạo giao dịch mới"""
        now = datetime.now().isoformat()
        query = '''
            INSERT INTO Transaction (accountId, amount, category, description, date, type, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        new_id = db.execute_insert(query, (account_id, amount, category, description, date, trans_type, now, now))
        return Transaction.find_by_id(new_id)
    
    @staticmethod
    def find_all(account_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Lấy danh sách giao dịch"""
        if account_id:
            query = 'SELECT * FROM Transaction WHERE accountId = ? ORDER BY date DESC LIMIT ?'
            results = db.execute(query, (account_id, limit))
        else:
            query = 'SELECT * FROM Transaction ORDER BY date DESC LIMIT ?'
            results = db.execute(query, (limit,))
        
        return [dict(row) for row in results]
    
    @staticmethod
    def find_by_id(trans_id: str) -> Optional[Dict[str, Any]]:
        """Tìm giao dịch theo ID"""
        query = 'SELECT * FROM Transaction WHERE id = ?'
        result = db.execute_one(query, (trans_id,))
        return dict(result) if result else None
    
    @staticmethod
    def delete(trans_id: str) -> bool:
        """Xóa giao dịch"""
        query = 'DELETE FROM Transaction WHERE id = ?'
        db.execute(query, (trans_id,))
        return True

class User:
    """User model - simple auth"""
    
    @staticmethod
    def create(username, name, email, password, phone=None):
        now = datetime.now().isoformat()
        phash = generate_password_hash(password)
        # Insert without id -> SQLite assigns INTEGER PK
        query = '''INSERT INTO "User" (username,name,email,passwordHash,phone,createdAt,updatedAt)
                   VALUES (?, ?, ?, ?, ?, ?, ?)'''
        new_id = db.execute_insert(query, (username, name, email, phash, phone, now, now))
        return User.find_by_id(new_id)
    
    @staticmethod
    def find_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        query = 'SELECT * FROM "User" WHERE id = ?'
        result = db.execute_one(query, (user_id,))
        return dict(result) if result else None
    
    @staticmethod
    def find_by_username(username: str) -> Optional[Dict[str, Any]]:
        query = 'SELECT * FROM "User" WHERE username = ?'
        result = db.execute_one(query, (username,))
        return dict(result) if result else None
    
    @staticmethod
    def find_by_email(email: str) -> Optional[Dict[str, Any]]:
        query = 'SELECT * FROM "User" WHERE email = ?'
        result = db.execute_one(query, (email,))
        return dict(result) if result else None
    
    @staticmethod
    def verify_password(stored_hash: str, password: str) -> bool:
        return check_password_hash(stored_hash, password)
    
    @staticmethod
    def update_name(user_id: str, new_name: str) -> Dict[str, Any]:
        query = 'UPDATE "User" SET name = ?, updatedAt = ? WHERE id = ?'
        db.execute(query, (new_name, datetime.now().isoformat(), user_id))
        return User.find_by_id(user_id)
