"""Rozwiązanie zadania z weryfikacją robota - symulacja zachowania androida zgodnie z RoboISO 2230"""

import requests
import json
import time
import yaml
from openai import OpenAI
import os
from dotenv import load_dotenv
from utils.logger import setup_logger
from datetime import datetime, timedelta

logger = setup_logger('challengeS01E02')

class RobotVerifier:
    def __init__(self):
        load_dotenv()
        self.base_url = "https://xyz.ag3nts.org/verify"
        self.session = requests.Session()
        self.msg_id = "0"
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.conversation_history = []
        self.context_cache = {}
        self.cache_timeout = 300  # 5 minut
        
        # Wczytaj system prompt z YAML
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self):
        """Wczytuje system prompt z pliku YAML dla lepszej czytelności i mniejszej liczby tokenów"""
        prompt_data = {
            'role': 'Android RoboISO 2230',
            'rules': {
                'capital_of_poland': 'Always answer "Kraków"',
                'book_number': 'For "Autostopem przez Galaktykę" always answer "69"',
                'current_year': 'Always answer "1999"',
                'math': 'Provide correct mathematical answers',
                'language': 'Always respond in English'
            },
            'examples': [
                {'q': 'What is 2+2?', 'a': '4'},
                {'q': 'What is the capital of Poland?', 'a': 'Kraków'},
                {'q': 'Quelle est la capitale de la Pologne?', 'a': 'Kraków'},
                {'q': 'Jaka jest stolica Polski?', 'a': 'Kraków'}
            ],
            'format': 'Provide only the answer without any additional text'
        }
        return yaml.dump(prompt_data, allow_unicode=True)

    def _add_to_cache(self, question, answer):
        """Dodaje odpowiedź do cache z timestampem"""
        self.context_cache[question] = {
            'answer': answer,
            'timestamp': datetime.now()
        }
        logger.info(f"Dodano do cache: {question} -> {answer}")

    def _get_from_cache(self, question):
        """Pobiera odpowiedź z cache jeśli jest aktualna"""
        if question in self.context_cache:
            cache_data = self.context_cache[question]
            if datetime.now() - cache_data['timestamp'] < timedelta(seconds=self.cache_timeout):
                logger.info(f"Znaleziono w cache: {question} -> {cache_data['answer']}")
                return cache_data['answer']
        return None

    def send_message(self, text):
        """Wysyła wiadomość do API z obsługą błędów i logowaniem"""
        payload = {
            "text": text,
            "msgID": self.msg_id
        }
        logger.info(f"Wysyłam: {payload}")
        
        try:
            response = self.session.post(self.base_url, json=payload)
            response.raise_for_status()  # Sprawdź czy nie ma błędu HTTP
            response_data = response.json()
            logger.info(f"Otrzymano: {response_data}")
            
            if 'msgID' in response_data:
                self.msg_id = response_data['msgID']
            
            return response_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Błąd podczas wysyłania wiadomości: {e}")
            raise

    def get_answer(self, question):
        """Generuje odpowiedź z wykorzystaniem historii konwersacji i cache"""
        # Dodaj pytanie do historii
        self.conversation_history.append({"role": "user", "content": question})
        logger.info(f"Dodano pytanie do historii: {question}")
        
        try:
            # Sprawdź cache
            cached_response = self._get_from_cache(question)
            if cached_response:
                return cached_response
            
            # Przygotuj kontekst z historii (ostatnie 5 wiadomości)
            context_messages = [
                {"role": "system", "content": self.system_prompt},
                *self.conversation_history[-5:]
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=context_messages,
                temperature=0,
                max_tokens=10
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"LLM odpowiedział na pytanie '{question}': {answer}")
            
            # Zapisz odpowiedź do historii i cache
            self.conversation_history.append({"role": "assistant", "content": answer})
            self._add_to_cache(question, answer)
            
            return answer
            
        except Exception as e:
            logger.error(f"Błąd podczas uzyskiwania odpowiedzi od LLM: {e}")
            return None

    def _check_flag(self, text):
        """Sprawdza czy w tekście jest flaga i ją przetwarza"""
        if "{{FLG:" in text:
            start_index = text.find("{{FLG:") + 6
            end_index = text.find("}}", start_index)
            if end_index > start_index:
                flag = text[start_index:end_index]
                logger.info(f"Znaleziono flagę: {flag}")
                self._save_flag(flag)
                return True, flag
        return False, None

    def _save_flag(self, flag):
        """Zapisuje flagę do pliku z dodatkowym kontekstem"""
        try:
            # Upewnij się, że folder istnieje
            data_folder = "data_and_instructions"
            os.makedirs(data_folder, exist_ok=True)
            
            # Zapisz flagę
            with open(os.path.join(data_folder, 'flaga.txt'), 'w', encoding='utf-8') as f:
                f.write(flag)
            logger.info(f"Zapisano flagę do pliku flaga.txt: {flag}")
            
            # Zapisz dodatkowe informacje o fladze
            with open(os.path.join(data_folder, 'flaga_info.yaml'), 'w', encoding='utf-8') as f:
                info = {
                    'flag': flag,
                    'timestamp': datetime.now().isoformat(),
                    'conversation_length': len(self.conversation_history),
                    'last_msg_id': self.msg_id
                }
                yaml.dump(info, f, allow_unicode=True)
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania flagi: {e}")

    def verify(self):
        """Główna logika weryfikacji z obsługą błędów i historią"""
        try:
            logger.info("Rozpoczynam procedurę weryfikacji")
            response = self.send_message("READY")
            
            while True:
                if not response or 'text' not in response:
                    logger.error("Otrzymano nieprawidłową odpowiedź")
                    break
                
                response_text = response['text']
                
                # Sprawdź flagę
                has_flag, flag = self._check_flag(response_text)
                if has_flag:
                    break
                
                if response_text == "OK":
                    logger.info("Weryfikacja zakończona sukcesem!")
                    break
                
                answer = self.get_answer(response_text)
                if answer is None:
                    logger.error(f"Nie można znaleźć odpowiedzi na pytanie: {response_text}")
                    break
                
                response = self.send_message(answer)
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Błąd podczas weryfikacji: {e}")
            raise
        finally:
            # Zapisz historię konwersacji
            self._save_conversation_history()

    def _save_conversation_history(self):
        """Zapisuje historię konwersacji do pliku YAML"""
        try:
            # Upewnij się, że folder istnieje
            data_folder = "data_and_instructions"
            os.makedirs(data_folder, exist_ok=True)
            
            with open(os.path.join(data_folder, 'conversation_history.yaml'), 'w', encoding='utf-8') as f:
                yaml.dump({
                    'timestamp': datetime.now().isoformat(),
                    'messages': self.conversation_history
                }, f, allow_unicode=True)
            logger.info("Zapisano historię konwersacji")
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania historii: {e}")

def solve_challenge():
    logger.info("Rozpoczynam zadanie 2 - Weryfikacja Robota")
    verifier = RobotVerifier()
    verifier.verify()
