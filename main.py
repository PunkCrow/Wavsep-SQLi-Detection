from functions import perform_injection_tests, get_input_tag
from url_manager import get_random_url, check_url_reachability, is_valid_url


def main():
    url_file = 'urls.txt'

    # Prompt the user for a URL
    while True:
        url_to_test = input("Enter a URL to check for SQL injection vulnerabilities, or write 'random' to use a random URL from the list: ").strip()
        # If the user didn't enter a URL, pick a random one from the list
        if url_to_test.lower() == 'random':
            url_to_test = get_random_url(url_file)
            break
        elif is_valid_url(url_to_test):
            print("Valid URL. Checking if URL is reachable.")
            break
        else:
            print("Please enter a valid URL or 'random'.")

    if check_url_reachability(url_to_test):
        print(f"The URL {url_to_test} is up. Proceeding with tests...")
        name = get_input_tag(url_to_test)
        if not name:
            print("No input tag found!")
        else:
            perform_injection_tests(url_to_test)


if __name__ == '__main__':
    main()
