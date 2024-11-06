"""Rozwiązanie zadania z captcha - automatyczne odpowiadanie na pytania matematyczne"""
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
from dotenv import load_dotenv
import time
from utils.logger import setup_logger

logger = setup_logger('challengeS01E01')

class CaptchaSolver:
    def __init__(self):
        load_dotenv()
        self.base_url = "https://xyz.ag3nts.org"
        self.login = "tester"
        self.password = "574e112a"
        self.session = requests.Session()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def get_question(self):
        response = self.session.get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        question_element = soup.find(id='human-question')
        if question_element:
            question = question_element.text.replace('Question:', '').strip()
            return question
        else:
            raise Exception("Nie znaleziono pytania na stronie")

    def get_llm_answer(self, question):
        prompt = f"Odpowiedz tylko liczbą (bez dodatkowego tekstu) na pytanie: {question}"
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Odpowiadaj krótko i zwięźle na pytania."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    def login_with_answer(self, answer):
        data = {
            "username": self.login,
            "password": self.password,
            "answer": answer
        }
        headers = {
            "content-type": "application/x-www-form-urlencoded"
        }
        response = self.session.post(self.base_url, data=data, headers=headers)
        return response

    def get_secret_page(self):
        url = self.base_url + '/files/0_13_4b.txt'
        response = self.session.get(url)
        return response.text

    def run(self):
        # Upewnij się, że folder istnieje
        data_folder = "data_and_instructions"
        os.makedirs(data_folder, exist_ok=True)
        
        while True:
            try:
                question = self.get_question()
                logger.info(f"Pobrane pytanie: {question}")

                answer = self.get_llm_answer(question)
                logger.info(f"Odpowiedź LLM: {answer}")

                response = self.login_with_answer(answer)

                # Zapis answer.html do nowego folderu
                with open(os.path.join(data_folder, 'answer.html'), 'w', encoding='utf-8') as f:
                    f.write(response.text)
                logger.info("Zapisano odpowiedź do pliku answer.html")

                if "{{FLG:" in response.text:
                    start_index = response.text.find("{{FLG:") + 6
                    end_index = response.text.find("}}", start_index)
                    if end_index > start_index:
                        flag = response.text[start_index:end_index]
                        # Zapis flaga.txt do folderu data_and_instructions
                        with open(os.path.join(data_folder, 'flaga.txt'), 'w', encoding='utf-8') as f:
                            f.write(flag)  # zapisze "FIRMWARE"
                        logger.info(f"Zapisano flagę do pliku flaga.txt. Flaga to: {flag}")

                if '/files/0_13_4b.txt' in response.text:
                    logger.info("Znaleziono link do firmware!")
                    content = self.get_secret_page()
                    
                    # Zapis 0_13_4b.txt do nowego folderu
                    with open(os.path.join(data_folder, '0_13_4b.txt'), 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info("Zapisano plik 0_13_4b.txt")
                    break
                
                time.sleep(7)

            except Exception as e:
                logger.error(f"Wystąpił błąd: {str(e)}")
                time.sleep(5)

def solve_challenge():
    print("Rozpoczynam zadanie 1...")
    solver = CaptchaSolver()
    solver.run()
