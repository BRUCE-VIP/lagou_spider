import pymongo
import re
import time
from pyquery import PyQuery as pq
from config import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 15)

def get_index():
	try:
		print('进入主页')
		browser.get('https://www.lagou.com/')
		close_window = wait.until(
				EC.element_to_be_clickable((By.CSS_SELECTOR, '#cboxClose'))
			)
		close_window.click()
		time.sleep(2)
		search_place = wait.until(
				EC.presence_of_element_located((By.CSS_SELECTOR, '#search_input'))
			)
		search_button = wait.until(
				EC.element_to_be_clickable((By.CSS_SELECTOR, '#search_button'))
			)
		search_place.send_keys(WORK)
		time.sleep(2)
		search_button.click()
	except TimeoutException as e:
		print('连接超时！')
		login()

def get_datas():
	for css_num in range(3, 11):
		css_place = '#filterCollapse > li:nth-child(4) > a:nth-child({})'.format(css_num)
		time.sleep(2)
		one_type = browser.find_element_by_css_selector(css_place)
		type_name = one_type.text
		one_type.click()
		all_page = browser.find_element_by_xpath('//*[@id="s_position_list"]/div[2]/div/span[last()-1]').text
		print('正在获取', type_name, '第1页的信息')
		get_data(type_name)
		time.sleep(2)
		for p in range(2, int(all_page)+1):
			next_page = wait.until(
					EC.element_to_be_clickable((By.XPATH, '//*[@id="s_position_list"]/div[2]/div/span[last()]'))
				)
			next_page.click()
			print('正在获取', type_name, '第{}页的信息'.format(str(p)))
			get_data(type_name)
			time.sleep(2)
		browser.refresh()
		time.sleep(2)
		one_type = browser.find_element_by_css_selector(css_place)
		one_type.click()


def get_data(type_name):
	html = browser.page_source
	doc = pq(html)
	items = doc('#s_position_list .item_con_list .con_list_item').items()
	for item in items:
		url = item.find('.p_top .position_link').attr('href')
		all_title = item.find('.p_top').text()
		title = re.findall(r'(.*) \[', all_title)[0]
		address = re.findall(r'.*?\[ (.*) \]', all_title)[0]
		all_tag = item.find('.li_b_l').text().replace('/ ', '').split(' ')
		salary = all_tag[0]
		experience = all_tag[1]
		education = all_tag[2]
		tags = [tag for tag in all_tag[3:]]
		company = item.find('.company_name').text()
		fuli = item.find('.li_b_r').text()
		data = {
			'title': title,
			'url': url,
			'company': company,
			'address': address,
			'salary': salary,
			'experience': experience,
			'education': education,
			'tags': tags,
			'type': type_name,
			'fuli': fuli,
		}
		print(data)
		db[MONGO_TABLE].save(data)
		print('插入成功')


def main():
	get_index()
	get_datas()
	browser.close()
	print('爬取完毕')

if __name__ == '__main__':
	main()
