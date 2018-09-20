# import the necessary packages
import argparse
import cv2
import os
import os, shutil
import pandas as pd
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
from utils import *
import requests
import xml.etree.ElementTree as ET
import pandas as pd
# from convert_xml_df import *
import shutil

refPt = []
cropping = False

'''
Defining the paths
'''

vid_files = 'Charades_v1/'
val_vid = 'CharadesDet/Annotations'
val_vid_folder = 'CharadesDet/val_videos'
charades_annotation = 'charades/Charades'
val_images = 'CharadesDet/val_videos_images_downscaled/'
annotated_images = 'CharadesDet/val_videos_annotated_images_downscaled/'
check_and_create(annotated_images)
val_vid_names = os.listdir(val_vid)
f = open('multi_person_vids.txt')
multi_person_vids =  f.read().splitlines()
hoi_annotation = 'CharadesDet/hoi_annotations_single_final'

check_and_create(hoi_annotation)
# check_and_create(multi_object_instances)
test_csv = os.path.join(charades_annotation,'Charades_v1_test.csv')
df = pd.read_csv(test_csv,sep = ',', low_memory=False)

def load_annotation(filename):
	"""
	Load annotation file for a given image.
	Args:
		img_name (string): string of the image name, relative to
			the image directory.
	Returns:
		BeautifulSoup structure: the annotation labels loaded as a
			BeautifulSoup data structure
	"""
	xml = ""
	with open(filename) as f:
		xml = f.readlines()
	xml = ''.join([line.strip('\t') for line in xml])
	return BeautifulSoup(xml)

def parse_xml(fn):
	'''
	Function to parse xml per frame
	'''
	a = load_annotation(fn)
	objs = a.findAll('object')
	no_persons = 0
	data = []

	for obj in objs:
				obj_names = obj.findChildren('name')
				for name_tag in obj_names:
					# if str(name_tag.contents[0]) == category:
						# fname = obj.findChild('filename').contents[0]
						obj_name = str(name_tag.contents[0])
						bbox = obj.findChildren('bndbox')[0]
						xmin = int(bbox.findChildren('xmin')[0].contents[0])
						ymin = int(bbox.findChildren('ymin')[0].contents[0])
						xmax = int(bbox.findChildren('xmax')[0].contents[0])
						ymax = int(bbox.findChildren('ymax')[0].contents[0])

						data.append([obj_name, xmin, ymin, xmax, ymax])

	return data


font = cv2.FONT_HERSHEY_SIMPLEX
################################### Process the action class names ##########################################
f2 = open(os.path.join(charades_annotation,'Charades_v1_classes.txt'))
lines = f2.readlines()
id_action = {}
for line in lines:
	p = line.split()
	id = p[0]
	action = ' '.join(p[1:])
	id_action[id] = action

