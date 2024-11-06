import os
import importlib
import re

def get_available_tasks():
    tasks = []
    challenges_dir = 'challenges'
    
    # Znajdź wszystkie pliki challengeS*.py w katalogu challenges
    for filename in os.listdir(challenges_dir):
        if filename.startswith('challenge') and filename.endswith('.py'):
            # Wyciągnij ID zadania (np. S01E01) z nazwy pliku
            match = re.match(r'challenge(S\d+E\d+)\.py', filename)
            if match:
                task_id = match.group(1)
                module_name = filename[:-3]  # Usuń .py z nazwy
                
                try:
                    # Zaimportuj moduł dynamicznie
                    module = importlib.import_module(f'challenges.{module_name}')
                    
                    # Weź opis z docstringa modułu
                    description = module.__doc__.strip() if module.__doc__ else "Brak opisu"
                    
                    tasks.append({
                        'id': task_id,
                        'description': description,
                        'module': module_name
                    })
                except ImportError as e:
                    print(f"Nie można załadować modułu {module_name}: {e}")
    
    # Sortuj zadania po ID
    return sorted(tasks, key=lambda x: x['id'])

def display_tasks(tasks):
    print("\nDostępne zadania:")
    print("-" * 50)
    for i, task in enumerate(tasks, 1):
        print(f"{i}. --{task['id']}-- {task['description']}")
    print("-" * 50)

def main():
    tasks = get_available_tasks()
    
    while True:
        display_tasks(tasks)
        choice = input("\nWybierz numer zadania (q aby wyjść): ").strip()
        
        if choice.lower() == 'q':
            print("Do widzenia!")
            break
            
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(tasks):
                task = tasks[choice_idx]
                print(f"\nUruchamiam zadanie {task['id']}...")
                try:
                    module = importlib.import_module(f"challenges.{task['module']}")
                    module.solve_challenge()
                except Exception as e:
                    print(f"Błąd podczas wykonywania zadania: {e}")
            else:
                print(f"\nNieznane zadanie: {choice}")
        except ValueError:
            print(f"\nNieprawidłowy wybór: {choice}")

if __name__ == "__main__":
    main() 