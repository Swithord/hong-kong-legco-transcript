import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from parse import parse


def parse_and_save(filename):
    try:
        df = parse(os.path.join('files', filename))
        print(f"Parsing {filename}, rows found: {len(df)}")
        if not df.empty:
            datetime = filename.split('_')[-1].split('.')[0]
            if len(datetime) != 6:
                datetime = filename.split('_')[-2]
            if len(datetime) != 6:
                print(f"Warning: could not find datetime from file {filename}")
            year = datetime[:2]
            if int(year) <= 25:
                year = '20' + year
            else:
                year = '19' + year
            month = datetime[2:4]
            day = datetime[4:6]
            df['date'] = f'{year}-{month}-{day}'
            legislative_year = filename.split('_')[0].split('yr')[-1]
            df['legislative_year'] = legislative_year
        save_path = os.path.join('parsed', filename.split('.')[0] + '.csv')
        df.to_csv(save_path, index=False)
        return save_path
    except Exception as e:
        print(f"Exception in parsing {filename}: {e}")
        return None


result_df = pd.DataFrame()

files = os.listdir('files')
files_to_process = [f for f in files if not os.path.exists(os.path.join('parsed', f.split('.')[0] + '.csv'))]

if files_to_process:
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(parse_and_save, f): f for f in files_to_process}

        for future in as_completed(futures):
            filename = futures[future]
            try:
                csv_path = future.result()
                if csv_path and os.path.exists(csv_path):
                    new_df = pd.read_csv(csv_path)
                    result_df = pd.concat([result_df, new_df], ignore_index=True)
            except Exception as e:
                print(f"Error reading parsed CSV for {filename}: {e}")
else:
    print("No new files to parse.")

parsed_files = [f for f in os.listdir('parsed') if f.endswith('.csv')]
for pf in parsed_files:
    df = pd.read_csv(os.path.join('parsed', pf))
    result_df = pd.concat([result_df, df], ignore_index=True)

print(f"Total rows in combined dataframe: {len(result_df)}")
result_df.to_csv('transcripts.csv', index=False)
