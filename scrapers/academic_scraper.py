from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def scrape_academic_positions():
    print("Setting up WebDriver...")
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1200")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    base_url = "https://academicpositions.com/jobs/position/phd"
    jobs = []

    try:
        print(f"Accessing Academic Positions PhD page: {base_url}")
        driver.get(base_url)

        # Wait for the job announcements to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.list-group-item"))
        )

        while True:
            print("Extracting job announcements from the current page...")
            job_cards = driver.find_elements(By.CSS_SELECTOR, "div.list-group-item")
            print(f"Found {len(job_cards)} job announcements on the page.")

            for job_card in job_cards:
                try:
                    # Extract job title
                    title_element = job_card.find_element(By.CSS_SELECTOR, "h4")
                    title = title_element.text.strip()

                    # Extract job link
                    job_link_element = job_card.find_element(By.CSS_SELECTOR, "a.text-dark.text-decoration-none.job-link")
                    job_url = job_link_element.get_attribute("href")

                    # Extract employer
                    employer_element = job_card.find_element(By.CSS_SELECTOR, "span.text-primary a.job-link")
                    employer = employer_element.text.strip()

                    # Extract location
                    location_elements = job_card.find_elements(By.CSS_SELECTOR, "div.job-locations a.text-muted")
                    location = ", ".join([elem.text.strip() for elem in location_elements])

                    # Extract publication date and deadline
                    published = closing_in = job_type = ""
                    info_divs = job_card.find_elements(By.CSS_SELECTOR, "div.row-tight.text-muted div.col-auto")
                    for info in info_divs:
                        icon = info.find_element(By.TAG_NAME, "i").get_attribute("class")
                        if "fe-calendar" in icon:
                            published = info.text.strip()
                        elif "fe-watch" in icon:
                            closing_in = info.text.strip()
                        elif "fe-clipboard" in icon:
                            job_type = info.text.strip()

                    # Extract description
                    description_element = job_card.find_element(By.CSS_SELECTOR, "p.text-muted")
                    description = description_element.text.strip()

                    # Append the job details
                    jobs.append({
                        "Title": title,
                        "Employer": employer,
                        "Location": location,
                        "Published": published,
                        "Closing In": closing_in,
                        "Job Type": job_type,
                        "URL": job_url,
                        "Description": description
                    })

                    print(f"Extracted job: {title}")

                except Exception as e:
                    print(f"Error extracting job details: {e}")
                    continue

            # Navigate to the next page
            try:
                next_page_button = driver.find_element(By.CSS_SELECTOR, "a.page-link[rel='next']")
                driver.execute_script("arguments[0].click();", next_page_button)
                print("Navigating to the next page...")
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.list-group-item"))
                )
            except Exception as e:
                print("No more pages to navigate or unable to locate the next button.", e)
                break

        # Check collected data
        print(f"Collected {len(jobs)} job entries.")

        # Save data to a CSV file
        try:
            output_path = "/Users/usirotamatthias/Desktop/academic_positions.csv"  # Change to your desired path
            pd.DataFrame(jobs).to_csv(output_path, index=False)
            print(f"Data successfully saved to {output_path}")
        except Exception as e:
            print(f"Error saving data to CSV: {e}")

    finally:
        driver.quit()
        print("WebDriver closed.")

if __name__ == "__main__":
    scrape_academic_positions()
