from pdfminer.high_level import extract_text
import html2text
import re
import pandas as pd
from argparse import ArgumentParser
from striprtf.striprtf import rtf_to_text
import textract

name_regex = r"^(?!MEMBER|CLERKS|CLERK IN|PUBLIC OFFICER)\s*[A-Z][A-Z\s,\'-]*(?:asked)?:"

def remove_lines_regex(text, pattern):
    if not text:
        return ''
    lines = text.split('\n')
    filtered_lines = [line for line in lines if not re.search(pattern, line)]
    return '\n'.join(filtered_lines)


def remove_after_keyword(text, keyword):
    if not text:
        return ''
    lines = text.split('\n')
    for i in range(len(lines) - 1, -1, -1):
        if keyword in lines[i]:
            return '\n'.join(lines[:i + 1])
    return text


def remove_lines_before_regex(text, patterns):
    # Remove all lines before the first occurrence of any pattern
    if not text:
        return ''
    lines = text.split('\n')
    for i in range(len(lines)):
        if any(re.search(pattern, lines[i]) for pattern in patterns):
            return '\n'.join(lines[i:])


def parse(filename: str) -> pd.DataFrame:
    """
Parse a Legislative Council transcript file and extract speaker names and their speeches.
    :param filename: Path to the file to parse (PDF, HTML, or DOC).
    :return: DataFrame containing speakers and their corresponding speeches.
    """
    file_type = filename.split('.')[-1].lower()
    if file_type == 'pdf':
        text = extract_text(filename)
    elif file_type == 'htm':
        h = html2text.HTML2Text()
        with open(filename, 'r', encoding='utf-8') as f:
            html_content = f.read()
            text = h.handle(html_content)
    else:
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                text = textract.process(filename, encoding='utf-8', errors='ignore').decode('utf-8')
            except:
                content = f.read()
                text = rtf_to_text(content, errors='ignore')

    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = re.sub(r'[\*_|]', '', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'^\d\\*.\s+', '\n', text, flags=re.MULTILINE)
    text = remove_lines_before_regex(text, [r"(in Cantonese)", r"(in English)", r"(in Chinese)", name_regex])
    for phrase in ('Suspended accordingly', 'Adjourned accordingly'):
        text = remove_after_keyword(text, phrase)
        text = remove_lines_regex(text, phrase)
    text = remove_lines_regex(text, r'LEGISLATIVE COUNCIL')
    text = remove_lines_regex(text, r'^\d+\s*$')
    text = re.sub(r'\(.*?\)', '', text, flags=re.DOTALL)
    text = re.sub(r'(?:\n[ ]*){3,}', '\n\n', text)

    # Attribute speakers to their "speeches"
    results = {'speaker': [], 'text': []}
    lines = text.split('\n')
    current_speaker = None
    current_text = ''
    for line in lines:
        if line.strip():  # Check if the line is not empty
            if re.match(name_regex, line):
                if current_speaker is not None:
                    results['speaker'].append(current_speaker)
                    results['text'].append(current_text.strip())
                current_speaker = line.split(':')[0].strip()
                current_speaker = current_speaker.replace('asked', '').strip()
                current_text = line.split(':')[1].strip() + ' '
            else:
                current_text += line.strip() + ' '
    if current_speaker is not None:
        results['speaker'].append(current_speaker)
        results['text'].append(current_text.strip())

    df = pd.DataFrame(results)
    return df


if __name__ == "__main__":
    parser = ArgumentParser(description="Parse a Legislative Council transcript PDF.")
    parser.add_argument('--filename', type=str, help='Path to the PDF file to parse.')
    parser.add_argument('--output', type=str, default='parsed_speech.csv', help='Output CSV file name.')
    args = parser.parse_args()

    df = parse(args.filename)
    df.to_csv(args.output, index=False)
