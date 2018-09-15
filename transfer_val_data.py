import os, shutil
import pandas as pd
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
from utils import *

vid_files = 'charades/Charades_v1_480/'
val_vid_names = 'CharadesDet/Annotations'
val_vid_folder = 'CharadesDet/val_videos_downscaled'

check_and_create(val_vid_folder)


def transfer_files():
	for n in os.listdir(val_vid_names):
		print os.path.join(vid_files,n+'.mp4')
		shutil.copy2(os.path.join(vid_files,n+'.mp4'),os.path.join(val_vid_folder,n+'.mp4'))



transfer_files()

# parse_xml()
