Using image-to-text detection technology, this project detects invalid drives and automatically deletes them.

Uses:
Just add a screenshot of the invalid drives to the “img” folder. There should only be the relevant part.

Requirements:
-ocr.space api key (free)
-Terminal opened with administrator permission
Install the requirements with the command - “pip install -r requirements.txt”.


Note: last.py scans by .sys names and deletes them. But some .sys drivers may have different names in the system. If you see drivers that are not deleted, please use last2.py. last2.py does the deletion by generalizing by manufacturer name. Choose according to your preference and the situation you are in.