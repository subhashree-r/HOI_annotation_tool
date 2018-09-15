% parse video frames
clear all;
clc;

% read video
addpath('/home/subha/hoi_vid/mmread/');
viddataset = '/home/subha/hoi_vid/CharadesDet/Charades_v1_480/';
imgdataset = '/home/subha/hoi_vid/CharadesDet/val_videos_images_downscaled_new/';
if ~exist(imgdataset,'dir')
    mkdir(imgdataset);
end

file = dir(viddataset);

for i = 1:9848
    vidname = file(i+3).name;
    vidname = vidname(1:end-4);
    vidpath = [viddataset,vidname,'.mp4'];
    disp(vidpath)
    readerobj = mmread(vidpath, [], [], false, true);
    start_frame = 1;
    [~, maxframe] = size(readerobj.frames(start_frame:end));
    vidFrames   = readerobj.frames(start_frame:end);
    impath = [imgdataset,vidname];
    if ~exist(impath,'dir')
        mkdir(impath);

    for im_id = 1:maxframe
        im = vidFrames(im_id).cdata;
        im_name = [num2str(im_id),'.jpg'];
        imwrite(im,[impath,'/',im_name],'jpg');
    end
    end
    i

end
