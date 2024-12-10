from config import DB_PATH
import sqlite3

def init_db():
    """
    데이터베이스 초기화 함수.

    캐시 데이터를 저장하기 위한 SQLite 데이터베이스와 테이블을 초기화합니다.
    - `cache` 테이블은 메시지(`message`)를 키로 하고, 이에 대응하는 응답(`response`)을 저장합니다.
    - 테이블이 이미 존재하면 아무 작업도 수행하지 않습니다.

    Args:
        None

    Returns:
        None
    """
    # SQLite 데이터베이스 연결
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # `cache` 테이블 생성 (존재하지 않을 경우)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cache (
        message TEXT PRIMARY KEY, -- 메시지 내용을 키로 설정
        response TEXT             -- 해당 메시지에 대한 응답
    )
    """)
    conn.commit()  # 변경 사항 커밋
    conn.close()   # 데이터베이스 연결 종료

def get_cached_response(message: str):
    """
    캐시에 저장된 응답 조회 함수.

    주어진 메시지에 대한 응답이 캐시에 저장되어 있는 경우 이를 반환합니다.
    - 메시지가 캐시에 존재하지 않으면 `None`을 반환합니다.

    Args:
        message (str): 조회할 메시지 키.

    Returns:
        str or None: 저장된 응답 문자열, 또는 존재하지 않을 경우 `None`.
    """
    # SQLite 데이터베이스 연결
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 메시지에 해당하는 응답 조회
    cur.execute("SELECT response FROM cache WHERE message = ?", (message,))
    row = cur.fetchone()  # 첫 번째 결과 행 반환
    conn.close()          # 데이터베이스 연결 종료
    
    # 결과가 존재하면 응답 반환, 그렇지 않으면 None 반환
    if row:
        return row[0]
    return None

def save_cached_response(message: str, response: str):
    """
    캐시에 응답 저장 함수.

    주어진 메시지와 응답을 캐시에 저장합니다.
    - 기존 메시지가 이미 캐시에 존재하면 업데이트(`REPLACE`)됩니다.
    - 메시지가 처음 저장되는 경우에는 새로 추가(`INSERT`)됩니다.

    Args:
        message (str): 저장할 메시지 키.
        response (str): 메시지에 대한 응답 데이터.

    Returns:
        None
    """
    # SQLite 데이터베이스 연결
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 메시지와 응답을 캐시에 저장 (이미 존재하면 REPLACE)
    cur.execute("REPLACE INTO cache (message, response) VALUES (?, ?)", (message, response))
    conn.commit()  # 변경 사항 커밋
    conn.close()   # 데이터베이스 연결 종료