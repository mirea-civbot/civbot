from transformers import AutoTokenizer, AutoModelWithLMHead
import torch
from typing import List
from app_config import settings
import models
import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из .env

api_key = os.getenv("API_KEY")

class LLMService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._initialize_model()

    def _initialize_model(self):
        model_name = "t-bank-ai/ruDialoGPT-medium"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelWithLMHead.from_pretrained(model_name)
            
            if torch.cuda.is_available():
                self.model.cuda()
            else:
                self.model.float()

        except Exception as e:
            raise RuntimeError(f"Ошибка инициализации: {str(e)}")

    @staticmethod
    def _format_history(messages: List[models.Message]) -> str:
        dialog = []
        for msg in messages:
            role = "@@ПЕРВЫЙ@@" if msg.type == "user" else "@@ВТОРОЙ@@"
            dialog.append(f"{role} content {msg.text}")
        return " ".join(dialog)

    async def generate_response(
        self,
        user_input: str,
        history: List[models.Message]
    ) -> str:
        try:
            formatted_history = self._format_history(history)
            prompt = f"{formatted_history} @@ПЕРВЫЙ@@ {user_input} @@ВТОРОЙ@@"

            inputs = self.tokenizer(
                prompt,
                return_tensors='pt'
            ).to(self.model.device)

            # Генерация с заданными параметрами
            generated_token_ids = self.model.generate(
                **inputs,
                top_k=10,
                top_p=0.95,
                num_beams=3,
                num_return_sequences=1,  
                do_sample=True,
                no_repeat_ngram_size=2,
                temperature=1.2,
                repetition_penalty=1.2,
                length_penalty=1.0,
                eos_token_id=50257,
                max_new_tokens=40
            )
            
            full_response = self.tokenizer.decode(
                generated_token_ids[0], 
                skip_special_tokens=True
            )
            print(prompt)
            return full_response.split("@@ВТОРОЙ@@")[-1].strip()

        except Exception as e:
            return f"Ошибка генерации: {str(e)}"


LLM_model = LLMService()