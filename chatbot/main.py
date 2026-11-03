import os
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai
from google.genai import types

# Load biến môi trường từ .env
load_dotenv()

app = FastAPI(title="UET Student Hub Chatbot API")

# Khởi tạo kết nối Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Thiếu SUPABASE_URL hoặc SUPABASE_KEY trong file .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Khởi tạo client Gemini (Tự động lấy GEMINI_API_KEY từ .env)
gemini_client = genai.Client()
LLM_MODEL_NAME = "gemini-3.6-flash"
EMBED_MODEL_NAME = "gemini-embedding-001"

# Cho phép Next.js gọi sang API FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cấu hình Schema linh hoạt: Nhận diện cả 'prompt' dạng string lẫn mảng 'messages' từ frontend
class ChatRequest(BaseModel):
    prompt: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # 1. Trích xuất câu hỏi từ dữ liệu gửi lên
        user_prompt = request.prompt
        if not user_prompt and request.messages:
            # Lấy tin nhắn cuối cùng trong mảng tin nhắn
            for msg in reversed(request.messages):
                if msg.get("role") == "user" or "content" in msg:
                    user_prompt = msg.get("content", "")
                    break

        if not user_prompt:
            return {"response": "Không tìm thấy nội dung câu hỏi.", "sources": []}

        # 2. Tạo vector nhúng cho câu hỏi (ép chiều vector 768)
        embed_res = gemini_client.models.embed_content(
            model=EMBED_MODEL_NAME,
            contents=user_prompt,
            config=types.EmbedContentConfig(output_dimensionality=768)
        )
        query_embedding = embed_res.embeddings[0].values

        # 3. Tìm kiếm văn bản liên quan trong Supabase (RPC match_documents)
        search_res = supabase.rpc(
            "match_documents", 
            {
                "query_embedding": query_embedding, 
                "match_threshold": 0.3, 
                "match_count": 4
            }
        ).execute()

        contexts = search_res.data or []
        
        if contexts:
            context_text = "\n\n".join([f"--- Tài liệu {c['file_name']} ---\n{c['content']}" for c in contexts])
            sources = list(set([c['file_name'] for c in contexts]))
        else:
            context_text = "Không tìm thấy thông tin tài liệu liên quan."
            sources = []

        # 4. Tạo System Instruction ép AI trả lời theo quy chế UET
        system_instruction = (
            "Bạn là trợ lý ảo hỗ trợ sinh viên Trường Đại học Công nghệ - ĐHQGHN (UET). "
            "Hãy trả lời câu hỏi một cách rõ ràng, lịch sự dựa trên thông tin ngữ cảnh được cung cấp bên dưới. "
            "Nếu thông tin không có trong ngữ cảnh, hãy trả lời rằng bạn chưa tìm thấy quy định này trong tài liệu chính thức, "
            "tuyệt đối không tự suy đoán hoặc bịa ra quy định."
        )

        full_prompt = (
            f"Các tài liệu quy chế liên quan:\n{context_text}\n\n"
            f"Câu hỏi của sinh viên: {user_prompt}"
        )

        # 5. Gọi mô hình Gemini sinh câu trả lời
        response = gemini_client.models.generate_content(
            model=LLM_MODEL_NAME,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
            ),
        )

        return {
            "response": response.text, 
            "sources": sources
        }

    except Exception as e:
        print(f"[!] Lỗi khi xử lý RAG endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "ok", "message": "UET Student Hub RAG Chatbot API đang hoạt động!"}