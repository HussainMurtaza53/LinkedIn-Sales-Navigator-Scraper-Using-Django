from threading import Thread
import pandas as pd
from tqdm import tqdm
import time
import json
import sys
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from scraping.models import *
from datetime import datetime


class Sales_Navigator_Scraper(Thread):

    # Constructor to save website which we will pass while calling Scraper class:
    def __init__(self, link, limit, job_id):

        self.link = link
        self.limit = limit
        self.job_id = job_id

        with open('./credentials.json') as f:
            json_data = json.load(f)
        
        self.username = json_data['username']
        self.password = json_data['password']

        PROXY = "151.80.255.29:8001"

        options = Options()
        options.headless = True
        options.add_argument('--proxy-server=%s' % PROXY)
        options.add_argument('--start-maximized')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--incognito")
        
        
        # options = Options()
        # options.headless = True
        # options.add_argument('--no-sandbox')
        # options.add_argument('--start-maximized')
        # options.add_argument('--start-fullscreen')
        # options.add_argument('--single-process')
        # options.add_argument('--disable-dev-shm-usage')
        # options.add_argument("--incognito")
        # options.add_argument('--disable-blink-features=AutomationControlled')
        # options.add_argument('--disable-blink-features=AutomationControlled')
        # options.add_argument("disable-infobars")
        
        self.driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", chrome_options = options)
        # self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = options)

        Thread.__init__(self)

    def run(self):

        self.start_browser(self.link)
        self.scrape(self.limit, self.job_id)
    
    # This function will open the website in new browser:
    def start_browser(self, website):
        
        self.driver.get(website)

        time.sleep(2)

        login_link = self.driver.find_element_by_tag_name('iframe').get_attribute('src')
        self.driver.get(login_link)

        try:
            self.enter_login_credentials()
        except:
            pass

        self.driver.get(website)

        try:
            self.driver.maximize_window()
        except:
            pass

        time.sleep(7)

    def enter_login_credentials(self):

        username = self.driver.find_element_by_id('username')
        username.send_keys(self.username)

        password = self.driver.find_element_by_id('password')
        password.send_keys(self.password)

        self.driver.find_element_by_class_name('from__button--floating').click()

    def get_page_data_by_scrolling(self):

        self.driver.find_element_by_xpath("//div[contains(@class, 'mt4') and contains(@class, 'mr5')]").click()

        html = self.driver.find_element_by_tag_name('html')
        html.send_keys(Keys.END)

        for i in range(8):
            html.send_keys(Keys.PAGE_UP)

        time.sleep(2)
        html.send_keys(Keys.END)
        html.send_keys(Keys.END)
        html.send_keys(Keys.HOME)
        html.send_keys(Keys.END)

        page_data = self.driver.find_elements_by_class_name('artdeco-entity-lockup__title')

        return page_data

    def shift_tab(self, element):

        ActionChains(self.driver).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(6)

    # This is the main function that will scrape all data:
    def scrape(self, limit, job_id):

        condition = True
        all_details = []
        count = 1
        # import pdb; pdb.set_trace()
        try:
            total_result = self.driver.find_element_by_class_name('_display-count-spacing_1igybl').text
        except:
            time.sleep(2)
            total_result = self.driver.find_element_by_class_name('_display-count-spacing_1igybl').text

        print('\n------------------------ Link Contains {0} ------------------------\n'.format(total_result))

        while condition:

            try:
                all_content = self.get_page_data_by_scrolling()
            except:
                time.sleep(8)
                all_content = self.get_page_data_by_scrolling()

            time.sleep(2)

            for l in tqdm(range(len(all_content))):

                if len(all_details) != limit:
                    
                    try:
                        name_ls = self.driver.find_elements_by_class_name('artdeco-entity-lockup__title')[l].text.split()

                        if len(name_ls) > 1:

                            f_name = name_ls[0]
                            l_name = name_ls[1]

                        else:
                            f_name = name_ls[0]
                            l_name = None

                        try:
                            location = self.driver.find_elements_by_class_name('artdeco-entity-lockup__caption')[l].text
                        except:
                            location = None

                        try:
                            info = self.driver.find_elements_by_class_name('artdeco-entity-lockup__subtitle')[l]
                            job_title = info.find_element_by_tag_name('span').text
                            company = info.text
                            company = company.replace(job_title + ' ', '')
                        except:
                            job_title = None
                            company = None

                        try:
                            comp_info = self.driver.find_elements_by_class_name('artdeco-entity-lockup__subtitle')[l].find_element_by_tag_name('a')

                            self.shift_tab(comp_info)

                            try:
                                company_url = self.driver.find_element_by_class_name('view-website-link').get_attribute('href')
                            except:
                                company_url = None

                            self.driver.close()

                            self.driver.switch_to.window(self.driver.window_handles[0])

                        except:
                            company_url = None

                        if company:

                            dic = {
                                'First_Name': f_name,
                                'Last_Name': l_name,
                                'Company': company,
                                'Company_URL': company_url,
                                'Job_Title': job_title,
                                'Location': location
                            }

                            all_details.append(dic)

                            self.save_data(all_details, job_id)

                            Job_Status.objects.filter(job_id = job_id).update(total_processed = len(all_details))

                    except:
                        pass

                else:
                    Job_Status.objects.filter(job_id = job_id).update(finished_at = datetime.now(), total_processed = len(all_details), job_status = 'complete')
                    break

            print('\n------------------------ PAGE NO. ' + str(count) + ' COMPLETED ------------------------\n')

            print('\n------------------------ SCRAPED CONTACTS: ' + str(len(all_details)) + ' ------------------------\n')

            if len(all_details) != limit:

                try:
                    try:
                        button_class = self.driver.find_element_by_class_name('artdeco-pagination__button--next').get_attribute('class')
                    except:

                        time.sleep(5)
                        button_class = self.driver.find_element_by_class_name('artdeco-pagination__button--next').get_attribute('class')

                    if 'artdeco-button--disabled' not in button_class:
                        try:
                            self.driver.find_element_by_class_name('artdeco-pagination__button--next').click()
                            time.sleep(10)
                            count += 1
                        except:
                           element = self.driver.find_element_by_class_name('artdeco-pagination__button--next')
                           self.driver.execute_script("arguments[0].click();", element)
                           time.sleep(10)
                           count += 1
                    else:
                        condition = False
                
                except Exception as err:
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    filename = exception_traceback.tb_frame.f_code.co_filename
                    line_number = exception_traceback.tb_lineno

                    with open('Error_Log.txt' , 'w') as file:
                        file.write('Error: ' + str(err) + '\n')
                        file.write('Exception type: ' + str(exception_type) + '\n')
                        file.write('File name: ' + str(filename) + '\n')
                        file.write('Line number: ' + str(line_number))
                        file.close()

                    condition = False
            else:
                condition = False

        print('\n------------------------ SCRAPING DONE OF LINK WITH {0} CONTACTS ------------------------\n'.format(limit))

    def save_data(self, data_ls, job_id):

        scraped_data = pd.DataFrame(data_ls)
        excel_name = 'LinkedIn_Sales_Navigator_ID#{0}_Data.csv'.format(job_id)
        scraped_data.to_csv('LinkedIn_Data/' + excel_name)