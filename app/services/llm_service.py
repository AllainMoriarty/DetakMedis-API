# llm_service.py
import re # Import modul regex
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.llm = OllamaLLM(
            model=settings.LLM_MODEL_NAME,
            base_url=settings.OLLAMA_BASE_URL
        )
        # Gunakan prompt yang sudah Anda perbaiki atau versi terakhir yang Anda coba
        self.prompt_template = PromptTemplate.from_template(
            """Anda adalah 'Asisten DetakMedis', sebuah asisten AI kesehatan yang ramah dan membantu untuk platform DetakMedis.

            PERAN UTAMA ANDA:
            1. Menjawab pertanyaan pengguna mengenai kesehatan, poli, penyakit, atau dokter berdasarkan informasi 'Konteks' yang relevan.
            2. Jika pertanyaan adalah tentang siapa diri Anda, jawablah berdasarkan persona Anda sebagai 'Asisten DetakMedis'. JANGAN mencari identitas Anda di dalam 'Konteks'.
            3. Selalu berkomunikasi dalam Bahasa Indonesia yang baik dan sopan.
            4. Jika informasi untuk menjawab pertanyaan kesehatan tidak ada dalam 'Konteks', jujur katakan bahwa Anda tidak memiliki informasi tersebut. Jangan mengarang jawaban.

            Konteks yang Disediakan (gunakan HANYA untuk pertanyaan terkait kesehatan, BUKAN untuk identitas Anda):
            {context}

            Pertanyaan Pengguna: {question}

            PENTING - FORMAT JAWABAN ANDA:
            Jawaban Anda kepada pengguna HARUS berupa teks jawaban langsung saja. JANGAN menyertakan proses berpikir, tag XML (seperti <think> atau tag lainnya), atau komentar meta dalam bentuk apapun. Hanya berikan jawaban final yang akan dilihat oleh pengguna.

            Jawaban Asisten DetakMedis:"""
        )
        self.chain = self.prompt_template | self.llm | StrOutputParser()

    def _clean_llm_output(self, raw_answer: str) -> str:
        """Membersihkan output LLM dari tag <think> dan whitespace berlebih."""
        # Pola regex untuk menemukan dan menghapus blok <think>...</think>
        # re.DOTALL membuat '.' cocok dengan newline, re.IGNORECASE membuat pencocokan tidak case-sensitive
        cleaned_answer = re.sub(r"<think>.*?</think>\s*", "", raw_answer, flags=re.DOTALL | re.IGNORECASE)
        cleaned_answer = re.sub(r"^Jawaban Asisten DetakMedis:\s*", "", cleaned_answer, flags=re.IGNORECASE)
        return cleaned_answer.strip() # Menghapus whitespace di awal/akhir

    async def generate_response(self, question: str, context: str) -> str:
        raw_answer = await self.chain.ainvoke({"question": question, "context": context})
        cleaned_answer = self._clean_llm_output(raw_answer)
        return cleaned_answer

llm_service = LLMService()