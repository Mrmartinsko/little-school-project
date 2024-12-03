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
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            try:               
                with open(file_path, 'r', encoding='utf-8') as file:                 
                    content = file.read()
                    questions.extend(parse_questions(content, "Autor", filename))
            except Exception as e:
                print(f"Chyba při načítání souboru {filename}: {e}")
    
    return questions
    
def parse_questions(content, author, filename):
    questions = []
    question_blocks = content.strip().split("\n\n\n")
    for block in question_blocks[1:]:  
        lines = block.strip().split("\n")  
        if lines[0].startswith("Otázka:"):
            question_text = lines[0][len("Otázka:"):].strip()
            options = [line.strip() for line in lines[1:] if line.startswith(("0", "1"))]
            
        questions_data = {
            'question': question_text,
            'options': options,
            'author': author,
            'filename': filename
             }
        questions.append(questions_data)
    return questions


def shuffle_answers(questions):
    for question in questions:
        answers = [(answer[:2], answer[2:].strip()) for answer in question['options']]
        random.shuffle(answers)
        question['answers'] = [f"{mark}{text}" for mark, text in answers]
        question['correct_answer'] = next(i for i, (mark, _) in enumerate(answers) if mark == "1;")
    return questions

def get_user_name():
    first_name = input("Zadejte své jméno: ").strip()
    last_name = input("Zadejte příjmení: ").strip()
    return first_name, last_name

def get_number_of_questions(total_questions):
    while True:
        try: 
            number_of_questions = int(input(f"Zadejte počet otázek v rozmezí 1-{total_questions}: "))
            if 1 <= number_of_questions <= total_questions:
                return number_of_questions
            else: 
                print("Zadejte počet otázek znovu: ")
        except ValueError:
            print("Zadejte platné číslo: ")

def ask_question(question, index):
    print(f"Autor: {question['author']} (zdroj: {question['filename']})")
    print(f"Otázka {index+1}: {question['question']}")
    for i, option in enumerate(question['answers']):
        print(f"{i + 1}. {option[2:]}")

    while True:
        try:
            user_input = int(input("\nVyberte číslo odpovědi: ")) - 1
            if 0 <= user_input <= len (question['answers']):
                break
            else: 
                print("Zadejte číslo v platném rozsahu: ")
        except ValueError:  
            print("Zadejte celé číslo: ")

    correct_index = question['correct_answer']
    is_correct = (user_input == correct_index)
    return is_correct

def calculate_result(score, total_questions):
    percentage = (score / total_questions) * 100
    for grade, (lower, upper) in MARKING.items():
        if lower <= percentage < upper:
            return grade, percentage
    return 5, percentage


def save_test_result(last_name, first_name, total_questions, grade, success_rate, wrong_answers):
    os.makedirs(RESULT_FOLDER, exist_ok=True)
    time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{last_name}_{first_name}_{time}_{total_questions}_{grade}.txt"
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
            lines.append(f"n\Otázka {question['question']}")
            lines.extend(question['answers'])
    with open(whole_file, "w", encoding='utf-8') as file:
        file.write("\n".join(lines))


def run_test():
    first_name, last_name = get_user_name()
    questions = load_questions_from_directory(os.getcwd())
    
    if not questions:
        print("Nebyla nalezena žádná otázka")
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


##############################################################
### Spuštění programu - MAIN

if __name__ == "__main__":

    os.system('clear' if os.name == 'posix' else 'cls')
    while True:
        run_test()
        repeat = input("Chcete test zopakovat? (ano/ne): ").lower()
        if repeat != "ano":
            break
