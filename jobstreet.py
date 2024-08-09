import pandas as pd
import datetime as dt
import warnings
warnings.filterwarnings("ignore")
import time

from bs4 import BeautifulSoup
import requests

def scraper(query_list):
    df_jobstreet = pd.DataFrame()
    for query in query_list:
        base_url = 'https://www.jobstreet.co.id'
        # list untuk menyimpan data
        data = []
        num_pages = 5
        key = '-'.join(query.lower().split(' '))+'-jobs'

        # Looping untuk setiap halaman
        for page in range(1, num_pages + 1):

            url = f'{base_url}/id/{key}?page={page}&sortmode=ListedDate'

            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            #a_tags = soup.find_all('a', attrs={'data-automation': 'job-list-view-job-link'})
            a_tags= soup.select('a[data-automation="job-list-view-job-link"]') #menggunakan CSS selector
            href_list = [a.get('href') for a in a_tags]

            for href_value in href_list:
                full_url = base_url + href_value
                job_response = requests.get(full_url)
                time.sleep(0.2)

                job_soup = BeautifulSoup(job_response.text, 'html.parser')

                try:
                    job_title = job_soup.find('h1').text.strip().lower()
                except:
                    job_title = 'None'
                try:
                    company_name = job_soup.find('a',class_='y735df0 y735dff y735df0 y735dff _10p6bbx1').text
                except:
                    try:
                        company_name = job_soup.find('span',class_='y735df0 _1iz8dgs4y _94v4w0 _94v4w1 _94v4w21 _4rkdcp4 _94v4wa').text
                    except:
                        company_name = 'None'
                try:
                    job_description = job_soup.find('div', {'data-automation': 'jobAdDetails'}).get_text(strip=True)
                except:
                    job_description = None
                try:
                    job_type = job_soup.find_all('span', class_='y735df0 _1iz8dgs4y _1iz8dgsr')[2].text
                except:
                    job_type = None
                try:
                    location = job_soup.find_all('span', class_='y735df0 _1iz8dgs4y _1iz8dgsr')[0].text
                except:
                    location = None
                try:
                    post = job_soup.find_all('span',class_="y735df0 _1iz8dgs4y _94v4w0 _94v4w1 _94v4w22 _4rkdcp4 _94v4w7")[1].text
                except:
                    post = None
                try:
                    if post.split(' ')[2] == 'hari':
                        upd = str(dt.datetime.now().date()-dt.timedelta(days=int(post.split(' ')[1])))
                    elif post.split(' ')[2] == 'jam':
                        upd = str(dt.datetime.now().date()-dt.timedelta(hours=int(post.split(' ')[1])))
                except:
                    upd = str(dt.datetime.now().date()-dt.timedelta(days=30))
                try:
                    data.append({'Portal':'Jobstreet','Last Update':upd, 'Job Title': job_title, 'Company': company_name,
                                'Location':location,'Description': job_description, 'Job Type': job_type, 'URL':full_url})
                except:
                    continue

        tmp = pd.DataFrame(data)
        df_jobstreet = pd.concat([df_jobstreet,tmp])
    return df_jobstreet