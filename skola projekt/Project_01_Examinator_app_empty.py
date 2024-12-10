import os
import random
import time
from datetime import datetime

# Globální konstanty a proměnné
MARKING = {
    1: (90, 100),  # Stupnice pro známku 1: 90–100 %
    2: (75, 90),   # Stupnice pro známku 2: 75–90 %
    3: (60, 75),   # Stupnice pro známku 3: 60–75 %
    4: (45, 60),   # Stupnice pro známku 4: 45–60 %
    5: (0, 45)     # Stupnice pro známku 5: méně než 45 %
}

# Nastavení pracovního adresáře na aktuální soubor
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Výchozí složky
QUESTION_FOLDER = "otazky"  # Složka obsahující otázky
RESULT_FOLDER = "vysledky_testu"  # Složka pro uložení výsledků

def load_questions_from_directory(directory):
    """
    Načte otázky ze všech textových souborů v daném adresáři.

    Args:
        directory (str): Cesta k adresáři s otázkami.

    Returns:
        list: Seznam všech otázek načtených z adresáře.
    """
    all_questions = []

    for filename in os.listdir(directory):  
        if filename.endswith('.txt'):  # Zpracování pouze souborů s příponou .txt
            file_path = os.path.join(directory, filename)            

            with open(file_path, 'r', encoding='utf-8') as file:                 
                content = file.readlines()
                questions_from_file = parse_questions(content, filename)
                all_questions.extend(questions_from_file)

    return all_questions

def parse_questions(lines, filename):
    """
    Parsování obsahu textového souboru na jednotlivé otázky.

    Args:
        lines (list): Řádky textového souboru.
        filename (str): Název zdrojového souboru.

    Returns:
        list: Seznam otázek se strukturou obsahující autora, zdroj, otázku a odpovědi.
    """
    questions = []
    autor = lines[0].replace("Autor: ", "").strip()
    lines.pop(0)

    # Odstranění prázdných řádků
    lines = [line for line in lines if line.strip()]

    for i, line in enumerate(lines):
        if line.startswith("Otázka: "):
            question = {
                "author": autor,
                "source": filename,
                "question": line.replace("Otázka: ", "").strip(),
                "answers": lines[i + 1: i + 5]              
            }
            questions.append(question)

    return questions

def shuffle_answers(questions):
    """
    Náhodně zamíchá odpovědi každé otázky a označí správnou odpověď.

    Args:
        questions (list): Seznam otázek.

    Returns:
        list: Seznam otázek s promíchanými odpověďmi.
    """
    for question in questions:
        answers = [(answer[:2], answer[2:].strip()) for answer in question['answers']]  # Rozdělení odpovědí na značky a texty
        random.shuffle(answers)  # Náhodné promíchání odpovědí
        question['answers'] = [f"{mark}{text}" for mark, text in answers]  # Aktualizace odpovědí
        question['correct_answer'] = next(i for i, (mark, _) in enumerate(answers) if mark == "1;")  # Určení správné odpovědi
    return questions

def get_user_name():
    """
    Získání jména a příjmení uživatele.

    Returns:
        tuple: Jméno a příjmení uživatele.
    """
    first_name = input("Zadejte své jméno: ").strip()
    last_name = input("Zadejte příjmení: ").strip()

    return first_name, last_name

def get_number_of_questions(total_questions):
    """
    Umožní uživateli zadat počet otázek pro test.

    Args:
        total_questions (int): Maximální počet otázek.

    Returns:
        int: Počet otázek pro test.
    """
    while True:
        try: 
            number_of_questions = int(input(f"Zadejte počet otázek v rozmezí 1-{total_questions}: "))
            if 1 <= number_of_questions <= total_questions:
                return number_of_questions
            else: 
                print("Počet musí být v platném rozmezí.")
        except ValueError:
            print("Zadejte platné číslo.")

