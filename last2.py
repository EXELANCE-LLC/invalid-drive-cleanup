import subprocess
import sys
import importlib.util

def package_installed(package_name):
    package_spec = importlib.util.find_spec(package_name)
    return package_spec is not None

required_packages = ['requests', 'logging', 'shutil', 'datetime']  # Örnek bağımlılıklar

missing_packages = [pkg for pkg in required_packages if not package_installed(pkg)]

if missing_packages:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing_packages], stdout=subprocess.DEVNULL)

# Import after checking
import os
import sys
import ctypes
import re
import requests
import json
import subprocess
import logging
import shutil
from datetime import datetime



def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

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
    encoding='utf-8'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def first_word_provider_name(name):
    """ Extract the first word of the provider name for comparison. """
    return name.split()[0].lower()

# ocr.space API https://ocr.space/OCRAPI
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
    processed_files = set()

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

    # Collect all OCR provider names
    ocr_provider_first_words = set(first_word_provider_name(item['ProviderName']) for item in ocr_data.values())

    # Find and remove drivers by first word of provider name match
    for provider_first_word in ocr_provider_first_words:
        for driver in dism_data:
            if first_word_provider_name(driver['ProviderName']) == provider_first_word:
                pub_name = driver['PublishedName']
                if not remove_driver(pub_name):
                    # Burada hata mesajı artık loglanmayacak, eğer hata mesajı hiç göstermek istemiyorsanız bu satırı da silebilirsiniz.
                    pass
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


def delete_directory_contents(directory):
    """Belirtilen dizinin içeriğini siler."""
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            logging.error(f"Failed to delete {item_path}: {e}")

def clean_up(base_path):
    """Dism çıktısını ve img, json klasörlerindeki tüm dosyaları siler."""
    dism_json_path = 'dism_drivers.json'
    json_folder_path = os.path.join(base_path, 'json')
    img_folder_path = os.path.join(base_path, 'img')

    if os.path.exists(dism_json_path):
        os.remove(dism_json_path)
        logging.info(f"{dism_json_path} has been deleted successfully.")

    delete_directory_contents(json_folder_path)
    logging.info(f"All files in {json_folder_path} have been deleted successfully.")

    delete_directory_contents(img_folder_path)
    logging.info(f"All files in {img_folder_path} have been deleted successfully.")

def main():
    if not is_admin():
        print("Please open the terminal with administrator privileges.")
        sys.exit(1)

    base_path = '.\\'
    process_images(base_path)
    save_dism_output_to_json()
    json_folder = os.path.join(base_path, 'json')
    match_and_remove_drivers(json_folder)
    clean_up(base_path)

if __name__ == "__main__":
    main()
