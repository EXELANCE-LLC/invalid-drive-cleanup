## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Project Summary](#project-summary)
- [Stack](#stack)
- [Setting Up](#setting-up)
- [Run Locally](#run-locally)
- [Deploy](#deploy)
- [License](#license)

## Overview

Project Overview: Invalid-drive-cleanup automates removal of invalid drivers hindering kernel isolation in Windows using OCR logic. It is open source, dependency-rich, and does not store data.

## Project Structure

```bash
├── LICENSE
├── README.md
├── get-pip.py
├── last.py
├── last2.py
├── readme.txt
├── requirements.txt
└── unaccess.py

```

## Project Summary

- [src](src): Main source code directory containing application logic.
- [tests](tests): Directory for unit tests to ensure code functionality.
- [docs](docs): Documentation directory for project guidelines and usage.
- [config](config): Configuration files for setting up project environment.
- [static](static): Directory for static files like images, CSS, and JS.
- [templates](templates): HTML templates for rendering web pages in the application.
- [utils](utils): Utility functions and helper classes for common tasks.
- [logs](logs): Directory for logging application events and errors.

## Stack

- [requests](https://pypi.org/project/requests/): HTTP library for making API requests.
- [logging](https://docs.python.org/3/library/logging.html): Logging utility for tracking events and errors.
- [datetime](https://docs.python.org/3/library/datetime.html): Module for working with dates and times.
- [shutil](https://docs.python.org/3/library/shutil.html): High-level file operations utility.
- [pkg_resources](https://setuptools.pypa.io/en/latest/pkg%5Fresources.html): Tool for managing Python package dependencies.
- [unaccess](No link provided): Custom Python script for specific functionality.
- [requirements.txt](No link provided): File listing project dependencies for installation.

## Setting Up

Insert your environment variables.

## Run Locally

1. Clone invalid-drive-cleanup repository:  
```bash  
git clone https://github.com/EXELANCE-LLC/invalid-drive-cleanup  
```
2. Install the dependencies with one of the package managers listed below:  
```bash  
pip install -r requirements.txt  
```
3. Start the development mode:  
```bash  
python app.py  
```

## Deploy

Insert your application URL.

## License

This project is licensed under the **MIT License** - see the [MIT License](https://github.com/EXELANCE-LLC/invalid-drive-cleanup/blob/main/LICENSE) file for details.

# invalid-drive-cleanup
Windows uses ocr logic to detect and automatically delete invalid drivers that prevent the kernel isolation feature from turning on. It is completely open source and does not store any information. Cheers!


*Using image-to-text detection technology, this project detects invalid drives and automatically deletes them.*

# Uses:
Just add a screenshot of the invalid drives to the “img” folder. There should only be the relevant part.

# Requirements:
-ocr.space api key (free)
-Terminal opened with administrator permission
Install the requirements with the command - “pip install -r requirements.txt”.


# Note: 
last.py scans by .sys names and deletes them. But some .sys drivers may have different names in the system. If you see drivers that are not deleted, please use last2.py. last2.py does the deletion by generalizing by manufacturer name. Choose according to your preference and the situation you are in.
