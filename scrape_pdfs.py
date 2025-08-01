import requests
from datetime import datetime, timedelta
import time


def generate_legco_urls(start_year: int = 2014, end_year: int = 2024) -> list[tuple[str, str, int, str]]:
    """
    Generate URLs for the Legislative Council (LegCo) 'Official Record of Proceedings' from 1998 to 2024.
    The URLs directly link to files (e.g. pdf, htm, doc, etc.).
    Currently, only records from the 1998 legislative year onwards is supported.
    :param start_year: The first legislative year to generate URLs for.
    :param end_year: The last legislative year to generate URLs for.
    :return: A list of tuples containing the legislative year, date of the meeting in 'yymmdd' format, document index, and the URL.
    """
    parts = {
        'en': {
            datetime(2000, 6, 27): [f'https://www.legco.gov.hk/yr99-00/english/counmtg/hansard/000627f{part}.pdf' for part in ('a', 'b')],
            datetime(2000, 5, 24): [f'https://www.legco.gov.hk/yr99-00/english/counmtg/hansard/000524{part}.pdf' for part in ('fe', 't')],
            datetime(1999, 12, 2): ['https://www.legco.gov.hk/yr99-00/english/counmtg/hansard/991202fb.pdf'],
            datetime(1999, 7, 16): [f'https://www.legco.gov.hk/yr98-99/english/counmtg/hansard/99716fe{part}.pdf' for
                                    part in ('1', '2')],
            datetime(1999, 7, 15): [f'https://www.legco.gov.hk/yr98-99/english/counmtg/hansard/99715fe{part}.pdf' for
                                    part in ('1', '2')],
            datetime(1999, 7, 14): [f'https://www.legco.gov.hk/yr98-99/english/counmtg/hansard/99714fe{part}.pdf' for part in ('1', '2')],
            datetime(1999, 3, 10): [f'https://www.legco.gov.hk/yr98-99/english/counmtg/hansard/990310f{part}.htm' for part in ('a', 'b', 'c', 'd')],
            datetime(1997, 9, 27): [f'counmtg/hansard/970927{part}.htm' for part in ('a', 'b')],
            datetime(1998, 2, 25): [f'counmtg/hansard/980225{part}.doc' for part in ('a', 'b')],
            # thankfully none of the 96-97 legco meetings conflict with 97 provisional legco
            datetime(1997, 6, 27): [f'lc_sitg/hansard/970627f{part}.doc' for part in ('a', 'b', 'c')],
            datetime(1997, 6, 26): [f'lc_sitg/hansard/970626f{part}.doc' for part in ('a', 'b')],
            datetime(1997, 6, 25): [f'lc_sitg/hansard/970625f{part}.doc' for part in ('a', 'b')],
            datetime(1997, 6, 24): [f'lc_sitg/hansard/970624f{part}.doc' for part in ('a', 'b')],
            datetime(1997, 6, 23): [f'lc_sitg/hansard/970623f{part}.doc' for part in ('a', 'b')],
            datetime(1997, 6, 17): [f'lc_sitg/hansard/970617f{part}.doc' for part in ('a', 'b')],
            datetime(1997, 6, 11): [f'lc_sitg/hansard/970611f{part}.doc' for part in ('a', 'b')],
            datetime(1997, 6, 4): [f'lc_sitg/hansard/970604f{part}.doc' for part in ('a', 'b')],
            datetime(1997, 5, 28): [f'lc_sitg/hansard/970528f{part}.doc' for part in ('a', 'b', 'c', 'd')],
            datetime(1997, 4, 9): [f'lc_sitg/hansard/970409f{part}.doc' for part in ('a', 'b')],
            datetime(1996, 7, 28): ['lc_sitg/hansard/h950728.pdf'],
            datetime(1996, 5, 29): ['lc_sitg/hansard/han2905.htm'],
            datetime(1996, 5, 15): ['lc_sitg/hansard/han1505.htm'],
            datetime(1996, 5, 1): ['lc_sitg/hansard/han0105.htm'],
            datetime(1996, 2, 7): [f'lc_sitg/hansard/960207{part}.doc' for part in ('fe', 't')]
        }
    }
    urls = []

    for year1 in range(start_year, end_year + 1):
        year2 = year1 + 1
        if year1 < 2022:
            legco_year = f"yr{str(year1)[-2:]}-{str(year2)[-2:]}"
        else:
            # from 2022 onwards
            legco_year = f"yr{str(year1)}"

        if year1 == 1983:
            start_date = datetime(year1, 9, 27)
            end_date = datetime(year2, 9, 26)
        elif year1 < 1985:
            start_date = datetime(year1, 10, 1)
            end_date = datetime(year2, 8, 16) # account for 1977, 1979, 1982, 1985, etc.
        elif year1 < 1997:
            start_date = datetime(year1, 10, 1)
            end_date = datetime(year2, 7, 31)
        elif year1 == 1997: # provisional council
            start_date = datetime(year1, 2, 22)
            end_date = datetime(year2, 4, 8)
        elif year1 == 1998:
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

        base_url = f'https://www.legco.gov.hk/{legco_year}/english/'

        while current_date <= end_date:
            if (year1 in (1996, 1997)) or current_date.weekday() < 5:
                # check only weekdays, except for some years
                yyyymmdd = current_date.strftime("%Y%m%d")
                yymmdd = current_date.strftime("%y%m%d")
                mmdd = current_date.strftime("%m%d")
                ddmm = current_date.strftime("%d%m")

                if current_date in parts['en']:
                    files = parts['en'][current_date]
                elif year1 < 1995:
                    files = [f'lc_sitg/hansard/h{yymmdd}.pdf']
                elif current_date <= datetime(1995, 12, 6):
                    files = [f'lc_sitg/hansard/han{ddmm}.htm']
                elif current_date <= datetime(1996, 7, 10):
                    files = [f'lc_sitg/hansard/{yymmdd}fe.doc']
                elif current_date <= datetime(1996, 10, 9):
                    files = [f'lc_sitg/hansard/han{ddmm}.htm']
                elif year1 == 1996:
                    # 96-97 colonial legco, after 10th oct 1996
                    files = [f"lc_sitg/hansard/{yymmdd}fe.doc"]
                elif year1 == 1997 and current_date <= datetime(1997, 10, 10):
                    # provision legco, before 10th oct 1997
                    files = [f"counmtg/hansard/{yymmdd}fe.htm"]
                elif year1 == 1997:
                    # provisional legco, after 10th oct 1997
                    files = [f"counmtg/hansard/{yymmdd}fe.doc"]
                elif current_date < datetime(1999, 6, 16):
                    # in the 1st legco before 16th June 1999, they are stored in HTM
                    files = [f"counmtg/hansard/{yymmdd}fe.htm"]
                elif current_date < datetime(2001, 10, 17):
                    # from 16th june 1999 to 16th october 2001
                    files = [f"counmtg/hansard/{yymmdd}fe.pdf"]
                elif year1 < 2006:
                    # from 17th october 2001 to 2005
                    files = [f"counmtg/hansard/cm{mmdd}ti-translate-e.pdf"]
                elif year1 < 2014:
                    # from 2006 to 2013
                    files = [f"counmtg/hansard/cm{mmdd}-translate-e.pdf"]
                else:
                    # from yr14-15 onwards
                    files = [f"counmtg/hansard/cm{yyyymmdd}-translate-e.pdf"]

                for i, file in enumerate(files):
                    urls.append((legco_year, current_date.strftime("%y%m%d"), i, base_url + file))
            current_date += timedelta(days=1)

    print(f"Finished URL generation. Total generated: {len(urls)}\n")
    return urls


def scrape_urls(urls: list[tuple[str, str, int, str]], sleep_time: float = 0.5) -> list[str]:
    """
    Scrape the URLs to check if they are valid and download the files.
    :param urls: A list of tuples containing the legislative year, date of the meeting in 'yymmdd' format, document index, and the URL.
    :param sleep_time: Time to sleep between requests to avoid overwhelming the server.
    :return: A list of valid URLs that were successfully downloaded.
    """
    valid_urls = []

    for i, (legco_year, yymmdd, idx, url) in enumerate(urls):
        try:
            print(f"[{i+1}/{len(urls)}] Checking: {url}")
            response = requests.get(url, timeout=15)

            if response.status_code == 200:
                print(f"Found: {url}")
                valid_urls.append(url)
                file_extension = url.split('.')[-1]
                name = f"{legco_year}_{yymmdd}_{idx}.{file_extension}"
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
    all_urls = generate_legco_urls(1985, 1989)
    existing_urls = scrape_urls(all_urls)

    with open("legco_pdf_urls.txt", "a") as f:
        for url in existing_urls:
            f.write(f"{url}\n")
