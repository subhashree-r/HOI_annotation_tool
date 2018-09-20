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
import argparse
from multiprocessing import Process
import threading

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
cropping = False

'''
Defining the paths
'''

vid_files = 'charades/Charades_v1/'
val_vid = 'CharadesDet/Annotations'
val_vid_folder = 'CharadesDet/val_videos'
charades_annotation = 'charades/Charades'
val_images = 'CharadesDet/val_videos_images_downscaled_new/'
annotated_images = 'CharadesDet/val_videos_annotated_images_downscaled/'
hoi_annotation  = 'CharadesDet/hoi_annotation_multi_person_final'
check_and_create(annotated_images)
check_and_create(hoi_annotation)
val_vid_names = os.listdir(val_vid)
f = open('multi_person_vids.txt')
multi_person_vids =  f.read().splitlines()

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
# print objects
cv2.namedWindow("image", cv2.WINDOW_NORMAL)

def process_video(vid):

	frames = sorted(os.listdir(vid))
	frames.sort(key=lambda f: int(filter(str.isdigit, f)))
	# no_frames = max([float(f.split('.')[0]) for f in frames])
	vid_name = vid.split(os.path.sep)[-1]
	actual_img_dir = os.path.join(val_images,vid_name)
	no_frames = len(os.listdir(actual_img_dir))
	df_row = df.loc[df['id']==vid_name]
	a =  list(df_row['actions'])
	vid_actions = a[0].split(';')
	vid_action_person = {}
	# no_frames = len(frames)
	frame_idx = 0
	while frame_idx < len(frames):
		frame = frames[frame_idx]
		print frame
		back_frame = 0
		p_idxes = []
		ann = parse_xml(os.path.join(vid,frame))
		object_annotations = [['Object Name','xmin','ymin','xmax','ymax','xmin','ymin','xmax','ymax']]
		object_annotations.extend(ann)
		person_ann = [bb for bb in sorted(ann) if bb[0]=='person']
		obj_ann = [bb for bb in ann if bb[0]!='person']
		frame_objects = [bb[0] for bb in obj_ann]
		frame_num = frame.split('.')[0]
		# print frame_num
		frame_time = (float(df_row['length'])/float(no_frames))*float(frame_num)
		img_name =os.path.join(val_images,vid_name,frame_num+'.jpg')
		print img_name
		final_annotations = []
		img = cv2.imread(img_name)
		im = img.copy()
		object_action = {}
		# print vid_actions
		for ac in vid_actions:
			# print a
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
		# print object_action
		p_id_bbx = {}
		p_id = 1
		im_person = im.copy()
		for p_bb in reversed(person_ann):
			ann_tmp=[]
			bb = map(int,p_bb[1:])
			cv2.rectangle(im_person, (bb[0],bb[1]),(bb[2],bb[3]),(0,0,255),2)
			cv2.putText(im_person,str(p_id),(bb[0]+10,bb[1]+20), font, 0.5,(0,0,255),2)
			p_id_bbx[p_id]=bb
			p_id+=1
		person_keys  = [ord(str(i+1)) for i in range(len(person_ann))]

		if not (person_ann and object_action):
			frame_idx+=1
		elif person_ann and object_action:
			object_interactions = [['Object Interaction','xmin','ymin','xmax','ymax','xmin','ymin','xmax','ymax']]
			for fa in object_action.values():
				print fa
				# frame_idx+=1

				im_temp = im_person.copy()
				object = object_action.keys()[object_action.values().index(fa)]
				object_instances = [bb for bb in obj_ann if bb[0]==object]
				object_instances_keys = [ord(str(i+1)) for i in range(len(object_instances))]
				for id,bb in enumerate(object_instances):
					id+=1
					bbx = map(int, bb[1:])
					cv2.rectangle(im_temp, (bbx[0],bbx[1]),(bbx[2],bbx[3]),(255,0,0),2)
					# cv2.putText(im_temp,bb[0]+'_'+str(id),(bbx[0]+10,bbx[1]+10), font, 0.6,(255,0,0),2)
					cv2.putText(im_temp,str(id),(bbx[0]+10,bbx[1]+20), font, 0.5,(255,0,0),2)
				while True:
					choose = True
					if fa in vid_action_person.keys() and len(object_instances)==1:
						im_temp1 = im.copy()
						cv2.putText(im_temp1,fa,(5,15), font, 0.5,(0,255,0),2)
						cv2.putText(im_temp1,'person',(5,50), font, 0.5,(0,0,255),2)
						cv2.putText(im_temp1,object,(5,70), font, 0.6,(255,0,0),2)

						bb_o = map(int,object_instances[0][1:])
						# print vid_action_person
						bb_p = p_id_bbx[vid_action_person[fa]]

						for bb in [bb_o,bb_p]:
							cv2.rectangle(im_temp1, (bb[0],bb[1]),(bb[2],bb[3]),(0,255,255),2)
						cv2.imshow("image", im_temp1)
						key1 = cv2.waitKey(0) & 0xFF
						if key1 == ord("b"):
							object_interactions.pop()
							frame_idx-=1
							back_frame =1
							break
						if key1 == ord("y"):
							ann_tmp = [fa]
							ann_tmp.extend(bb_p)
							# if len(object_instances)==1:
							ann_tmp.extend(bb_o)
							object_interactions.append(ann_tmp)
							choose =False
							# frame_idx+=1
							break
						elif key1 == ord("n"):
							choose = True
					if choose:
							# print fa
							cv2.putText(im_temp,fa,(5,15), font, 0.5,(0,255,0),2)
							cv2.putText(im_temp,'person',(5,50), font, 0.5,(0,0,255),2)
							cv2.putText(im_temp,object,(5,70), font, 0.6,(255,0,0),2)
							cv2.imshow("image", im_temp)
							key1 = cv2.waitKey(0) & 0xFF
							if key1 == ord("0"):
								frame_idx+=1
								break
							# if key1 == ord("b"):
							# 	frame_idx-=1
							# 	object_interactions.pop()
							# 	break
							key2 = cv2.waitKey(0) & 0xFF
							if key1 == ord("y") or key1 == ord("n"):
								key1 = cv2.waitKey(0) & 0xFF
								key2 = cv2.waitKey(0) & 0xFF

							elif key1 == ord("b"):
								object_interactions.pop()
								back_frame =1
								frame_idx -=1
								break
							elif len(object_instances)==1 and key1 in person_keys :

								ann_tmp = [fa]
								ann_tmp.extend(map(int,person_ann[int(chr(key1))-1][1:]))
								# if len(object_instances)==1:
								ann_tmp.extend(map(int,object_instances[0][1:]))
								object_interactions.append(ann_tmp)
								# frame_idx+=1
								# break
							elif len(object_instances)>1:
									# key2 = cv2.waitKey(33) & 0xFF
									key_p = int(chr(key1))
									# cv2.putText(im_temp,'Press person and object numbers',(5,70), font, 0.5,(0,255,0),2)
									key2 = cv2.waitKey(0) & 0xFF

									if key2 == ord("a"):
										for k in range(len(object_instances)):
											ann_tmp = [fa]
											ann_tmp.extend(map(int,person_ann[key_p-1][1:]))
											ann_tmp.extend(map(int,object_instances[k][1:]))
											object_interactions.append(ann_tmp)
											# frame_idx+=1
										# break
									else:
										key_o = int(chr(key2))
										print "key1",key_p,key_o
										ann_tmp = [fa]
										ann_tmp.extend(map(int,person_ann[key_p-1][1:]))
										ann_tmp.extend(map(int,object_instances[key_o-1][1:]))
										object_interactions.append(ann_tmp)
										# frame_idx+=1
							vid_action_person[fa] = int(chr(key1))
							frame_idx+=1
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

