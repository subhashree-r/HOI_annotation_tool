import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import itertools
import csv
from itertools import izip
import re
import os


def check_and_create(input_dir):
	if not os.path.isdir(input_dir):
		os.makedirs(input_dir)
