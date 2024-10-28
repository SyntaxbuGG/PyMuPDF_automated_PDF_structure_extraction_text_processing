import fitz
import json
import re
from pprint import pprint

pdf_file = fitz.open("filefortest.pdf")

toc = pdf_file.get_toc()

section_pattern = re.compile(r'^\d+\.\d+')
subsection_pattern = re.compile(r'^\d+\.\d+\.\d+')



def extract_structure(file: list[list]) ->dict[dict]:
    structure = {}
    chapter = 0
  
    for line in file[1:] :
        level,title,page = line 
             
        if level == 1:
            if 'Глава' in title:
                chapter += 1
             
                structure[str(chapter)] = {}    
                current_chapter = str(chapter) 
            else :
                structure[current_chapter] = {
                    'title': title,
                    'sections': {}
                }
             

        elif level == 2 and section_pattern.match(title):
            section_number = title.split()[0]
            withoutnumberstitle = " ".join(title.split()[1:])
            structure[current_chapter]['sections'][section_number] = {
                'title' : withoutnumberstitle,
                'subsections': {}
            }
        
        elif level == 3 and subsection_pattern.match(title):
            subsections_number = title.split()[0]
            withoutnumberstitle = " ".join(title.split()[1:])
            structure[current_chapter]['sections'][section_number]['subsections'][subsections_number] = {
                'title' : withoutnumberstitle,
            }
          

    return structure


extracted_structure = extract_structure(toc)
print(extracted_structure)

            
with open('structuretestfinal.json','w',encoding='utf-8') as json_file:
    json.dump(extracted_structure,json_file, ensure_ascii=False, indent=4)
