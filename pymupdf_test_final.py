import fitz
import json
import re


pdf_file = fitz.open("filefortest.pdf")

toc = pdf_file.get_toc()

# Определение паттерн регуляных выражений
chapter_pattern = re.compile(r"^[А-Яа-я]+(\s+[А-Яа-я]+(,\s*)?){0,20}$")
section_pattern = re.compile(r'^\d+\.\d(\.)?+\s')
subsection_pattern = re.compile(r'^\d+\.\d+\.\d+\s')
text_pattern_stop = re.compile(
    r'\b\d+\.\d+(\.\d+)?\.?\s+([А-Я][а-я]+|[А-Я]+)')


# Чтобы при чтение json файла было удобно !
def clean_text(text: str) -> str:
    """Удаляет лишние пробелы и переносы строк из текста."""
    return ' '.join(text.split())


def extract_text_from_pages(title_text: str, start_page: int) -> str:
    """Извлекает текст, начиная с заданного заголовка, до следующего заголовка или конца документа."""

    finally_text = ""
    text_without_num = ''

    # Это чтобы несколько пробелов или какихто невидимох символов заменить на регэксп пробел
    pattern_title = title_text.replace(" ", r"\s*")

    # Находит по заголовок игнорируя заглавные и строчные буквы
    pattern = re.compile(rf'{pattern_title}(.*)', re.DOTALL | re.IGNORECASE)

    try:
        total_pages = pdf_file.page_count
        while start_page <= total_pages:
            page = pdf_file.load_page(start_page - 1)
            page_text = page.get_text("text")
            match = pattern.search(page_text)

            text_without_num = match.group(1).lstrip() if match else page_text

            match_text = text_pattern_stop.search(text_without_num)

            if match_text:
                match_section = match_text.start()
                finally_text += text_without_num[:match_section].strip()
                finally_text = clean_text(finally_text)
                return finally_text.strip()
            finally_text += text_without_num.strip()
            start_page += 1

    except Exception as e:
        print(f"Ошибка при обработке страницы {start_page}: {e}")
    finally_text = clean_text(finally_text)
    return finally_text


# Корректировка уровень заголовка
def correct_level(level: int, title: str) -> int:
    return 3 if level == 2 and subsection_pattern.match(title) else 2 if level == 3 and section_pattern.match(title) else level


def extract_structure(file: list[list]) -> dict[str, dict]:
    """Извлекает структуру документа на основе оглавления."""
    structure = {}
    current_chapter = 0

    for line in file[1:]:
        level, title, page = line
        level = correct_level(level, title)
        without_numbers_title = ' '.join(title.split()[1:])
        text_from_page = extract_text_from_pages(title, page)

        if level == 1 and chapter_pattern.match(title):
            current_chapter += 1

            if text_from_page:
                structure[current_chapter] = {
                    'title': title,
                    'text': text_from_page,
                    'sections': {},
                }
            else:
                structure[current_chapter] = {
                    'title': title,
                    'sections': {}
                }

        elif level == 2 and section_pattern.match(title):
            section_number = title.split()[0]

            if text_from_page:
                structure[current_chapter]['sections'][section_number] = {
                    'title': without_numbers_title,
                    'text': text_from_page,
                    'subsections': {},
                }
            else:
                structure[current_chapter]['sections'][section_number] = {
                    'title': without_numbers_title,
                    'subsections': {},


                }

        elif level == 3 and subsection_pattern.match(title):
            subsections_number = title.split()[0]

            if text_from_page:
                structure[current_chapter]['sections'][section_number]['subsections'][subsections_number] = {
                    'title': without_numbers_title,
                    'text': text_from_page
                }
            else:
                structure[current_chapter]['sections'][section_number]['subsections'][subsections_number] = {
                    'title': without_numbers_title,
                }

    return structure


extracted_structure = extract_structure(toc)


with open('structuretestfinal.json', 'w', encoding='utf-8') as json_file:
    json.dump(extracted_structure, json_file, ensure_ascii=False, indent=4)


print('Succesfull created json file')
