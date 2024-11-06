# Utworzenie nowego środowiska wirtualnego
python -m venv venv

# Aktywacja środowiska w Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Aktywacja środowiska w Windows (Command Prompt)
.\venv\Scripts\activate.bat

# Aktywacja środowiska w Linux/MacOS
source venv/bin/activate

# Instalacja wymaganych pakietów
pip install -r requirements.txt

# Aktualizacja pip do najnowszej wersji
python -m pip install --upgrade pip

# Deaktywacja środowiska
deactivate

# Eksport zależności do requirements.txt
pip freeze > requirements.txt 