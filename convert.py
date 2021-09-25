import cv2 as cv
import sys
import pprint

FRAME_WIDTH=int(480/4)
FRAME_HEIGHT=int(360/8)
# sort by gray value in descending order
rgb_ascii= list("BADAPPLEISAWESOME(;)VV(;)--^         ")
rgb_len=len(rgb_ascii)

def frames_to_python(frames):
    with open("frames_data.py","w") as f:
        f.write("frames_data = " + pprint.pformat(frames))

def frames_to_c(frames):
    with open("data.c","w+") as f:
        for idx,frame in enumerate(frames):
            f.write("char *frame%d[]= { \n" % idx)
            for line in frame:
                f.write("\" %s \",\n" % line)
            f.write("};\n")


def mp4_to_frames(video_path):
    vc = cv.VideoCapture(video_path)
    frames = []
    total = vc.get(int(cv.CAP_PROP_FRAME_COUNT))
    count = 0
    while True:
        # use first 100 frames for demonstration
        if count == 100:
            break
        f, frame = vc.read()
        if frame is None:
            break
        count += 1
        print("\rcurrent frame: %d / %d" % (count, total),end="")
        frame_ascii =  frame_to_ascii(frame)
        frames.append(frame_ascii)
    vc.release()
    return frames

def frame_to_ascii(frame):
    height, width, _ = frame.shape
    rgb = 0.5 * frame[:, :, 2] + 0.2 * frame[:, :, 1] + 0.3 * frame[:, :, 0]
    res = []
    # sampling
    for i in range(FRAME_HEIGHT):
        y = int(i * height/FRAME_HEIGHT)
        text = ""
        for j in range(FRAME_WIDTH):
            x = int(j * width/FRAME_WIDTH)
            text += rgb_ascii[int(rgb[y][x]/256 * rgb_len)]
        res.append(text)
    return res

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise ValueError('Please provide video path')
    path = sys.argv[1]
    print(f"convert video {path}")
    frames = mp4_to_frames(path)
    if sys.argv[2] == 'c':
        frames_to_c(frames)
    else:
        frames_to_python(frames)
