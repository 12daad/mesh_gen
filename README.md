
# requirement
- platform: Windows
- python version >= 3.14
- python dependencies
```
pip install -r requirements.txt
```


# quick start
- start without specifying args, this startup method uses configure from `conf.json` file
```
python main.py
```

- start with certain args, e.g.
```
python main.py  --image_files "images\TaiChi_HighRes copy 1.bmp" --scale 0.5 --period_range 0.3 0.6 --width 0.1 --height 0.02
```
using `python main.py -h` for more help

# conf.json example
a valid `conf.json` file
```json
{
"scale": 0.6, // specify the scale of image, unit in micrometer/pixel 
"checked_gray": [],  // only specified gray scales will be checked, default is 0 to 255 (256 points totally)
"period_range": [0.3, 0.6], // specify the period range, unit in micrometer, note that the gray scale to period mapping is required to be linear
"width": 0.1, // specify the width of the nanobar, unit in micrometer
"height": 0.02, // specify the height of the nanobar, unit in micrometer
"output_dir": "./gds_output", //sepcify the path to save the gds files
"multi_process": 1 // specify the number of working processes
}
```

