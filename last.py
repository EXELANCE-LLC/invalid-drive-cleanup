import os
import re
import requests
import json
import subprocess
import logging
from datetime import datetime

# Log dosyası için klasör ve dosya ismi ayarı
log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f'{log_directory}/log_{current_time}.log'

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_filename,
    filemode='w',
    encoding='utf-8'  # Log dosyasını UTF-8 formatında kaydet
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def normalize_provider_name(name):
    """ Normalize the provider name for more reliable comparison. """
    return re.sub(r'[\.,\s]+', '', name.lower())  # Remove spaces, periods and commas and convert to lower case for normalization

def ocr_space_file(filename, overlay=False, OCREngine=5, api_key='K86699985588957', language='eng', FileType='Auto', IsCreateSearchablePDF=False, isSearchablePdfHideTextLayer=True, detectOrientation=False, isTable=False, scale=True, detectCheckbox=False):
    payload = {
        'isOverlayRequired': overlay,
        'apikey': api_key,
        'language': language,
        'FileType': FileType,
        'IsCreateSearchablePDF': IsCreateSearchablePDF,
        'isSearchablePdfHideTextLayer': isSearchablePdfHideTextLayer,
        'detectOrientation': detectOrientation,
        'scale': scale,
        'OCREngine': OCREngine,
    }
    try:
        with open(filename, 'rb') as f:
            response = requests.post('https://api.ocr.space/parse/image',
                                     files={filename: f},
                                     data=payload,
                                     timeout=5)
        logging.info(f"OCR processing completed for {filename}")
        return response.json()
    except Exception as e:
        logging.error(f"Error processing file {filename}: {e}")
        return None

def process_images(base_path):
    image_folder = os.path.join(base_path, 'img')
    json_folder = os.path.join(base_path, 'json')
    
    os.makedirs(json_folder, exist_ok=True)
    logging.info("Image processing started.")

    for filename in os.listdir(image_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            full_path = os.path.join(image_folder, filename)
            logging.info(f"Processing image {filename}")
            result = ocr_space_file(full_path, language='eng')
            if result and 'ParsedResults' in result and result['ParsedResults']:
                parsed_text = result['ParsedResults'][0]['ParsedText']
                lines = parsed_text.split("\n")
                json_output = []
                current_pair = {}
                for line in lines:
                    line = line.strip()
                    if line.endswith('.sys'):
                        line = line[:-4] + '.inf'  # Convert sys to inf
                        current_pair['OriginalFileName'] = line
                    else:
                        if line:
                            current_pair['ProviderName'] = line
                    if 'OriginalFileName' in current_pair and 'ProviderName' in current_pair:
                        json_output.append(current_pair)
                        logging.info(f"Processed OriginalFileName: {current_pair['OriginalFileName']} with ProviderName: {current_pair['ProviderName']}")
                        current_pair = {}
                json_filename = os.path.join(json_folder, f'{os.path.splitext(filename)[0]}_output.json')
                with open(json_filename, 'w') as json_file:
                    json.dump(json_output, json_file, indent=4)
                logging.info(f"Saved processed data to {json_filename}")
            else:
                logging.warning(f"No results found or error processing {filename}")

def save_dism_output_to_json():
    logging.info("Fetching DISM output...")
    result = subprocess.run('dism /online /get-drivers /format:table', capture_output=True, text=True, shell=True)
    lines = result.stdout.split('\n')
    drivers_list = []
    start_index = next(i for i, line in enumerate(lines) if '------' in line) + 1
    for line in lines[start_index:]:
        parts = [part.strip() for part in line.split('|') if part.strip()]
        if len(parts) >= 5:
            drivers_list.append({'PublishedName': parts[0], 'OriginalFileName': parts[1], 'ProviderName': parts[4]})
    with open('dism_drivers.json', 'w') as f:
        json.dump(drivers_list, f, indent=4)
    logging.info("DISM driver data saved to JSON.")

def match_and_remove_drivers(json_folder):
    with open('dism_drivers.json', 'r') as f:
        dism_data = json.load(f)
    ocr_data = {}
    processed_files = set()  # To avoid processing the same OriginalFileName multiple times

    for json_file in os.listdir(json_folder):
        if json_file.endswith('.json'):
            with open(os.path.join(json_folder, json_file), 'r') as f:
                data = json.load(f)
            for item in data:
                lower_original_name = item['OriginalFileName'].lower()
                if lower_original_name not in processed_files:
                    ocr_data[lower_original_name] = item
                    processed_files.add(lower_original_name)
                    logging.info(f"Loaded OCR data for {item['OriginalFileName']} with ProviderName: {item['ProviderName']} for processing.")

    matched_drivers = []
    unmatched_providers = []

    for driver in dism_data:
        original_name = driver['OriginalFileName'].lower()
        if original_name in ocr_data:
            normalized_dism_provider = normalize_provider_name(driver['ProviderName'])
            normalized_ocr_provider = normalize_provider_name(ocr_data[original_name]['ProviderName'])
            if normalized_dism_provider == normalized_ocr_provider:
                matched_drivers.append(driver['PublishedName'])
                logging.info(f"Match found and marked for removal: {driver['PublishedName']} for driver {driver['OriginalFileName']}")
            else:
                unmatched_providers.append((ocr_data[original_name]['ProviderName'], ocr_data[original_name]['OriginalFileName']))
                logging.info(f"No match found for {driver['OriginalFileName']} based on normalized ProviderName: DISM ({normalized_dism_provider}), OCR ({normalized_ocr_provider})")

    if matched_drivers:
        logging.info(f"Proceeding to remove matched drivers: {matched_drivers}")
        for pub_name in matched_drivers:
            if remove_driver(pub_name):
                logging.info(f"Driver {pub_name} removed successfully.")
            else:
                logging.warning(f"Failed to remove driver {pub_name}.")
    else:
        logging.info("No drivers matched based on OriginalFileName and ProviderName.")

    # Check unmatched provider names in DISM data
    if unmatched_providers:
        for unmatched_provider, original_filename in unmatched_providers:
            normalized_unmatched_provider = normalize_provider_name(unmatched_provider)
            for driver in dism_data:
                if normalized_unmatched_provider == normalize_provider_name(driver['ProviderName']):
                    logging.info(f"ProviderName match found for unmatched OriginalFileName {original_filename}. DISM PublishedName: {driver['PublishedName']} with Provider: {driver['ProviderName']}")
                    print(f"Match found by ProviderName for {original_filename}. DISM PublishedName: {driver['PublishedName']}")

def remove_driver(published_name):
    pnputil_path = r'C:\\Windows\\System32\\pnputil.exe'
    command = f'{pnputil_path} /delete-driver {published_name} /uninstall /force'
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    if "Driver package deleted successfully" in result.stdout:
        logging.info(f"Successfully removed {published_name}")
        return True
    else:
        logging.warning(f"Failed to remove {published_name}: {result.stdout}")
        return False

def main():
    base_path = '.\\'
    process_images(base_path)
    save_dism_output_to_json()
    json_folder = os.path.join(base_path, 'json')
    match_and_remove_drivers(json_folder)

if __name__ == "__main__":
    main()
