import re
import csv
import requests
from bs4 import BeautifulSoup as bs

base = 'https://catalog.colorado.edu/courses-a-z/'

# each course we need the skinny on, and 
# the language(s)/software(s) associated 
n = 'number'
l = 'language'
courses = {
    'APPM': [{n:'4650', l:'Python, Matlab'}, {n:'4120', l:'LaTex'}, {n:'2350', l:'Matlab'}],
    'MATH': [{n:'4440', l:'Python: Sage'}, {n:'3001', l:'LaTex'}, {n:'2001', l:'LaTex'}, 
             {n:'3430', l:'Matlab'}, {n:'2135', l:'LaTex'}],
    'CSCI': [{n:'4593', l:'Risc-V, C, Linux (Bash)'}, {n:'4448', l:'Java, JUnit'}, 
             {n:'3308', l:'Javascript, HTML, CSS, Postgresql, ...'}, {n:'3202', l:'Python'}, 
             {n:'3753', l:'C, Linux (Bash)'}, {n:'2824', l:'Python'}, {n:'3104', l:'C++, Python'},
             {n:'2400', l:'C'}, {n:'2270', l:'C++'}, {n:'3155', l:'Scala'}],
    'ECON': [{n:'4848', l:'Stata'}, {n:'3818', l:'R, R-Studio'}, {n:'4697'}, {n:'4423'}, {n:'3080'}, 
             {n:'3070'}, {n:'2020'}, {n:'2010'}] # 3374
}

course_items = []

for key, value in courses.items():
    
    # go to specific uri link in the course catalog
    url = base + key.lower()
    page = requests.get(url)
    soup = str(bs(page.content, 'html.parser'))
    
    for obj in value:
        course_obj = { 'school' : key, 'course_num' :  obj[n], 
                      'language' : obj[l] if obj.get(l) is not None else " "}
        
        # get full name of course 
        name_end_p = re.compile(r'\<\/')
        name_start_p = re.compile(obj[n] + r'\s+.*\)\s+')

        name_start_i = name_start_p.search(soup).end()
        name_end_i = name_start_i + name_end_p.search(soup[name_start_i:]).start()
        
        course_obj['name'] = soup[name_start_i:name_end_i].strip()

        # get course description and details 
        desc_start_p = re.compile(r'\"\>')
        desc_end_p = re.compile(r'\<')
        
        desc_start_i = name_end_i + desc_start_p.search(soup[name_end_i:]).end()
        desc_end_i = desc_start_i + desc_end_p.search(soup[desc_start_i:]).start()
        
        course_obj['description'] = soup[desc_start_i:desc_end_i].strip()
        course_items.append(course_obj)

# add the outlier
course_items.append({
    'school': 'ECON',
    'course_num': '3274',
    'language': ' ',
    'name': 'International Economics',
    'description': 'Studied how global businesses are impacted by real world developments in economics, politics, and finance; emphasis on globalization, trade and investment, the global marketplace and monetary system.'
})

# writing to csv file  
filename = "university_courses.csv"
headers = ['school', 'course_num', 'language', 'name', 'description']

with open(filename, 'w', newline='') as csvfile:  
    
    writer = csv.DictWriter(csvfile, fieldnames = headers)  
    
    # writing headers (field names)  
    writer.writeheader()  
        
    # writing data rows  
    writer.writerows(course_items) 
    
