import sqlite3
import os
import threading
from contextlib import contextmanager
from config import Config

# 线程本地存储，确保每个线程有独立的数据库连接
local = threading.local()

def get_db_path():
    """获取数据库文件路径"""
    # Config.DATABASE 现在已经是绝对路径，直接使用
    return Config.DATABASE

@contextmanager
def get_db_connection():
    """获取数据库连接（线程安全）"""
    db_path = get_db_path()
    conn = None
    
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        yield conn
    except sqlite3.OperationalError as e:
        print(f"[DB] 数据库操作错误: {e}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise e
    except Exception as e:
        print(f"[DB] 数据库连接错误: {e}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise e
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

def execute_query(query, params=None):
    """执行查询语句"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor

def fetch_all(query, params=None):
    """获取所有结果 - 在同一连接中执行并返回结果"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

def fetch_one(query, params=None):
    """获取单条结果 - 在同一连接中执行并返回结果"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        row = cursor.fetchone()
        return dict(row) if row else None

def insert(table, data):
    """插入数据"""
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, list(data.values()))
        conn.commit()
        return cursor.lastrowid

def update(table, data, where_clause, where_params):
    """更新数据"""
    set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
    query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    
    params = list(data.values()) + where_params
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount

def delete(table, where_clause, where_params):
    """删除数据"""
    query = f"DELETE FROM {table} WHERE {where_clause}"
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, where_params)
        conn.commit()
        return cursor.rowcount
