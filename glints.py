import pandas as pd
import datetime as dt
import warnings
import time
warnings.filterwarnings("ignore")
#import requests
import json

from bs4 import BeautifulSoup
from selenium import webdriver

#headers = {'User-Agent': "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"}
def scraper(query_list, driver):
    #driver = webdriver.Safari()
    #df_glints = pd.DataFrame()
    #job_title = []
    #comp = []
    #upd = []
    #types = []
    #edu = []
    #exp = []
    #skills = []
    #content = []
    job_url = []
    #location = []
    data = pd.DataFrame()
    tmp = []
    #query_list = ['Data Analyst','Data Scientist','Data Engineer']
    for query in query_list:
        kwd = query.lower()
        pages = 3

        for pg in range(1,pages+1):
            glints_url = f'https://glints.com/id/opportunities/jobs/explore?keyword={kwd}&country=ID&sortBy=LATEST&yearsOfExperienceRanges=LESS_THAN_A_YEAR%2CONE_TO_THREE_YEARS&lastUpdated=PAST_MONTH&page={pg}'

            driver.get(glints_url)
            html = driver.page_source
            #html = requests.get(glints_url, headers=headers).text
            soup = BeautifulSoup(html, 'html.parser')
            job_url += ['https://glints.com'+x['href'] for x in soup.find_all('a',{"class":"CompactOpportunityCardsc__CardAnchorWrapper-sc-dkg8my-24 knEIai job-search-results_job-card_link"})]
            #location += [x['title'] for x in soup.find_all('span',{'class':'CardJobLocation__StyledTruncatedLocation-sc-1by41tq-1 kEinQH'})]
        for url in job_url:
            #res = requests.get(url, headers=headers).text
            driver.get(url)
            driver.get(url)
            time.sleep(0.2)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            try:
                api = json.loads(soup.find("script",{"type":"application/json"}).text)['props']['pageProps']['initialOpportunity']
            except:
                continue
            '''exp.append(f"{api['minYearsOfExperience']}-{api['maxYearsOfExperience']} years")
            edu.append(api['educationLevel'])
            job_title.append(api['title'])
            comp.append(api['company']['name'])
            upd.append(api['updatedAt'])
            types.append(api['type'])
            location.append(api['location']['parents'][0]['name'])
            try:
                skills.append(','.join([x.text for x in soup.find('div',{"class":"Opportunitysc__SkillsContainer-sc-gb4ubh-10 jccjri"}).find_all('div',{'class':"TagStyle__TagContentWrapper-sc-r1wv7a-1 koGVuk"})]))
            except:
                skills.append('None')
            try:
                content.append(soup.find_all("div",{"data-contents":True})[0].get_text())
            except:
                content.append('None')'''
            
            exp=f"{api['minYearsOfExperience']}-{api['maxYearsOfExperience']} years"
            edu=api['educationLevel']
            job_title=api['title']
            comp=api['company']['name']
            upd=api['updatedAt']
            types=api['type']
            location=api['location']['parents'][0]['name']
            try:
                skills=','.join([x.text for x in soup.find('div',{"class":"Opportunitysc__SkillsContainer-sc-gb4ubh-10 jccjri"}).find_all('div',{'class':"TagStyle__TagContentWrapper-sc-r1wv7a-1 koGVuk"})])
            except:
                skills = None
            try:
                content=soup.find_all("div",{"data-contents":True})[0].get_text()
            except:
                content = None

            tmp.append({'Portal':'Glints',
                        'Job Title':job_title,
                        'Company':comp,
                        'Location':location,
                        'Last Update':upd,
                        'Job Type':types,
                        'Education':edu,
                        'Experience':exp,
                        'Skills':skills,
                        'Description':content,
                        'URL':url})

    '''tmp['Portal'] = ['Glints' for x in job_title]
    tmp['Job Title'] = job_title
    tmp['Company'] = comp
    tmp['Location'] = location
    tmp['Last Update'] = upd
    tmp['Job Type'] = types
    tmp['Education'] = edu
    tmp['Experience'] = exp
    tmp['Skills'] = skills
    tmp['Description'] = content
    tmp['URL'] = job_url'''
    data = pd.DataFrame(tmp)
    return data