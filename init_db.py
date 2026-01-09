import sqlite3
from datetime import datetime
import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load .env so DB path can be provided via DATABASE_PATH
load_dotenv()
DB_PATH = os.getenv('DATABASE_PATH', 'prisma/dev.db')


def migrate_to_integer_ids(conn: sqlite3.Connection):
    """
    Migrate existing TEXT/UUID id schema to INTEGER AUTOINCREMENT ids.
    Copies data into *_new tables, maps old_id -> new_id for foreign keys,
    then replaces old tables.
    If tables do not exist or are already integer-based, does nothing.
    """
    cur = conn.cursor()

    def table_exists(name: str) -> bool:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (name,))
        return cur.fetchone() is not None

    # If no User table, nothing to migrate
    if not table_exists('User'):
        print("ℹ️  Bỏ qua migration: bảng 'User' không tồn tại (DB mới).")
        return

    # If User.id already integer PK, skip
    cur.execute("PRAGMA table_info('User')")
    cols = cur.fetchall()
    if cols and 'INT' in (cols[0][2] or '').upper():
        print("ℹ️  Bỏ qua migration: 'User.id' đã là INTEGER.")
        return

    print("🔁 Chạy migration: chuyển id TEXT (UUID) sang INTEGER AUTOINCREMENT")

    # --- Create new tables with INTEGER PK ---
    cur.execute('''
      CREATE TABLE IF NOT EXISTS User_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        name TEXT,
        email TEXT UNIQUE,
        passwordHash TEXT NOT NULL,
        phone TEXT,
        createdAt TEXT NOT NULL,
        updatedAt TEXT NOT NULL
      )
    ''')

    cur.execute('''
      CREATE TABLE IF NOT EXISTS SavingsGoal_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        targetAmount REAL NOT NULL,
        currentAmount REAL DEFAULT 0,
        deadline TEXT,
        userId INTEGER,
        createdAt TEXT NOT NULL,
        updatedAt TEXT NOT NULL
      )
    ''')

    cur.execute('''
      CREATE TABLE IF NOT EXISTS Account_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        bank TEXT,
        accountNumber TEXT,
        currentBalance REAL DEFAULT 0,
        createdAt TEXT NOT NULL,
        updatedAt TEXT NOT NULL
      )
    ''')

    cur.execute('''
      CREATE TABLE IF NOT EXISTS Transaction_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        accountId INTEGER,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        date TEXT NOT NULL,
        type TEXT NOT NULL,
        createdAt TEXT NOT NULL,
        updatedAt TEXT NOT NULL
      )
    ''')

    conn.commit()

    # --- Copy users and build mapping old_id -> new_id ---
    cur.execute('SELECT id, username, name, email, passwordHash, phone, createdAt, updatedAt FROM "User"')
    user_rows = cur.fetchall()
    user_map: Dict[str, int] = {}
    for old_id, username, name, email, phash, phone, createdAt, updatedAt in user_rows:
        cur.execute('INSERT INTO User_new (username,name,email,passwordHash,phone,createdAt,updatedAt) VALUES (?,?,?,?,?,?,?)',
                    (username, name, email, phash, phone, createdAt, updatedAt))
        user_map[old_id] = cur.lastrowid

    # --- Copy SavingsGoal, map userId ---
    if table_exists('SavingsGoal'):
        cur.execute("SELECT id, name, targetAmount, currentAmount, deadline, userId, createdAt, updatedAt FROM SavingsGoal")
        for old_id, name, targetAmount, currentAmount, deadline, old_userId, createdAt, updatedAt in cur.fetchall():
            new_user = user_map.get(old_userId) if old_userId else None
            cur.execute('INSERT INTO SavingsGoal_new (name,targetAmount,currentAmount,deadline,userId,createdAt,updatedAt) VALUES (?,?,?,?,?,?,?)',
                        (name, targetAmount, currentAmount, deadline, new_user, createdAt, updatedAt))

    # --- Copy Account (no user mapping assumed) ---
    if table_exists('Account'):
        cur.execute("SELECT id, name, bank, accountNumber, currentBalance, createdAt, updatedAt FROM Account")
        account_old = cur.fetchall()
        account_map: Dict[str, int] = {}
        for old_id, name, bank, accountNumber, currentBalance, createdAt, updatedAt in account_old:
            cur.execute('INSERT INTO Account_new (name,bank,accountNumber,currentBalance,createdAt,updatedAt) VALUES (?,?,?,?,?,?)',
                        (name, bank, accountNumber, currentBalance, createdAt, updatedAt))
            account_map[old_id] = cur.lastrowid

    # --- Copy Transaction, map accountId ---
    if table_exists('Transaction'):
        cur.execute('SELECT id, accountId, amount, category, description, date, type, createdAt, updatedAt FROM `Transaction`')
        for old_id, old_accountId, amount, category, description, date, ttype, createdAt, updatedAt in cur.fetchall():
            new_acc = account_map.get(old_accountId) if old_accountId else None
            cur.execute('INSERT INTO Transaction_new (accountId, amount, category, description, date, type, createdAt, updatedAt) VALUES (?,?,?,?,?,?,?,?)',
                        (new_acc, amount, category, description, date, ttype, createdAt, updatedAt))

    conn.commit()

    # --- Replace old tables with new ---
    for tbl in ['Transaction', 'Account', 'SavingsGoal', 'User']:
        cur.execute(f'DROP TABLE IF EXISTS "{tbl}"')

    cur.execute('ALTER TABLE User_new RENAME TO "User"')
    cur.execute('ALTER TABLE SavingsGoal_new RENAME TO "SavingsGoal"')
    cur.execute('ALTER TABLE Account_new RENAME TO "Account"')
    cur.execute('ALTER TABLE Transaction_new RENAME TO "Transaction"')
    conn.commit()

    print("✅ Migration hoàn tất: id chuyển sang INTEGER AUTOINCREMENT")


