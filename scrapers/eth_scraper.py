import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scrape_eth_jobs():
    print("Setting up WebDriver...")

    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)

    jobs = []

    try:
        url = "https://www.jobs.ethz.ch/"
        print(f"Accessing the ETH Zurich job listings: {url}")
        driver.get(url)

        time.sleep(5)  # Allow the page to load fully

        job_listings = driver.find_elements(By.CSS_SELECTOR, "li.job-ad__item__wrapper")
        print(f"Found {len(job_listings)} job postings.")

        for listing in job_listings:
            try:
                # Extract basic job information
                title = listing.find_element(By.CSS_SELECTOR, "div.job-ad__item__title").text.strip()
                link = listing.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                company_info = listing.find_element(By.CSS_SELECTOR, "div.job-ad__item__company").text.strip()
                date, recruiter = map(str.strip, company_info.split("|", 1))

                # Filter for PhD positions
                if "PhD" in title or "Doctoral" in title:
                    # Navigate to job details page
                    driver.execute_script("window.open(arguments[0], '_blank');", link)
                    driver.switch_to.window(driver.window_handles[-1])

                    # Wait for the description to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.paragraph.description__paragraph"))
                    )

                    # Extract the first paragraph of the job description
                    description = driver.find_element(By.CSS_SELECTOR, "div.paragraph.description__paragraph p").text.strip()

                    jobs.append({
                        "Title": title,
                        "Employer": recruiter,
                        "Location": "ETH Zurich, Switzerland",
                        "Published": date,
                        "Closing In": "",  # ETH Zurich does not show application deadlines clearly
                        "Job Type": "PhD",
                        "URL": link,
                        "Description": description,
                    })
                    print(f"Extracted job: {title}")

                    # Close the detail tab and switch back
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                else:
                    print(f"Skipped job (not PhD): {title}")

            except Exception as e:
                print(f"Error extracting job details: {e}")
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                continue

        # Save jobs to CSV
        output_path = "eth_positions_with_description.csv"
        pd.DataFrame(jobs).to_csv(output_path, index=False)
        print(f"Job data successfully saved to {output_path}")

    except Exception as e:
        print(f"An error occurred during scraping: {e}")

    finally:
        driver.quit()
        print("WebDriver closed.")


if __name__ == "__main__":
    scrape_eth_jobs()

