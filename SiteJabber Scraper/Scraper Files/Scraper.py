from xextract import String
from datetime import datetime
import json
import sys
import requests

# Check for command-line arguments
try:
    # Construct the initial URL for scraping reviews
    base_url = "https://www.sitejabber.com/reviews/"
    enter_url = str(sys.argv[1])
    base_parts = base_url.split(".com")
    url = enter_url.split("/")[-1]

    # Extract the number of days input from the command line
    no_of_days = int(sys.argv[2])
except:
    print("Please enter the url and no of days as arguments "
          "Example: python script.py  https://www.sitejabber.com/reviews/ ")
    sys.exit(1)


# Function to convert date format from 'Month Day, Year' to 'MM/DD/YYYY'
def convert_date_format(input_date):
    try_formats = [
        '%B %d%a, %Y',
        '%B %dst, %Y',
        '%B %dnd, %Y',
        '%B %drd, %Y',
        '%B %dth, %Y'
    ]

    for date_format in try_formats:
        try:
            input_date_obj = datetime.strptime(input_date, date_format)
            output_date = input_date_obj.strftime('%m/%d/%Y')
            return output_date
        except ValueError:
            pass

    return "Invalid date format"


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


# Function for getting star rating
def get_star_rating(width):
    if width == '0%':
        return '5'
    elif width == '20%':
        return '4'
    elif width == '40%':
        return '3'
    elif width == '60%':
        return '2'
    elif width == '80%':
        return '1'
    else:
        return 'Unknown'


# Store scraped reviews
reviews = []

# Get the text from the URL
url = f'https://www.sitejabber.com/reviews/{url}'
response = requests.get(url)
get_text = response.text

# Find the number of reviews available for scraping
no_of_reviews = '//div[@class="review__flex "]'
no_of_reviews = String(xpath=no_of_reviews).parse_html(get_text)

# website name
scraping_site_name = url.split("/")[-1].capitalize()

# Loop through each review card to scrape review data
for review in range(1, len(no_of_reviews) + 1):
    card_xpath = f'(//div[@class="review__flex "])[{review}]'
    stars_elements = [
        '0%', '20%', '40%', '60%', '80%', '100%'
    ]

    star_rating = None
    found_star = False

    for width in stars_elements:
        stars_width = String(xpath=f'{card_xpath}//div[@class="review__info"]//div[@style="width: {width};"]') \
            .parse_html(get_text)
        if stars_width:
            star_rating = get_star_rating(width)
            found_star = True
            break

    if not found_star:
        star_rating = '0'

    user_name = String(xpath=f'{card_xpath}//span[@class="review__author__name__link"]').parse_html(
        get_text)
    user_name = [name.replace('\u00a0', ' ') for name in user_name]
    stars = star_rating
    dates = String(xpath=f'{card_xpath}//div[@class="review__date"]').parse_html(get_text)
    dates = [date.replace('\n\t', ' ') for date in dates]
    dates = [date.strip() for date in dates]
    dates = [convert_date_format(date) for date in dates]
    ids_data = String(xpath=f'{card_xpath}//div[@class="review__title"]//a', attr='href').parse_html(get_text)
    ids = [id.split('#')[1] for id in ids_data]
    base_url = 'https://www.sitejabber.com'
    source_url = base_url + ids_data[0]
    titles = String(xpath=f'{card_xpath}//span[@class="review__title__text"]').parse_html(
        get_text)
    details = String(xpath=f'{card_xpath}//p[@style="margin-bottom:10px"]').parse_html(get_text)
    details = [detail.strip() for detail in details]

    # Check if the review was published within the specified number of days
    for name, star, date, id, source, title, detail in zip(user_name, stars, dates, ids, source_url, titles, details):
        published_date = date
        days_difference = days_until_date(published_date)
        # Check if no of days is less than or equal to the input days
        if days_difference <= no_of_days:
            data = {
                'User': name,
                'Stars': star,
                'Date': published_date,
                'id': id,
                'Source_url': source_url,
                'Titles': title,
                'Details': detail
            }
            # reviews is a list of dictionaries
            reviews.append(data)

current_date = datetime.now().strftime("%m%d%y")
file_name = f"Site_jabber_{current_date}_{scraping_site_name}.json"

# Save the scraped data in a JSON file
with open(f'{file_name}', 'w', encoding='utf-8') as outfile:
    json.dump(reviews, outfile, indent=4)

print("Data has been Scraped and saved")
