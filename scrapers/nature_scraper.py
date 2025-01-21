from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time


def scrape_nature_careers_detailed_with_pagination():
    print("Setting up WebDriver...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    jobs = []

    try:
        base_url = "https://www.nature.com/naturecareers/jobs/phd-position"
        print(f"Accessing the Nature Careers job listings: {base_url}")
        driver.get(base_url)

        while True:
            print(f"Scraping page: {driver.current_url}")
            # Wait for job cards to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.lister__item"))
            )
            job_listings = driver.find_elements(By.CSS_SELECTOR, "li.lister__item")
            print(f"Found {len(job_listings)} job postings on this page.")

            for job_card in job_listings:
                try:
                    # Extract job title and URL
                    title = job_card.find_element(By.CSS_SELECTOR, "h3.lister__header a span").text.strip()
                    job_url = job_card.find_element(By.CSS_SELECTOR, "h3.lister__header a").get_attribute("href")

                    # Navigate to job detail page
                    driver.execute_script("window.open(arguments[0], '_blank');", job_url)
                    driver.switch_to.window(driver.window_handles[-1])

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.mds-surface__inner"))
                    )

                    # Extract details from the job detail page
                    employer = driver.find_element(By.XPATH, "//dt[text()='Employer']/following-sibling::dd").text.strip()
                    location = driver.find_element(By.XPATH, "//dt[text()='Location']/following-sibling::dd").text.strip()
                    salary = (
                        driver.find_element(By.XPATH, "//dt[text()='Salary']/following-sibling::dd").text.strip()
                        if driver.find_elements(By.XPATH, "//dt[text()='Salary']/following-sibling::dd")
                        else "Not specified"
                    )
                    closing_date = (
                        driver.find_element(By.XPATH, "//dt[text()='Closing date']/following-sibling::dd").text.strip()
                        if driver.find_elements(By.XPATH, "//dt[text()='Closing date']/following-sibling::dd")
                        else "Not specified"
                    )
                    description = (
                        driver.find_element(By.CSS_SELECTOR, "div.mds-grid-row p").text.strip()
                        if driver.find_elements(By.CSS_SELECTOR, "div.mds-grid-row p")
                        else "No description provided"
                    )

                    jobs.append({
                        "Title": title,
                        "Employer": employer,
                        "Location": location,
                        "Salary": salary,
                        "Closing Date": closing_date,
                        "URL": job_url,
                        "Description": description,
                    })

                    print(f"Extracted job: {title}")
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                except Exception as e:
                    print(f"Error extracting job details: {e}")
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    continue

            # Check for "Next" button and navigate
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "ul.paginator__items a[rel='next']")
                driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Ensure button is in view
                driver.execute_script("arguments[0].click();", next_button)  # Click the button using JavaScript
                print("Navigating to the next page...")
                time.sleep(5)  # Allow the next page to load
            except Exception as e:
                print(f"No more pages or navigation issue: {e}")
                break

        # Save data to CSV
        output_path = "nature_positions_detailed_with_pagination.csv"
        try:
            pd.DataFrame(jobs).to_csv(output_path, index=False)
            print(f"Job data successfully saved to {output_path}")
        except Exception as e:
            print(f"Error saving job data to CSV: {e}")

    except Exception as e:
        print(f"Scraping error: {e}")
    finally:
        driver.quit()
        print("WebDriver closed.")


if __name__ == "__main__":
    scrape_nature_careers_detailed_with_pagination()
