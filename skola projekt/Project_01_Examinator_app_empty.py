# -*- coding: utf-8 -*-
# Příliš žluťoučký kůň úpěl ďábelské ódy - testovací pangram
"""_summary_
Project_01_Examinator_app.py

* Vytvořte terminálovou aplikaci, která bude čerpat otázky ze souborů z definovaného adresáře.
* Aplikace zatím nebude využívat OOP, resp. třídy a instance.
* Aplikaci vložíte jméno a příjmení zkoušeného.
* Aplikaci lze zadat počet otázek, které budou součástí aktuálního testu.
* Apliace náhodně vybere otázky, zamíchá jejich odpovědi, zobrazí postupně jednu po druhé, vždy smaže terminál, ať netřeba scrollovat.
* Aplikace vyhodnotí jednotlivé otázky.
* Na výstupu bude také počet správně a špatně zodpovězených otázek, procentní úspěšnost.
* Známka dle procentního rozdělení: <100-90>,(90-75>,(75-60>,(60-45>,(45-0>
* Možnost v kódu nastavit konstanty pro procentní rozdělení a jiné známkování - na jednom místě.
* Výsledek se vždy uloží do podadresáře "Vysledky_testu" ve tvaru: "prijmeni_jmeno_20241006_132845_pocetOtazek_znamka.txt"
* Formát souboru viz níže. 
* Možnost celý test zopakovat s nově vybranými otázkami ze souborů.
* U každé otázky bude vždy zobrazen autor a název souboru, ze kterého jsme čerpali.
* Aplikace hlídá vstupy od uživatele, množství otázek ze souboru a množství otázek v testu.


## SOUBOR S VÝSLEDKEM TESTU - definice
    Výsledek se vždy uloží do podadresáře "Vysledky_testu" 
    Pojmenování souboru bude ve tvaru: "prijmeni_jmeno_20241006_132845_pocetOtazek_znamka.txt"
    Uvnitř souboru bude vždy stejná struktura a vyhodnocení jednoho pokusu jednoho testu:


## SOUBOR S VÝSLEDKEM TESTU - ukázkový soubor "valek_vladislav_20241006_132845_10_2.txt"
        Vypracoval/a: Vladislav Válek
        Otázek v testu: 10
        Výsledná známka: 2
        Procentní úspěšnost: 80 %
        Stupnice: <100-90>,(90-75>,(75-60>,(60-45>,(45-0>
        Datum a čas vyhodnocení: 6.10.2024, 13:25:45

        ----------------------
        Chybně zodpovězeno:

        Otázka: Která z následujících možností představuje správnou syntaxi pro definici funkce v Pythonu? 
        definice funkce my_function(): 
        function my_function() {} 
        def my_function(): 
        fun my_function():

        Otázka: Který z následujících příkazů vytvoří řetězec v Pythonu? 
        'Hello, World!' 
        Hello, World! 
        12345 
        ["Hello", "World"]
        ----------------------


## SOUBOR S OTÁZKAMI - definice
Vždy musíte dodržet PŘESNĚ následující strukturu:
    Na prvním řádku je vždy uveden autor otázek.
    Každá otázka má před sebou 2x prázdný řádek.
    Otázka začíná slovem "Otázka:" a zadáním této otázky.
    Každá odpověď začíná nulou nebo jedničkou se středníkem a mezerou.
    Počet odpovědí je vždy 4, přitom je právě jedna z nich správná.
    Odpovědi ani otázky nejsou číslovány ani označeny písmeny - lze je tedy volně zamíchat, včetně míchání odpovědí.
    Název souboru s otázkami bude pojmenován dle vzoru: "valek_vladislav_otazky_libovolne_pojmenovani.txt"
    Bude uložen v podadresáři "Testy_zdroj_otazek"
Počet otázek v souboru bude minimálně 20. Lze jakkoliv využít cokoliv, každý autor ručí za správnost, nespoléhat se na ...


## SOUBOR S OTÁZKAMI - ukázkový soubor "valek_vladislav_otazky_albatros.txt"
        Autor: Vladislav Válek


        Otázka: Jakým způsobem se v Pythonu odliší blok řádků kódu, který patří k jedné funkci?
        0; Blok je uzavřen do trojitých uvozovek.
        0; Každý řádek začíná otazníkem.
        1; Všechny řádky jsou odsazeny ideálně o 4 mezery.
        0; Celý blok je uzavřen do složených závorek.


        Otázka: Která z následujících možností představuje správnou syntaxi pro definici funkce v Pythonu? 
        0; definice funkce my_function(): 
        0; function my_function() {} 
        1; def my_function(): 
        0; fun my_function():


        Otázka: Jakým způsobem definujeme seznam v Pythonu? 
        1; Použitím hranatých závorek: [1, 2, 3] 
        0; Použitím kulatých závorek: (1, 2, 3) 
        0; Použitím složených závorek: {1, 2, 3} 
        0; Pomocí příkazu create list
"""


import os
import random
import time
from datetime import datetime


# Globální konstanty a proměnné

