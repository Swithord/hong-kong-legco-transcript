import requests
from datetime import datetime, timedelta
import time


def generate_legco_urls(start_year: int = 2014, end_year: int = 2024) -> list[tuple[str, str, str]]:
    """
    Generate URLs for the Legislative Council (LegCo) 'Official Record of Proceedings' from 1998 to 2024.
    The URLs directly link to files (e.g. pdf, htm, doc, etc.).
    Currently, only records from the 1998 legislative year onwards is supported.
    :param start_year: The first legislative year to generate URLs for.
    :param end_year: The last legislative year to generate URLs for.
    :return: A list of tuples containing the legislative year, date of the meeting in 'yymmdd' format, and the URL.
    """
    urls = []

    for year1 in range(start_year, end_year + 1):
        year2 = year1 + 1
        if year1 < 2022:
            legco_year = f"yr{str(year1)[-2:]}-{str(year2)[-2:]}"
        else:
            # from 2022 onwards
            legco_year = f"yr{str(year1)}"

        if year1 == 1998:
            start_date = datetime(year1, 7, 1)
            end_date = datetime(year2, 7, 31)
        elif year1 < 2022:
            # LegCo meets typically from october to july
            start_date = datetime(year1, 10, 1)
            end_date = datetime(year2, 7, 31)
        else:
            # From 2022, the meetings are year-round
            start_date = datetime(year1, 1, 1)
            end_date = datetime(year1, 12, 31)
        current_date = start_date

        while current_date <= end_date:
            if current_date.weekday() < 5:  # Weekdays only
                if year1 < 1998:
                    continue
                if current_date < datetime(1999, 6, 16):
                    # in the 1st legco before 16th June 1999, they are stored in HTM
                    yymmdd = current_date.strftime("%y%m%d")
                    url = f"https://www.legco.gov.hk/{legco_year}/english/counmtg/hansard/{yymmdd}fe.htm"
                elif current_date < datetime(2001, 10, 17):
                    # from 16th june 1999 to 16th october 2001
                    yymmdd = current_date.strftime("%y%m%d")
                    url = f"https://www.legco.gov.hk/{legco_year}/english/counmtg/hansard/{yymmdd}fe.pdf"
                elif year1 < 2006:
                    # from 17th october 2001 to 2005
                    mmdd = current_date.strftime("%m%d")
                    url = f"https://www.legco.gov.hk/{legco_year}/english/counmtg/hansard/cm{mmdd}ti-translate-e.pdf"
                elif year1 < 2014:
                    # from 2006 to 2013
                    mmdd = current_date.strftime("%m%d")
                    url = f"https://www.legco.gov.hk/{legco_year}/english/counmtg/hansard/cm{mmdd}-translate-e.pdf"
                else:
                    # from yr14-15 onwards
                    yyyymmdd = current_date.strftime("%Y%m%d")
                    url = f"https://www.legco.gov.hk/{legco_year}/english/counmtg/hansard/cm{yyyymmdd}-translate-e.pdf"
                urls.append((legco_year, current_date.strftime("%y%m%d"), url))
            current_date += timedelta(days=1)

    print(f"Finished URL generation. Total generated: {len(urls)}\n")
    return urls


def scrape_urls(urls: list[tuple[str, str, str]], sleep_time: float = 0.5) -> list[str]:
    """
    Scrape the URLs to check if they are valid and download the files.
    :param urls: A list of tuples containing the legislative year, date of the meeting in 'yymmdd' format, and the URL.
    :param sleep_time: Time to sleep between requests to avoid overwhelming the server.
    :return: A list of valid URLs that were successfully downloaded.
    """
    valid_urls = []

    for i, (legco_year, yymmdd, url) in enumerate(urls):
        try:
            print(f"[{i+1}/{len(urls)}] Checking: {url}")
            response = requests.get(url, timeout=15)

            if response.status_code == 200:
                print(f"Found: {url}")
                valid_urls.append(url)
                file_extension = url.split('.')[-1]
                name = f"{legco_year}_{yymmdd}.{file_extension}"
                with open(f"files/{name}", "wb") as f:
                    f.write(response.content)
                    print(f"Saved file: {name}")
            else:
                print(f"Not found (status {response.status_code}): {url}")
        except requests.RequestException as e:
            print(f"Request failed for {url}: {e}")

        time.sleep(sleep_time)

    print(f"\nDone. Found {len(valid_urls)} valid files.\n")
    return valid_urls


if __name__ == "__main__":
    all_urls = generate_legco_urls(1998, 2005)
    existing_urls = scrape_urls(all_urls)

    with open("legco_pdf_urls.txt", "a") as f:
        for year, url in existing_urls:
            f.write(f"{year},{url}\n")
