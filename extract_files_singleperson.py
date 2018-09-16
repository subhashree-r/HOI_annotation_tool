import os
file = open("single_person_videos.txt", "r")
for line in file:
	line = line.rstrip("\n")
	s = "Charades_v1_480/" + line + ".mp4"
	cmd = "mv " + s + " CharadesDet/focus_videos_singleperson/"
	os.system(cmd)