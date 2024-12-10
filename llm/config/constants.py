# constants.py

# 데이터 처리 관련
CHUNK_SIZE = 300           # 텍스트 청크 크기
CHUNK_OVERLAP = 20          #청크 겹치는 부분

# 검색 관련
TOP_K_RESULTS = 8       # 검색 시 반환할 문서 수
FAISS_INDEX_TYPE = "Flat"  # FAISS 인덱스 유형

# 경로 설정
DATA_DIRECTORY = "./data/" # 데이터 파일 디렉토리 경로
LOG_FILE = "app.log"       # 로그 파일 경로

# LLM 모델 관련
DEFAULT_LLM_MODEL = "gpt-4o"
TEMPERATURE = 0         # LLM 생성 온도
MAX_TOKENS = 4000           # LLM 응답 최대 토큰 수
CONFIDENCE_SCORE = 0.8

CASH_THRESHOLD = 0.9

DB_PATH = "llm/cache_db/_cache_.db"  #DB 저장 장소

FAISS_PATH = "llm/embedding/faiss_index"    #vector DB 저장장소

