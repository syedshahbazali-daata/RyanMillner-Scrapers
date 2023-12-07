import requests
from datetime import datetime
from lxml import html
import json
import sys

# Check for command-line arguments
try:
    # Construct the initial URL for scraping reviews sorted by latest
    enter_the_url = str(sys.argv[1])
    url = enter_the_url.split(".com")[0] + ".com/1/RT-P.html?sort=latest"

    # Extract the number of days input from the command line
    no_of_days = int(sys.argv[2])
except:
    print("Please enter the url and no of days as arguments "
          "Example: python script.py  https://super-com.pissedconsumer.com/")
    sys.exit(1)

scraping_site_name = url.split(".com")[0].split("//")[-1].split(".")[0].capitalize()


# Function to convert date format from 'Month Day, Year' to 'MM/DD/YYYY'
def convert_date_format(input_date):
    input_date_obj = datetime.strptime(input_date, '%b %d, %Y')
    output_date = input_date_obj.strftime('%m/%d/%Y')
    return output_date


# Function to calculate the difference in days between two dates
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


# Function to retrieve text content from an XPath
def get_text(xpath):
    try:
        return tree.xpath(xpath)[0]
    except:
        return ""


# Function to retrieve links from an XPath
def get_links(xpath):
    elements = tree.xpath(xpath)
    links = [element.get('href') if element is not None else '' for element in elements]
    return links


reviews = []  # Store scraped reviews
page = 1

# Get initial page content for scraping review links
response = requests.get(url)
tree = html.fromstring(response.content)

# Find the number of pages available for reviews
last_link = int(tree.xpath('//li[@class="last"]//span//text()')[0])

# Generate a list of URLs for all available pages of reviews
list_of_urls = [url.replace("/1/", f"/{page_no}/") for page_no in range(1, last_link + 1)]

page_no = 1
found_reviews_within_days = True

# Loop through each page URL to scrape reviews
for single_url in list_of_urls:
    print(f"Scraping page no {page_no} ")
    response = requests.get(single_url)
    tree = html.fromstring(response.content)
    no_of_reviews = len(tree.xpath('//div[@class="f-component-info"]'))

    for review_card in range(1, no_of_reviews + 1):
        card_xpath = f'(//div[@class="f-component-info"])[{review_card}]'

        # Extract information from each review card
        user_name = get_text(f'{card_xpath}//a/span/text()')
        stars = get_text(f'{card_xpath}//div[@class="rating-title action-element bold-link-third"]//text()')
        stars = stars.split('.')[0].strip()
        date = get_text(f'{card_xpath}//time[@class="mr24px-desktop"]//text()')
        titles = get_text(f'{card_xpath}//h2/text()')
        titles = titles.strip()
        ids = get_text(f"{card_xpath}//span[contains(@class, 'inline-row')]/text()")
        ids = ids.strip().replace('#', '').split('&')[0]
        details = get_text(f'{card_xpath}//div[@class="overflow-text"]//text()')
        details = details.strip()

        if user_name == "":
            user_name = get_text(f'{card_xpath}//span[@class="user"]/text()')

        if titles == "":
            titles = get_text(f'{card_xpath}//h2/span/text()')

        if stars == "":
            stars = ''
        if titles == "":
            titles = 'NA'
        if details == "":
            details = 'NA'

        published_date = date
        published_date = convert_date_format(published_date)
        days_difference = days_until_date(published_date)

        if days_difference <= no_of_days:
            data = {
                'User': user_name,
                'Stars': stars,
                'Date': published_date,
                'id': ids,
                'Source_url': single_url,
                'Titles': titles,
                'Details': details
            }

            reviews.append(data)

        else:
            found_reviews_within_days = False
            break

    # Check if reviews within the specified number of days have been found
    if not found_reviews_within_days:
        break
    if no_of_reviews == 0:
        break

    page_no += 1

# Write scraped reviews to a JSON file
current_date = datetime.now().strftime("%m%d%y")
file_name = f"pissed_consumer_scraper_{current_date}_{scraping_site_name}.json"

# Saving the data in json file
with open(f'{file_name}', 'w', encoding='utf-8') as outfile:
    json.dump(reviews, outfile, indent=4)

# Printing the message
print("Data has been Scraped and saved")