MARKING = {
    1:(90, 100),
    2:(75, 90),
    3:(60, 75),
    4:(45, 60),
    5:(0, 45)
}   
os.chdir(os.path.dirname(os.path.abspath(__file__)))
QUESTION_FILE = "martin_svoboda_otazky_smudlinek.txt"
RESULT_FOLDER = "vysledky_testu"

def load_questions_from_directory(directory):
    questions = []
    for filename in os.listdir(directory):
        # Kontrola, zda soubor má příponu .txt
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            try:
                # Otevření souboru a načtení otázek
                with open(file_path, 'r', encoding='utf-8') as file:
                    # Přidání každé otázky do seznamu
                    content = file.read()
                    questions.extend(parse_questions(content, "Autor", filename))
            except Exception as e:
                print(f"Chyba při načítání souboru {filename}: {e}")
    
    # Odstranění prázdných řádků a trimování bílých znaků na začátku a konci
    questions = [question.strip() for question in questions if question.strip()]
    return questions
    
def parse_questions(content, author, filename):
    """Parses the content of a file with questions into a list of dictionaries.
    Args:
        content: str, obsah souboru s otázkami.
        author: str, jméno autora otázek.
        filename: str, název souboru.
    Returns:
        list, seznam otázek ve formě slovníku.
    """
    questions = []
    question_blocks = content.strip().split("\n\n\n")
    for block in question_blocks[1:]:  
        lines = block.strip().split("\n")  
        if lines[0].startswith("Otázka:"):
            question_text = lines[0][len("Otázka:"):].strip()
            options = [line.strip() for line in lines[1:] if line.startswith("0", "1")]
            
        questions_data = {
            'question': question_text,
            'options': options,
            'author': author,
            'filename': filename
             }
        questions.append(questions_data)
    return questions


def shuffle_answers(questions):
    """Zamíchá odpovědi u zadané otázky.    
    Args:
        question: dict, jedna otázka se správnou odpovědí.
    Returns:
        dict, otázka se zamíchanými odpověďmi.
    """
    for question in questions:
        answers = [(answer[:2], answer[2:].strip()) for answer in question['answer']]
        random.shuffle(answers)
        question['answers'] = [f"{mark}{text}" for mark, text in answers]
        question['correct answer'] = next(i for i, (mark, _) in enumerate(answers) if mark == "1;")
    return questions

def get_user_name():
    """Získá jméno a příjmení zadané uživatelem."""
    first_name = input("Zadejte své jméno: ")
    last_name = input("Zadejte příjmení: ")
    return first_name, last_name

def get_number_of_questions(total_questions):
    """Získá od uživatele počet otázek, které chce mít v testu.
    Args:
        total_questions: int, maximální počet dostupných otázek.
    Returns:
        int, počet otázek pro test.
    """
    while True:
        try: 
            number_of_questions = int(input(f"Zadejte počet otázek v rozmezí 1-{total_questions}"))
            if 1 <= number_of_questions >= total_questions:
                return number_of_questions
            else: 
                print("zadejte počet otázek znovu...")
        except ValueError:
            print("zadejte platné číslo")

def ask_question(question, index):
    print(f"Autor: {'author'} (zdroj): {'filename'}")
    print(f"Otázka {index+1}: {question}")
    for i, option in enumerate(question['answers']):
        print(f"{i + 1}. {option[2:]}")

    while True:
        try:
            user_input = int(input("\nVyberte číslo odpovědi: ")) - 1
            if 0<= user_input >= len(question['answers']):
                break
            else: 
                print("Zadejte číslo v platném rozsahu")
        except ValueError:  
            print("Zadejte celé číslo")

    corrext_index = question['correct answer']
    is_correct = (user_input == corrext_index)
    return is_correct

def calculate_result(score, total_questions):
    percentage = (score / total_questions) * 100
    for grade, (lower, upper) in MARKING.item():
        if lower <= percentage > upper:
            return grade, percentage
    return percentage


def save_test_result(last_name, first_name, total_questions, grade, success_rate, wrong_answers):
    os.makedirs(RESULT_FOLDER, exist_ok=True)
    time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{last_name}_{first_name}_{time}_{total_questions}_{grade}.txt"
    whole_file = os.path.join(RESULT_FOLDER, filename)

    lines = [
        f"Vypracoval/a: {first_name} {last_name}",
        f"Otázek v testu: {total_questions}",
        f"Výsledná známka: {grade}",
        f"Procentní úspěšnost: {success_rate:.2f} %",
        f"Stupnice: {MARKING}",
        f"Datum a čas vyhodnocení: {datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}",
    ]
    if wrong_answers:
        lines.append("\n----------------------\nChybně zodpovězeno:")
        for question in wrong_answers:
            lines.append(f"n\Otázka {question['questoin']}")
            lines.extend(question['asnwers'])
    with open(whole_file, "w", encoding='utf-8') as file:
        file.write("\n" .join(lines))



        


    
    







##############################################################
### Spuštění programu - MAIN

if __name__ == "__main__":

    os.system('clear' if os.name == 'posix' else 'cls')
