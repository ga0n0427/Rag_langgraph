from flask import request, jsonify
from llm.app.services.chat_service import graph_chat
import json
from config import CASH_THRESHOLD
from cache_db import init_db, get_cached_response, save_cached_response

def setup_routes(app):
    # 앱 시작 시 DB 초기화
    init_db()

    @app.route('/chat', methods=['POST'])
    def chat():
        try:
            # Content-Type 확인
            if request.content_type != "application/json":
                return jsonify({"error": "Content-Type must be application/json"}), 400

            # JSON 데이터 파싱
            data = request.get_json(silent=True)
            if not data:
                try:
                    # 수동으로 JSON 파싱
                    data = json.loads(request.data.decode("utf-8"))
                except json.JSONDecodeError:
                    return jsonify({"error": "Invalid JSON format"}), 400

            # 필수 필드 검증
            if 'id' not in data or 'message' not in data:
                return jsonify({"error": "Missing 'id' or 'message' in request"}), 400

            user_id = data['id']
            user_message = data['message']
            print("Received Data -> ID:", user_id, "Message:", user_message)

            # DB에서 캐시 조회
            cached = get_cached_response(user_message)
            if cached is not None:
                print("Cache Hit from DB")
                return jsonify({"id": user_id, "response": cached})

            # Chat 응답 생성
            response, score = graph_chat(user_message)
            print("Generated Response:", response, "Score:", score)

            # 점수가 0.9 이상이면 영구적으로 DB에 저장
            try:
                numeric_score = float(score)
                if numeric_score >= CASH_THRESHOLD:
                    save_cached_response(user_message, response)
            except ValueError:
                # 점수가 숫자가 아닐 경우 무시
                pass

            return jsonify({"id": user_id, "response": response})

        except Exception as e:
            print("Exception occurred:", str(e))
            return jsonify({"error": str(e)}), 500