def init_database():
    """Khởi tạo database với schema cơ bản (KHÔNG có dữ liệu mẫu)"""

    # Tạo thư mục chứa DB nếu chưa có
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # run migration if needed (migrate will skip if DB is new or already integer)
    migrate_to_integer_ids(conn)

    # tiếp tục tạo bảng (IF NOT EXISTS) với id INTEGER AUTOINCREMENT
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SavingsGoal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            targetAmount REAL NOT NULL,
            currentAmount REAL DEFAULT 0,
            deadline TEXT,
            userId INTEGER,
            createdAt TEXT NOT NULL,
            updatedAt TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Account (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            bank TEXT,
            accountNumber TEXT,
            currentBalance REAL DEFAULT 0,
            createdAt TEXT NOT NULL,
            updatedAt TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `Transaction` (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            accountId INTEGER,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            createdAt TEXT NOT NULL,
            updatedAt TEXT NOT NULL,
            FOREIGN KEY (accountId) REFERENCES Account(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "User" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            name TEXT,
            email TEXT UNIQUE,
            passwordHash TEXT NOT NULL,
            phone TEXT,
            createdAt TEXT NOT NULL,
            updatedAt TEXT NOT NULL
        )
    ''')

    conn.commit()

    # Kiểm tra xem đã có dữ liệu chưa
    cursor.execute('SELECT COUNT(*) FROM SavingsGoal')
    count = cursor.fetchone()[0]

    if count == 0:
        print("⚠️  Database trống - chưa có dữ liệu")
        print("   Hãy thêm mục tiêu tiết kiệm đầu tiên qua giao diện web")
    else:
        print(f"✅ Database đã có {count} mục tiêu tiết kiệm")

    conn.close()

    print(f"✅ Database đã sẵn sàng tại {DB_PATH}")


if __name__ == '__main__':
    init_database()
