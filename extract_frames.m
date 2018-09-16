% parse video frames
clear all;
clc;

% read video
addpath('mmread/');
viddataset = '/media/cooper/Data/hoi_data_labelling/CharadesDet/focus_videos_multiperson/';
imgdataset = '/media/cooper/Data/hoi_data_labelling/CharadesDet/val_videos_images_downscaled_new/';

if ~exist(imgdataset,'dir')
    mkdir(imgdataset);
end

file = dir(viddataset);
A = size(file);
for i = 1:A(1)
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
 

end
