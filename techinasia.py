import pandas as pd
import warnings
import time
warnings.filterwarnings("ignore")

from bs4 import BeautifulSoup
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def scraper(query_list,driver):
    df_techinasia = pd.DataFrame()
    #driver = webdriver.Safari()
    for query in query_list:
        kwd = query.lower()

        main_url = f"https://www.techinasia.com/jobs/search?query={kwd}"
        driver.get(main_url)

        # Function untuk scroll page
        def scroll_page():
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(1)

        # scrolling x kali
        for i in range(7):
            scroll_page()

        main_page_source = driver.page_source

        main_soup = BeautifulSoup(main_page_source, 'html.parser')

        job_results = main_soup.find_all('article', {'data-cy': 'job-result'})

        if len(job_results)>0:
            pass
        else:
            continue

        titles = []
        companies = []
        locations = []
        salaries = []
        categories = []
        types = []
        updated = []

        # ambil data dari main search page
        for job in job_results:
            # Find the parent element containing both job title and company name
            job_info = job.find('div', {'class': 'jsx-1749311545 details'})

            # Extract job title
            title_element = job_info.find('a', {'data-cy': 'job-title'})
            title = title_element.text.strip() if title_element else "N/A"
            titles.append(title)

            # Extract combined text of job info (including company name)
            job_info_text = job_info.get_text(separator='|', strip=True)
            job_info_parts = job_info_text.split('|')

            # Extract company name (assuming it's after the job title)
            company = job_info_parts[1].strip() if len(job_info_parts) > 1 else "N/A"
            companies.append(company)

            # Extract other details similarly as before
            location = job.find_all('div', {'class': 'jsx-1749311545'})[-3].text.strip()
            locations.append(location)

            salary = job.find_all('div', {'class': 'jsx-1749311545'})[-2].text.strip()
            salaries.append(salary)

            category = job.find('li', {'class': 'jsx-1749311545'}).text.strip()
            categories.append(category)

            job_type = job.find_all('li', {'class': 'jsx-1749311545'})[-1].text.strip()
            types.append(job_type)

            update = job.find('span',{'class':'jsx-1022654950 published-at'}).text.strip()
            updated.append(update)

        data = {
            'Portal': ['Techinasia' for x in range(len(titles))],
            'Job Title': titles,
            'Company': companies,
            'Location': locations,
            'Salary': salaries,
            'Category': categories,
            'Job Type': types,
            'Last Update':updated
        }

        main_job_data = pd.DataFrame(data)

        '''
        Dari sini melakukan scraping terhadap setiap page individu job listing
        Jadi gw ambil url tiap job dulu terus di looping
        '''

        # ambil url dari main search page
        job_urls = []
        job_elements = main_soup.find_all('a', {'data-cy': 'job-title'})
        for element in job_elements:
            job_urls.append("https://www.techinasia.com" + element['href'])

        # ambil data dari individual job listing pada search page
        job_data_individual = []

        vacancies = []
        experience = []

        # Looping URL job
        for job_url in job_urls:
            driver.get(job_url)
            
            time.sleep(1)
            
            page_source_individual = driver.page_source

            time.sleep(1)
            
            soup_individual = BeautifulSoup(page_source_individual, 'html.parser')
            
            # ambil data dari individual page

            job_desc_requirements = soup_individual.find('section', {'class': 'jsx-301681418'})

            exp_vac = soup_individual.find('b', {'class': 'jsx-3446601365'})

            desc_req_text = job_desc_requirements.get_text(separator=' ', strip=True) if job_desc_requirements else "N/A"

            required_skills = [tag.text.strip() for tag in soup_individual.find_all('span', {'data-cy': 'tag'})]
            

            # Get Element data
            elements = soup_individual.find_all('b', {"class": "jsx-3446601365"})

            data_get = []
            for element in elements:
                try:
                    data_get.append(element.get_text())
                except AttributeError:
                    data_get.append(None)
            time.sleep(1)
                
        
            job_data_individual.append({
                'Description': desc_req_text,
                'Required Skills': required_skills,
                'get_data': data_get
            })

            individual_page_data = pd.DataFrame(job_data_individual)
            df = pd.concat([main_job_data, individual_page_data], axis = 1)

        experience = []

        for data in df['get_data']:
            if data:
                experience.append(data[2])
            else:
                experience.append('Nan')

        df['Experience'] = experience
        df['URL'] = job_urls
        df_techinasia=pd.concat([df_techinasia,df])
    #driver.close()
    return df_techinasia