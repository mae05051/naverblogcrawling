import sys
import pandas as pd
from selenium import webdriver
import time
from tqdm import tqdm
from datetime import datetime, timedelta




driver = webdriver.Chrome("./chromedriver") #구글드라이버 path

#search_text:검색어
#start_date,end_date: 검색 시작일, 종료일
#order_by: 정렬순 (정확순='sim', 날짜순='recentdate')
def naverblog_crawling(search_text,start_date,end_date,order_by):
    url1p='https://section.blog.naver.com/Search/Post.naver?pageNo=1&rangeType=PERIOD&orderBy='+ order_by +'&startDate='+ start_date +'&endDate='+end_date+'&keyword=' + search_text
    driver.get(url1p)
    print(url1p)
    count=driver.find_elements_by_xpath('/html/body/ui-view/div/main/div/div/section/div[1]/div[2]/span/span/em')#건수
    print(count[0])
    c=int((count[0].text).replace("건","").replace(",",""))#건수 전처리
    th=1 #페이지 긁는량 임계값 (2로 설정시 절반만 긁음)
    page=(c//7+1)//th
    
    url_list = []
    for i in tqdm(range(1, page+1)):  # 1~page까지 크롤링
        #url = 'https://section.blog.naver.com/Search/Post.nhn?pageNo='+ str(i) + '&rangeType=ALL&orderBy=recentdate&keyword=' + text
        url='https://section.blog.naver.com/Search/Post.naver?pageNo=' + str(i) + '&rangeType=PERIOD&orderBy='+order_by+'&startDate='+ start_date +'&endDate='+end_date+'&keyword=' + search_text
        driver.get(url)
        time.sleep(0.5)
        if i==page:
            for k in range(1,(c%7+1)):
                blogs= driver.find_element_by_xpath('/html/body/ui-view/div/main/div/div/section/div[2]/div['+str(k)+']/div/div[1]/div[1]/a[1]')
                blog = blogs.get_attribute('href')
                url_list.append(blog)
        else:
            for j in range(1, 8): # 페이지별 크롤링 할 블로그 개수 설정
                blogs= driver.find_element_by_xpath('/html/body/ui-view/div/main/div/div/section/div[2]/div['+str(j)+']/div/div[1]/div[1]/a[1]')
                blog = blogs.get_attribute('href')
                url_list.append(blog)
    print(len(url_list))
    
    list_titles=[]
    list_contents=[]
    list_dates=[]
    list_url=[]

    print("url 수집 끝, 해당 url 데이터 크롤링")
    
    for url in tqdm(url_list): # 수집한 url 만큼 반복
        driver.get(url) # 해당 url로 이동
        driver.switch_to.frame('mainFrame')
    
        contents = driver.find_elements_by_css_selector(".se-component.se-text.se-l-default")#본문
        titles=driver.find_elements_by_css_selector('.se-module.se-module-text.se-title-text')#제목
        dates=driver.find_elements_by_css_selector("span.se_publishDate.pcol2")#날짜
        #print(contents)
        contents
        content_list = []
        if contents != []:#본문내용 못긁으면
            
            list_url.append(url)#url 리스트

            for content in contents:
                content_list.append(content.text)
                content_str = ' '.join(content_list)#본문내용

            list_contents.append(str(content_str))#본문내용 리스트
                        
            for title in titles:
                list_titles.append(title.text)

            for date in dates:
                hour = datetime.today().strftime('%H') #현재시간
                minute= datetime.today().strftime('%M') #현재 분
                if '분' in date.text:
                    blog_date = date.text.replace('분 전','')
                    if int(hour) == 0 & (int(minute) - int(blog_date))<0:
                        list_dates.append((datetime.today() - timedelta(days=1)).strftime('%Y. %m. %d.')) 
                    else:
                        list_dates.append(datetime.today().strftime("%Y. %m. %d."))
                    
                elif '시간' in date.text:
                    blog_date = date.text.replace('시간 전','')
                    if int(hour) - int(blog_date) < 0:
                        list_dates.append((datetime.today() - timedelta(days=1)).strftime('%Y. %m. %d.')) 
                    else:
                        list_dates.append(datetime.today().strftime("%Y. %m. %d."))

                else:
                    list_dates.append(datetime.strptime(date.text, '%Y. %m. %d. %H:%M').strftime('%Y. %m. %d.'))
                    # list_dates.append(date.text[:len(date.text)-6])
                    
        
    print('contents 수집 끝')
    # print(len(list_titles))
    # print(len(list_dates))
    # print(len(list_contents))

    crawling = pd.DataFrame(list(zip(list_dates,list_titles, list_contents, list_url)),columns = ['날짜','제목','본문','URL'])
    #crawling = pd.DataFrame(list_contents,columns =['본문'])
    crawling['본문'] = crawling['본문'].str.replace('\n',' ')

    crawling.to_csv(''+search_text+'.csv',index=False,encoding='utf-8-sig')
    driver.close()
    
#main
s=input("검색어를 입력하세요: ")
naverblog_crawling(s,'2021-12-27','2021-12-28','recentdate')