################### Process the object labels ###############################
f3 = open(os.path.join('CharadesDet','charade_object_classes.txt'))
objects = f3.read().splitlines()
def process_video(vid):
	print "Processing", vid
	cv2.namedWindow("image", cv2.WINDOW_NORMAL)
	frames = sorted(os.listdir(vid))
	frames.sort(key=lambda f: int(filter(str.isdigit, f)))
	vid_name = vid.split(os.path.sep)[-1]
	df_row = df.loc[df['id']==vid_name]
	actual_img_dir = os.path.join(val_images,vid_name)
	no_frames = len(os.listdir(actual_img_dir))
	a =  list(df_row['actions'])
	vid_actions = a[0].split(';')
	frame_idx = 0
	print "Number of frames {}".format(len(frames))
	while frame_idx < len(frames):
		frame = frames[frame_idx]
		back_frame = 0
		p_idxes = []
		ann = parse_xml(os.path.join(vid,frame))
		object_annotations = [['Object Name','xmin','ymin','xmax','ymax','xmin','ymin','xmax','ymax']]
		object_interactions = [['Object Interaction','xmin','ymin','xmax','ymax','xmin','ymin','xmax','ymax']]
		object_annotations.extend(ann)
		person_ann = [bb for bb in sorted(ann) if bb[0]=='person']
		obj_ann = [bb for bb in ann if bb[0]!='person']
		frame_objects = [bb[0] for bb in obj_ann]
		frame_num = frame.split('.')[0]
		frame_time = (float(df_row['length'])/float(no_frames))*float(frame_num)
		img_name =os.path.join(val_images,vid_name,frame_num+'.jpg')
		final_annotations = []
		img = cv2.imread(img_name)
		im = img.copy()
		object_action = {}
		for ac in vid_actions:
			labels = ac.split(' ')
			if float(labels[1])<=frame_time<=float(labels[2]):
				for w in frame_objects:
					obs = w.split('_')
					try:
						obs.remove('s')
					except:
						pass
					ob_bool = [1 for x in obs if x in id_action[labels[0]]]
					if any(ob_bool):
							object_action[w] = id_action[labels[0]]
		if person_ann and object_action:
			print frame

			successful = True
			for fa in object_action.values():

				while True:

					im_temp = im.copy()
					object = object_action.keys()[object_action.values().index(fa)]
					object_instances = [bb for bb in obj_ann if bb[0]==object]
					object_instances_keys = [ord(str(i+1)) for i in range(len(object_instances))]
					for id,bb in enumerate(object_instances):
						id+=1
						bbx = map(int, bb[1:])
						cv2.rectangle(im_temp, (bbx[0],bbx[1]),(bbx[2],bbx[3]),(0,0,255),2)
						cv2.putText(im_temp,str(id),((bbx[0]+bbx[2])/2,(bbx[1]+bbx[3])/2), font, 0.5,(255,0,0),2)
					cv2.putText(im_temp,fa,(10,10), font, 0.5,(0,255,0),2)
					cv2.putText(im_temp,object,(5, 40), font, 0.6,(255,0,0),2)
					cv2.imshow("image", im_temp)
					key = cv2.waitKey(1) & 0xFF
					if key == ord("0"):
						# frame_idx +=1
						break
					elif key in object_instances_keys:
						ann_tmp = [fa]
						ann_tmp.extend(map(int,person_ann[0][1:]))
						ann_tmp.extend(map(int,object_instances[int(chr(key))-1][1:]))
						object_interactions.append(ann_tmp)
						# frame_idx +=1
						break
					elif key == ord("a"):
						for k in range(len(object_instances)):
							ann_tmp = [fa]
							ann_tmp.extend(map(int,person_ann[0][1:]))
							ann_tmp.extend(map(int,object_instances[k][1:]))
							object_interactions.append(ann_tmp)
						# frame_idx +=1
						break
					elif key == ord("b"):
						object_interactions.pop()
						back_frame = 1
						frame_idx -=1
						break
					elif key == ord("0"):
						# frame_idx +=1
						break
				if back_frame:
					break
		if back_frame:
			continue
		else:
			frame_idx+=1
		hoi_seq_folder = os.path.join(hoi_annotation, vid_name)
		check_and_create(hoi_seq_folder)
		csv_file_obj = os.path.join(hoi_seq_folder,str(frame_num)+'_obj.csv')
		csv_file_int = os.path.join(hoi_seq_folder,str(frame_num)+'_int.csv')

		with open(csv_file_int,'wb') as out:
			writer  = csv.writer(out)
			writer.writerows(object_interactions)
		with open(csv_file_obj,'wb') as out:
			writer  = csv.writer(out)
			writer.writerows(object_annotations)
	if frame_idx == len(frames) and os.path.exists(os.path.join(hoi_annotation, vid_name)):
		success_log_file = os.path.join(os.getcwd(),os.path.join(hoi_annotation,vid_name,'log_success.txt'))
		with open(success_log_file,"w+") as f:
			f.write("success")
def main():

	next_img = cv2.imread('next.png')
	log_file = os.path.join(hoi_annotation,'log.txt')
	single_file = open('single_person_videos.txt')
	single_person_vids =  single_file.read().splitlines()
	# print single_person_vids
	f1 = open(log_file,'w+')
	for v in os.listdir(val_vid):

		if not os.path.exists(os.path.join(hoi_annotation, v,'log_success.txt')):
			if v in single_person_vids:
				process_video(os.path.join(val_vid,v))
				cv2.imshow("image",next_img)
				key = cv2.waitKey(0) & 0xFF
				if key == ord("\n") or key == ord("y") or key == ord("1") or key == ord("2"):
					continue
				else:
					break


if __name__ == '__main__':
	main()
