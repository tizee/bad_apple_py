# bad apple ASCII

The size of original video I used is 480x360.

How it works:

1. Use OpenCV or similar tool to convert video into ASCII characters according to the RGB channel, of which value is between 0 and 255.
2. Print frame by frame in the screen using terminal library like `ncurses` or print with control sequences manually