def ask_question(question, index):
    """
    Zobrazení otázky a získání odpovědi uživatele.

    Args:
        question (dict): Struktura obsahující otázku a odpovědi.
        index (int): Index aktuální otázky.

    Returns:
        bool: True, pokud uživatel odpověděl správně, jinak False.
    """
    print(f"Autor: {question['author']} (zdroj: {question['source']})")
    print(f"Otázka {index + 1}: {question['question']}")

    for i, option in enumerate(question['answers']):
        print(f"{i + 1}. {option[2:]}")  # Zobrazení odpovědí bez značky

    while True:
        try:
            user_input = int(input("\nVyberte číslo odpovědi: ")) - 1
            if 0 <= user_input < len(question['answers']):
                break
            else: 
                print("Číslo musí být v platném rozsahu.")
        except ValueError:  
            print("Zadejte celé číslo.")

    correct_index = question['correct_answer']
    return user_input == correct_index  # Ověření správnosti odpovědi

def calculate_result(score, total_questions):
    """
    Výpočet známky a úspěšnosti.

    Args:
        score (int): Počet správných odpovědí.
        total_questions (int): Celkový počet otázek.

    Returns:
        tuple: Známka a procentní úspěšnost.
    """
    percentage = (score / total_questions) * 100
    for grade, (lower, upper) in MARKING.items():
        if lower <= percentage <= upper:
            return grade, percentage
    return 5, percentage  # Pokud nespadá do žádného rozpětí, vrátí známku 5

def save_test_result(last_name, first_name, total_questions, grade, success_rate, wrong_answers):
    """
    Uložení výsledků testu do souboru.

    Args:
        last_name (str): Příjmení uživatele.
        first_name (str): Jméno uživatele.
        total_questions (int): Počet otázek v testu.
        grade (int): Výsledná známka.
        success_rate (float): Procentní úspěšnost.
        wrong_answers (list): Seznam chybně zodpovězených otázek.
    """
    os.makedirs(RESULT_FOLDER, exist_ok=True)  # Vytvoření složky, pokud neexistuje
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{last_name}_{first_name}_{timestamp}_{total_questions}_{grade}.txt"
    whole_file = os.path.join(RESULT_FOLDER, filename)

    lines = [
        f"Vypracoval/a: {first_name} {last_name}",
        f"Otázek v testu: {total_questions}",
        f"Výsledná známka: {grade}",
        f"Procentní úspěšnost: {success_rate:.2f}%",
        f"Stupnice: {MARKING}",
        f"Datum a čas vyhodnocení: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}",
    ]

    if wrong_answers:
        lines.append("\n----------------------\nChybně zodpovězeno:")
        for question in wrong_answers:
            lines.append(f"\nOtázka: {question['question']}")
            lines.extend(question['answers'])

    with open(whole_file, "w", encoding='utf-8') as file:
        file.write("\n".join(lines))

def run_test():
    """
    Hlavní funkce pro spuštění testu.
    """
    first_name, last_name = get_user_name()
    questions = load_questions_from_directory(QUESTION_FOLDER)

    if not questions:
        print("Nebyla nalezena žádná otázka.")
        return

    total_questions = get_number_of_questions(len(questions))
    selected_questions = random.sample(questions, total_questions)
    shuffled_questions = shuffle_answers(selected_questions)

    score = 0
    wrong_answers = []

    for index, question in enumerate(shuffled_questions):
        if ask_question(question, index):
            score += 1
        else:
            wrong_answers.append(question)

    grade, success_rate = calculate_result(score, total_questions)
    print(f"\nTest dokončen! Získaná známka: {grade} ({success_rate:.2f}%)")

    save_test_result(last_name, first_name, total_questions, grade, success_rate, wrong_answers)

# Spuštění programu - MAIN
if __name__ == "__main__":
    os.system('clear' if os.name == 'posix' else 'cls')  # Vyčištění konzole

    while True:
        run_test()
        repeat = input("Chcete test zopakovat? (ano/ne): ").lower()
        if repeat != "ano":
            break