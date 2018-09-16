import os
file = open("multi_person_vids.txt", "r")
for line in file:
	line = line.rstrip("\n")
	s = "Charades_v1_480/" + line + ".mp4"
	cmd = "mv " + s + " CharadesDet/focus_videos_multiperson/"
	os.system(cmd)