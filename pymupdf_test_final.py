import fitz
import json
import re
from pprint import pprint

pdf_file = fitz.open("Руководство_Бухгалтерия_для_Узбекистана_ред_3_0.pdf")

toc = pdf_file.get_toc()



def extract_structure(file):
    structure = {}
    chapter = 0
    section_key = 1
    subsection_key = 1
    for line in file[1:] :
        level,title,page = line 
       
        if level == 1:
            if 'Глава' in title:
                chapter += 1
                section_key = 1
                structure[str(chapter)] = {}    
                current_chapter = str(chapter) 
            else :
                structure[current_chapter] = {
                    'title': title,
                    'sections': {}
                }
             

        elif level == 2:
            section_number = f'{chapter}.{section_key}'
            
            structure[current_chapter]['sections'][section_number] = {
                'title' : title,
                'subsections': {}
            }
            section_key += 1
            subsection_key = 1


        elif level == 3:
            subsections_number = f'{section_number}.{subsection_key}'
            structure[current_chapter]['sections'][section_number]['subsections'][subsections_number] = {
                'title' : title,
            }
            subsection_key += 1

    return structure

#print(toc)
extracted_structure = extract_structure(toc)
print(json.dumps(extracted_structure, indent=4, ensure_ascii=False))
            
with open('structuretestfinal.json','w',encoding='utf-8') as json_file:
    json.dump(extracted_structure,json_file, ensure_ascii=False, indent=4)
