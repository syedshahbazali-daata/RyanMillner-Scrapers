from lxml import html
from datetime import datetime
import requests
import sys
import csv


def convert_date_format(date_string):
    try:
        date_object = datetime.strptime(date_string, "%B %d, %Y")
        formatted_date = date_object.strftime("%m/%d/%Y")
        return formatted_date
    except ValueError:
        return 'Invalid date format'


def days_until_date(input_date):
    date_format = "%m/%d/%Y"
    try:
        input_datetime = datetime.strptime(input_date, date_format)
        current_datetime = datetime.now()
        time_difference = current_datetime - input_datetime
        days_difference = time_difference.days
        return int(days_difference)
    except ValueError:
        return "Invalid date format"


def scrape_data(site_url):
    response = requests.get(site_url)
    get_content = response.content
    tree = html.fromstring(get_content)
    user_name = tree.xpath('//ul[@class="meta-group"]//li[1]//text()')
    user_name = [x.strip() for x in user_name]
    user_name = [x.replace('\u00e9', '') for x in user_name]
    user_name = [x.replace('\u00f8', '') for x in user_name]
    titles = tree.xpath('//span[@class="striped-list-info"]//a/text()')
    dates = tree.xpath('//ul[@class="meta-group"]//li//time[@data-datetime="calendar"]/text()')
    dates = [date.rsplit(' ', 1)[0] for date in dates]
    urls = tree.xpath('//span[@class="striped-list-info"]//a')
    urls = [x.attrib['href'] for x in urls]
    forum_category = tree.xpath('//header[@class="page-header"]//h1//text()')
    forum_category = [x.strip() for x in forum_category]

    next_page_link = tree.xpath('//li[@class="pagination-next"]//a')
    next_page_link = [x.attrib['href'] for x in next_page_link]
    base_url = "https://support.zendesk.com"
    next_page_link = [base_url + x for x in next_page_link]

    all_body_texts = []

    for get_text in urls:
        response = requests.get(get_text)
        get_content = response.content
        tree = html.fromstring(get_content)
        body_text = tree.xpath('//div[@class="post-body"]')
        body_text = [x.text_content().strip() for x in body_text]
        body_text = [x.replace('\u00a0', '') for x in body_text]
        body_text = [x.replace('\n', '') for x in body_text]
        all_body_texts.append(body_text)

    return user_name, titles, dates, urls, forum_category, next_page_link, all_body_texts


try:
    enter_the_url = str(sys.argv[1])
    url_convert = "https://support.zendesk.com/hc/en-us/community/topics/" + enter_the_url.split("/")[-1] + "#posts"
    no_of_days = int(sys.argv[2])
except:
    print("Please enter the URL and number of days as arguments. "
          "Example: python script.py https://support.zendesk.com/hc/en-us/community/topics 5")
    sys.exit(1)

url = url_convert
site_url = url
save_data = []
days_difference = 0

scraping_site_name = url.split("/")[-1].split("-")[0].capitalize()

keep_going = True
print("Scraping data...")
while keep_going:
    user_name, titles, dates, urls, forum_category, next_page_link, all_body_texts = scrape_data(site_url)
    data_found = False

    for name, title, url, date, body_text in zip(user_name, titles, urls, dates, all_body_texts):
        published_date = date
        published_date = convert_date_format(published_date)

        days_difference = days_until_date(published_date)

        if days_difference <= no_of_days:
            data = [name, title, url, published_date, body_text[0], forum_category[0]]
            save_data.append(data)
            print(published_date)

    if days_difference >= no_of_days:
        keep_going = False
        break

    if not next_page_link:
        break

    site_url = next_page_link[0]
    next_page_link = next_page_link[1:]

current_date = datetime.now().strftime("%m%d%y")
file_name = f"Zendex_community_Scraper_{current_date}_{scraping_site_name}.csv"

header = ['USER NAME', 'TITLE', 'URL', 'DATE', 'TEXT', 'FORUM CATEGORY']
save_data.insert(0, header)

with open(f'{file_name}', 'w', encoding='utf-8') as outfile:
    csv_writer = csv.writer(outfile)
    csv_writer.writerows(save_data)

print("Data has been Scraped and saved")
