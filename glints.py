import pandas as pd
import datetime as dt
import warnings
import time
warnings.filterwarnings("ignore")

from bs4 import BeautifulSoup
from selenium import webdriver

def scraper(query_list):
    driver = webdriver.Safari()
    df_glints = pd.DataFrame()
    for query in query_list:
        job_url = []
        location = []
        kwd = query.lower()
        pages = 5

        for pg in range(1,pages+1):
            glints_url = f'https://glints.com/id/opportunities/jobs/explore?keyword={kwd}&country=ID&sortBy=LATEST&yearsOfExperienceRanges=LESS_THAN_A_YEAR%2CONE_TO_THREE_YEARS&lastUpdated=PAST_MONTH&page={pg}'

            driver.get(glints_url)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            job_url += ['https://glints.com'+x['href'] for x in soup.find_all('a',{"class":"CompactOpportunityCardsc__CardAnchorWrapper-sc-dkg8my-24 knEIai job-search-results_job-card_link"})]
            location += [x['title'] for x in soup.find_all('span',{'class':'CardJobLocation__StyledTruncatedLocation-sc-1by41tq-1 kEinQH'})]
        job_title = []
        comp = []
        upd = []
        type = []
        edu = []
        exp = []
        skills = []
        content = []
        tmp = pd.DataFrame()
        for url in job_url:
            driver.get(url)
            time.sleep(0.3)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            try:
                job_title.append(soup.find('h1',{'aria-label':'Job Title'}).text.lower())
            except:
                job_title.append('None')
            try:
                comp.append(soup.find('div',{"class":"TopFoldsc__JobOverViewCompanyName-sc-1fbktg5-5 gvAbxa"}).find('a').text)
            except:
                comp.append('None')
            try:
                days = int(soup.find('span',{"class":"TopFoldsc__UpdatedAt-sc-1fbktg5-14 donikX"}).text.split(' ')[1])
            except:
                days = 1
            upd.append(str(dt.datetime.now().date()-dt.timedelta(days=days)))
            try:
                type.append(soup.find_all('div',{"class":"TopFoldsc__JobOverViewInfo-sc-1fbktg5-9 iqoKuL"})[1].text)
            except:
                type.append('None')
            try:
                edu.append(soup.find_all('div',{"class":"TopFoldsc__JobOverViewInfo-sc-1fbktg5-9 iqoKuL"})[2].text)
            except:
                edu.append('None')
            try:
                exp.append(soup.find_all('div',{"class":"TopFoldsc__JobOverViewInfo-sc-1fbktg5-9 iqoKuL"})[3].text)
            except:
                exp.append('None')
            try:
                skills.append(','.join([x.text for x in soup.find('div',{"class":"Opportunitysc__SkillsContainer-sc-gb4ubh-10 jccjri"}).find_all('div',{'class':"TagStyle__TagContentWrapper-sc-r1wv7a-1 koGVuk"})]))
            except:
                skills.append('None')
            content.append(soup.find_all("div",{"data-contents":True})[0].get_text())

        tmp['Portal'] = ['Glints' for x in job_title]
        tmp['Job Title'] = job_title
        tmp['Company'] = comp
        tmp['Location'] = location
        tmp['Last Update'] = upd
        tmp['Job Type'] = type
        tmp['Education'] = edu
        tmp['Experience'] = exp
        tmp['Skills'] = skills
        tmp['Description'] = content
        tmp['URL'] = job_url

        #tmp = tmp[~tmp['Experience'].str.contains('5')]
        df_glints = pd.concat([df_glints,tmp])
    driver.close()
    return df_glints