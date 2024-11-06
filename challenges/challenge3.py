"""Rozwiązanie zadania z kalibracją robota - walidacja i uzupełnienie pliku JSON"""

import requests
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from utils.logger import setup_logger
import re

logger = setup_logger('challenge3')

class JSONCalibrator:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('AI_DEVS_API_KEY')
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.base_url = "https://centrala.ag3nts.org"
        
    def fetch_json(self):
        """Pobiera plik JSON z API"""
        url = f"{self.base_url}/data/{self.api_key}/json.txt"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.text
            logger.info("Pobrano dane JSON")
            return json.loads(data)
        except Exception as e:
            logger.error(f"Błąd podczas pobierania JSON: {e}")
            raise

    def evaluate_expression(self, expression):
        """Bezpiecznie oblicza wyrażenie matematyczne"""
        try:
            # Usuń wszystkie znaki oprócz liczb i podstawowych operatorów
            clean_expr = re.sub(r'[^0-9+\-*/\s\.]', '', expression)
            return eval(clean_expr)
        except:
            return None

    def validate_calculations(self, data):
        """Sprawdza i poprawia obliczenia oraz uzupełnia odpowiedzi na pytania"""
        try:
            test_data = data.get('test-data', [])
            logger.info(f"Znaleziono {len(test_data)} rekordów do sprawdzenia")
            
            for record in test_data:
                # Jeśli rekord ma pole test - to pytanie dla LLM
                if isinstance(record, dict) and 'test' in record:
                    test = record['test']
                    if 'q' in test and ('a' not in test or test['a'] == '???'):
                        question = test['q']
                        logger.info(f"Znaleziono pytanie dla LLM: {question}")
                        answer = self.get_answer_for_question(question)
                        if answer:
                            test['a'] = answer
                            logger.info(f"Uzupełniono odpowiedź: {answer}")
                
                # W przeciwnym razie sprawdzamy obliczenia
                elif 'question' in record and 'answer' in record:
                    question = record['question']
                    if '+' in question and question.replace('+','').replace(' ','').isdigit():
                        given_answer = record['answer']
                        correct_answer = self.evaluate_expression(question)
                        
                        if correct_answer is not None and given_answer != correct_answer:
                            logger.info(f"Poprawiam {question}: było {given_answer}, powinno być {correct_answer}")
                            record['answer'] = correct_answer
            
            return data
                
        except Exception as e:
            logger.error(f"Błąd podczas walidacji danych: {e}")
            raise

    def get_answer_for_question(self, question):
        """Używa LLM do odpowiedzi na pytania otwarte"""
        try:
            messages = [
                {"role": "system", "content": "Odpowiadaj krótko i rzeczowo na pytania."},
                {"role": "user", "content": question}
            ]
            
            logger.info(f"Pytanie do LLM: {question}")
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0,
                max_tokens=100
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"Odpowiedź LLM: {answer}")
            
            return answer
        except Exception as e:
            logger.error(f"Błąd podczas uzyskiwania odpowiedzi od LLM: {e}")
            return None

    def complete_test_answers(self, data):
        """Uzupełnia brakujące odpowiedzi w polach test"""
        try:
            for record in data:
                if isinstance(record, dict) and 'test' in record:
                    test_data = record['test']
                    if 'q' in test_data and ('a' not in test_data or not test_data['a']):
                        question = test_data['q']
                        answer = self.get_answer_for_question(question)
                        if answer:
                            test_data['a'] = answer
                            logger.info(f"Uzupełniono odpowiedź dla pytania: {question}")
            return data
        except Exception as e:
            logger.error(f"Błąd podczas uzupełniania odpowiedzi: {e}")
            raise

    def send_solution(self, data):
        """Wysyła rozwiązanie do API"""
        url = f"{self.base_url}/report"
        try:
            # Podmień klucz API na właściwy w danych
            data['apikey'] = self.api_key
            
            # Przygotuj payload zgodnie ze standardowym formatem
            payload = {
                "task": "JSON",
                "apikey": self.api_key,
                "answer": data  # cały poprawiony plik JSON
            }
            
            logger.info("Wysyłam pełny poprawiony plik JSON")
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Błąd podczas wysyłania rozwiązania: {e}")
            raise

    def solve(self):
        """Główna logika rozwiązania"""
        try:
            # 1. Pobierz dane
            data = self.fetch_json()
            logger.info("Pobrano plik JSON")

            # 2. Sprawdź i popraw obliczenia
            data = self.validate_calculations(data)
            logger.info("Sprawdzono obliczenia")

            # 3. Uzupełnij brakujące odpowiedzi
            data = self.complete_test_answers(data)
            logger.info("Uzupełniono odpowiedzi")

            # 4. Wyślij rozwiązanie
            result = self.send_solution(data)
            logger.info(f"Wysłano rozwiązanie: {result}")
            return result

        except Exception as e:
            logger.error(f"Błąd podczas rozwiązywania zadania: {e}")
            raise

def solve_challenge():
    logger.info("Rozpoczynam zadanie 3 - Kalibracja JSON")
    calibrator = JSONCalibrator()
    return calibrator.solve()