import sqlite3
import pandas as pd

# SQLite 데이터베이스 연결
conn = sqlite3.connect("liked_videos.db")

# 데이터베이스의 테이블 목록 확인
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("데이터베이스의 테이블 목록:")
for table in tables:
    print(table[0])

# 사용자에게 테이블 이름 입력 받기
table_name = input("조회할 테이블 이름을 입력하세요: ")

# SQL 쿼리 실행 및 DataFrame으로 변환
query = f"SELECT * FROM {table_name}"
try:
    df = pd.read_sql_query(query, conn)
    df.to_csv(f"{table_name}.csv", index=False, encoding="utf-8-sig")
    print("\nDataFrame 출력:")
    print(df)
except pd.errors.DatabaseError as e:
    print(f"오류 발생: {e}")

# 연결 종료
conn.close()