def show_video(vid):
	cv2.namedWindow("video", cv2.WINDOW_NORMAL)
	frames = sorted(os.listdir(vid))
	frames.sort(key=lambda f: int(filter(str.isdigit, f)))
	vid_name = vid.split(os.path.sep)[-1]
	actual_img_dir = os.path.join(val_images,vid_name)
	no_frames = len(os.listdir(actual_img_dir))
	for frame in frames:
		frame_num = frame.split('.')[0]
		# print frame_num
		# frame_time = (float(df_row['length'])/float(no_frames))*float(frame_num)
		img_name =os.path.join(val_images,vid_name,frame_num+'.jpg')
		# print img_name
		final_annotations = []
		img = cv2.imread(img_name)
		cv2.imshow("video",img)
		cv2.waitKey(1)

def parse_arguments():
	parser = argparse.ArgumentParser(description="Siamese Tracking")
	# parser.add_argument("-v",
	# 	"--vid_id", help="Path to MOTChallenge directory (train or test)",
	# 	required=True)


	return parser.parse_args()

def main():

	next_img = cv2.imread('next.png')
	print "Starting code"
	for v in os.listdir(val_vid):
		if not os.path.exists(os.path.join(hoi_annotation, v,'log_success.txt')):

			if v in multi_person_vids:
					process_video(os.path.join(val_vid,v))
					cv2.imshow("image",next_img)
					key = cv2.waitKey(0) & 0xFF
					if key == ord("\n") or key == ord("y") or key == ord("1") or key == ord("2"):
						continue
					else:
						break


if __name__ == '__main__':
	main()





#GOPZI
