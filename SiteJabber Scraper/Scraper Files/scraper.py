import requests
from xextract import String
from datetime import datetime
import json
import sys

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
          "Example: python script.py  https://super-com.pissedconsumer.com/")
    sys.exit(1)

scraping_site_name = url.split(".com")[0].split("//")[-1].split(".")[0].capitalize()
url = f"https://www.sitejabber.com/reviews/{url}"

page_no = 0
payload = f"_method=POST&page={page_no}&=search%3D&=timeframe%3D&=_Token%5Bunlocked%5D%3D&sort=published&filter%5B%5D=0&filter%5B%5D=0&filter%5B%5D=0&filter%5B%5D=0&_Token%5Bfields%5D=3faddf844284abffdf223f82eae5724f057b925c%253A&_Token%5Bdebug%5D=%255B%2522%255C%252Freviews%255C%252Fsuper.com%2522%252C%255B%2522page%2522%252C%2522search%2522%252C%2522sort%2522%252C%2522rating%2522%252C%2522timeframe%2522%252C%2522filter%2522%255D%252C%255B%255D%255D"
headers = {
    "authority": "www.sitejabber.com",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.sitejabber.com",
    "referer": "https://www.sitejabber.com/reviews/super.com",
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}


# Get star rating
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


# Get the text from the URL
response = requests.request("POST", url, data=payload, headers=headers)
get_data = response.text
json_data = response.json()['html']

stars_elements = [
    '0%', '20%', '40%', '60%', '80%', '100%'
]

star_rating = None
found_star = False

reviews = []

last_page_no = (String(xpath='//span[@class="pagination__numbers__item"]/a')).parse(json_data)
last_page_no = int(last_page_no[-1].replace(',', '').strip())

found_reviews_within_days = True
# Loop through all the pages
for page_no in range(1, last_page_no + 1):
    payload = f"_method=POST&page={page_no}&=search%3D&=timeframe%3D&=_Token%5Bunlocked%5D%3D&sort=published&filter%5B%5D=0&filter%5B%5D=0&filter%5B%5D=0&filter%5B%5D=0&_Token%5Bfields%5D=3faddf844284abffdf223f82eae5724f057b925c%253A&_Token%5Bdebug%5D=%255B%2522%255C%252Freviews%255C%252Fsuper.com%2522%252C%255B%2522page%2522%252C%2522search%2522%252C%2522sort%2522%252C%2522rating%2522%252C%2522timeframe%2522%252C%2522filter%2522%255D%252C%255B%255D%255D"
    response = requests.request("POST", url, data=payload, headers=headers)
    get_data = response.text
    json_data = response.json()['html']
    no_of_reviews = String(xpath='//div[@class="review__flex "]').parse(json_data)
    print(f"Page {page_no} of {last_page_no} pages")

    # Loop through all the reviews in a page
    for review in range(1, len(no_of_reviews) + 1):
        card_xpath = f'(//div[@class="review__flex "])[{review}]'
        for width in stars_elements:
            stars_width = String(xpath=f'{card_xpath}//div[@class="review__info"]//div[@style="width: {width};"]') \
                .parse(json_data)
            if stars_width:
                star_rating = get_star_rating(width)
                found_star = True
                break

        # Get the review data
        user_name = String(xpath=f'{card_xpath}//div[@class="review__author__name"]//span').parse(json_data)
        user_name = [name.replace('\u00a0', ' ') for name in user_name]
        stars = star_rating
        dates = String(xpath=f'{card_xpath}//div[@class="review__date"]').parse(json_data)
        dates = [date.replace('\n\t', ' ') for date in dates]
        dates = [date.strip() for date in dates]
        dates = [convert_date_format(date) for date in dates]
        ids_data = String(xpath=f'{card_xpath}//div[@class="review__title"]//a', attr='href').parse(json_data)
        ids = [id.split('#')[1] for id in ids_data]
        base_url = 'https://www.sitejabber.com'
        source_url = base_url + ids_data[0]
        titles = String(xpath=f'{card_xpath}//span[@class="review__title__text"]').parse(json_data)
        details = String(xpath=f'{card_xpath}//p[@style="margin-bottom:10px"]').parse(json_data)
        details = [detail.strip() for detail in details]

        for name, star, date, id, source, title, detail in zip(user_name, stars, dates, ids, source_url, titles,
                                                               details):
            # Check if the review was published within the specified number of days
            published_date = date
            days_difference = days_until_date(published_date)

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

                # Append the review data to the list
                reviews.append(data)
            else:
                found_reviews_within_days = False  # No more reviews within the specified number of days
                break
    if not found_reviews_within_days or len(
            no_of_reviews) == 0:
        break

# Save the data to a JSON file
current_date = datetime.now().strftime("%m%d%y")
file_name = f"Site_jabber_{current_date}_{scraping_site_name}.json"

with open(f'{file_name}', 'w', encoding='utf-8') as outfile:
    json.dump(reviews, outfile, indent=4)

print("Data has been Scraped and saved")
