from bs4 import BeautifulSoup
import requests
import urllib3
import time
import csv
import datetime

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

elementary_url = "https://www.app.edu.gov.on.ca/eng/sift/index.asp"
secondary_url = "https://www.app.edu.gov.on.ca/eng/sift/indexSec.asp"
school_profile_url_prefix = "https://www.app.edu.gov.on.ca/eng/sift/schoolProfile.asp?SCH_NUMBER="

def get_schools(url):
    """
    Get a list of school IDs from the given url.
    :param url:
    :return:
    """
    response = requests.get(url=url, headers=headers)
    web_page = response.text
    soup = BeautifulSoup(web_page, 'html.parser')

    # Parse the school list
    options = soup.find(name='select', id='SCH_NUMBER').find_all(name='option')
    school_ids = [option.get('value') for option in options]
    print(f"Found {len(school_ids)} schools")

    return school_ids


def get_school_data(school_id):

    school_dict = {}

    school_url = school_profile_url_prefix + str(school_id)
    response = requests.get(url=school_url, headers=headers)
    web_page = response.text
    soup = BeautifulSoup(web_page, 'html.parser')

    # Parse the school data
    detail_lines = soup.find(name='div', class_='content').find_all(name='div')
    detail_lines_text_list = [line for line in detail_lines][:8]
    # print(detail_lines_text_list)
    for line in detail_lines_text_list:
        text = line.text
        if ":" not in text:
            continue
        key = text.split(':')[0].strip()
        value = text.split(':')[1].strip()
        try:
            link = line.find('a').get('href')
        except:
            link = None

        if "Address" in key:
            school_dict['address'] = value
        elif "Phone" in key:
            school_dict['phone'] = value
        elif "Fax" in key:
            school_dict['fax'] = value
        elif "Enrolment" in key:
            school_dict['enrolment'] = value
        elif "Grades" in key:
            school_dict['grades'] = value
        elif "School Website" in key:
            school_dict['school_name'] = value
            school_dict['school_website'] = link
        elif "Board Name" in key:
            school_dict['board_name'] = value
        elif "Board Website" in key:
            school_dict['board_website'] = link

    return school_dict

def main():

    # Get a list of school IDs
    type_select = input("Parse primary or elementary school? Enter 1 for primary, 2 for secondary: ")
    if type_select == "1":
        school_ids = get_schools(elementary_url)
    elif type_select == "2":
        school_ids = get_schools(secondary_url)
    else:
        print("Invalid input")
        return

    iteration = input("How many schools do you want to parse? Type 0 for all: ")

    # Get current time
    now = datetime.datetime.now()
    print(f"Start time: {now}")

    # Create a csv file
    with open(f'{type_select}_{now}.csv', 'w', newline='') as csvfile:
        fieldnames = ['school_id', 'school_name', 'school_website', 'board_name', 'board_website', 'address', 'phone', 'fax', 'enrolment', 'grades']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Get school data
        count = 0
        for school_id in school_ids:

            print(f"Parsing school {school_id} - {count} out of {len(school_ids)} schools ({round(count/len(school_ids)*100, 2)}%)")

            try:
                school_dict = get_school_data(school_id)
                time.sleep(0.5)
                school_dict['school_id'] = school_id
                writer.writerow(school_dict)
            except:
                print(f"Error parsing school {school_id}")

            count += 1
            if iteration != '0' and count >= int(iteration):
                break

    print(f"Done! {count} schools parsed.")


if __name__ == '__main__':
    main()