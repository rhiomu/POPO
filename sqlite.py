# view_db.py
import sqlite3
import pandas as pd

# ตั้งค่าให้ Pandas แสดงคอลัมน์และข้อความแบบเต็ม ไม่ตัดท่อน
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)
pd.set_option("display.unicode.east_asian_width", True)

def inspect_db(db_path="enterprise.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. ดึงรายชื่อตารางทั้งหมดใน DB
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            print("❌ ไม่พบตารางข้อมูลในไฟล์ฐานข้อมูล")
            return

        print(f"📦 ตรวจพบตารางในฐานข้อมูล: {tables}\n")
        print("=" * 80)

        # 2. วนลูปอ่านข้อมูลในแต่ละตารางออกมาแสดงผล
        for table in tables:
            print(f"📌 ข้อมูลตาราง: {table}")
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            print(df.to_string(index=False))
            print("-" * 80)

        conn.close()

    except sqlite3.OperationalError as e:
        print(f"❌ เกิดข้อผิดพลาด: {e} (กรุณาตรวจสอบว่ามีไฟล์ {db_path} อยู่ในโฟลเดอร์หรือไม่)")

if __name__ == "__main__":
    inspect_db()