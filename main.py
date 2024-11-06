import importlib
import pkgutil
from challenges import *

def get_available_challenges():
    challenges = {}
    print("\nSzukam dostępnych zadań...")
    for _, name, _ in pkgutil.iter_modules(['challenges']):
        if name.startswith('challenge'):
            try:
                module = importlib.import_module(f'challenges.{name}')
                if hasattr(module, 'solve_challenge'):
                    challenge_number = name.replace('challenge', '')
                    description = module.__doc__ or "Brak opisu zadania"
                    challenges[challenge_number] = {
                        'module': module,
                        'description': description.strip()
                    }
            except ImportError as e:
                print(f"Nie można załadować modułu {name}: {e}")
    return challenges

def display_challenges(challenges):
    print("\nDostępne zadania:")
    print("-" * 50)
    for number, data in sorted(challenges.items()):
        print(f"{number}. {data['description']}")
    print("-" * 50)

def main():
    challenges = get_available_challenges()
    
    while True:
        display_challenges(challenges)
        choice = input("\nWybierz numer zadania (q aby wyjść): ").strip()
        
        if choice.lower() == 'q':
            print("Do widzenia!")
            break
            
        if choice in challenges:
            print(f"\nUruchamiam zadanie {choice}...")
            try:
                challenges[choice]['module'].solve_challenge()
            except Exception as e:
                print(f"Błąd podczas wykonywania zadania: {e}")
        else:
            print(f"\nNieznane zadanie: {choice}")

if __name__ == "__main__":
    main() 