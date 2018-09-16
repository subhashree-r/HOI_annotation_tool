# HOI Interaction Annotation Tool In Videos
## Installations

1. Install Open CV 2.4.11 version
2. Python 2.7
3. pip install -r requirements.txt


## Directory structure

```
/hoi_vid
  /CharadesDet
  /charades
  /charades-algorithms
```

`mkdir hoi_vid`

`cd hoi_vid`

`git clone https://github.com/xiaolonw/CharadesDet.git`

`wget http://ai2-website.s3.amazonaws.com/data/Charades_v1_480.zip`

## Running Commands
python hoi_annotate_multi_final.py
python  hoi_annotate_single_final.py

Use the following code for transferring the video: Change the paths accordingly

`python transfer_val_data.py`

## Instructions/ Specifications
### Single Person videos
1. The frame with action name (green), object/ object instances (blue) will be displayed.
2. Press the button `1,2,3` that corresponds to the object that belongs to the person present in the frame and the action displayed.
3. From the next frame, it will start predicting the possible pair (in yellow), press `y` if it is the correct pair and  `n` to reject it and make a new annotation.
4. Press `b` if you have to go back in frames.
5. When there are multiple instances of the same object, and all the instances belong to the person, press `a` to associate all of them to the person.




### Multi Person Videos
1. The frame with persons(red), objects(blue) will be displayed.
2. Press then number for person `1,2,3` and the object instance that belongs to the person `1,2,3`.
3. Press `b` if you have to go back in frame.


### General Instructions
1. After every video `Next` image comes. You can press `Enter` or `y` if you want to continue annotating next video. If you press any other key, it will exit the code. You can annotate later.
