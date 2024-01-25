import re
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

target_major = "Information Technology"
file_name = f"Minnstate {target_major} Comparison Sheet.tsv"

# Initialize Selenium WebDriver
driver = webdriver.Firefox()  # Using Firefox driver
driver.get("https://www.minnstate.edu/campusesprograms/index.html#")

# Set the window size to be large so that the chat bot doesn't cover our windows
driver.set_window_size(1920, 1036)

# Click the search button using JavaScript to bypass visibility check, the page if it doesn't load quick will error otherwise
driver.execute_script(
    "arguments[0].click();",
    driver.find_element(By.CSS_SELECTOR, "#program-search-btn > span"),
)

# Wait for the loading element to disappear
WebDriverWait(driver, 10).until(
    EC.invisibility_of_element_located((By.CLASS_NAME, "loading"))
)

# Now that the loading element has disappeared, click on the select programs dropdown
driver.find_element(By.CSS_SELECTOR, ".ms-options-wrap > button").click()

# Find our major in the list and select it
for group in driver.find_elements(By.CSS_SELECTOR, ".optgroup"):
    major_name = group.find_element(By.CSS_SELECTOR, ".label").text
    # print(major_name)

    if major_name == target_major:
        # click the select all button
        group.find_element(By.CSS_SELECTOR, ".ms-selectall").click()
        break

# More simply you can do this, but then you can't dynamically choose the major:
# driver.find_element(By.CSS_SELECTOR, ".optgroup:nth-child(9) > .ms-selectall").click()

# Search
driver.find_element(By.CSS_SELECTOR, ".btn > span").click()

# Get the number of pages
page_nav = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "pagination"))
)
last_page_number = int(
    page_nav.find_element(By.CSS_SELECTOR, "ul.pagination li:nth-last-child(2) a").text
)

# Making the final CSV file
with open(file_name, mode="w") as file:
    writer = csv.writer(file, delimiter="\t")
    writer.writerow(["University", "Award", "Program Name", "Credits"])

    # Browse through all pages and add a new row for the information
    for page in range(1, last_page_number):
        # Navigate each program offered on this page
        programs = driver.find_elements(
            By.CSS_SELECTOR, ".program-list-result-row.listview"
        )

        for program in programs:
            program_name = program.find_element(By.CSS_SELECTOR, "h3 a").text

            # get the credit and awards
            label_div = program.find_element(By.CLASS_NAME, "col-lg-5")

            award, credits = re.search(
                r"Award:\s(.*?);\sCredits:\s(.*?)\s", label_div.text
            ).groups()

            # get the university name from its url, this is pretty jank, but it's because the DOM is jank
            university_url = program.find_element(
                By.CSS_SELECTOR,
                "div:first-child > div:nth-child(3) > div:nth-child(2) > address:first-child > div:first-child > div:first-child > a:first-child",
            ).text

            writer.writerow([university_url, award, program_name, credits])
        # navigate to the next page
        driver.find_element(By.LINK_TEXT, f"{page+1}").click()

# Close the WebDriver
driver.quit()
