import os
import sys
import logging
import multiprocessing

from pydantic import BaseModel
import cv2

from mesh_gen import *

logging.basicConfig(level=logging.INFO)
logging.getLogger("mesh_gen").setLevel(level=logging.CRITICAL)
logging.getLogger("gds_util").setLevel(level=logging.CRITICAL)

logger = logging.getLogger("main")
logger.setLevel(level=logging.INFO)


class Conf(BaseModel):
    scale: float
    checked_gray: list[int]
    period_range: list[float]
    width: float
    height: float
    output_dir: str
    multi_process: int
    
def worker(queue: multiprocessing.Queue):
    while not queue.empty():
        tar, args = queue.get()
        tar(*args)


def task(image_name, scale, checked_gray, gds_file, period_mapping, width, height):
    img = cv2.imread(image_name, cv2.IMREAD_GRAYSCALE)
    img_util = ImageUtility(imag=img, 
                            scale=scale, 
                            period_mapping=period_mapping)
    mesh_points_iter = mesh_gen_iter(img_util, batch_size=4096, checked_gray=checked_gray)

    gdslib = GdsLibrary()
    rect_name = f"rect"
    rect = gdslib.create_cell(GdsCellType.RECTANGLE, name=rect_name, width=width, height=height, layer=0)
    for xs, ys, _ in mesh_points_iter:
        if len(xs) > 0:
            gdslib.add_ref_multi_xy(rect, xs, ys)
    try:
        gdslib.dump(gds_file)
    except IOError as e:
        logging.error(f"error when saving gds files: {e}")
    
    logger.info(f"gds file has been written to `{gds_file}`")


def parse_arg_from_json(json_file: str) -> tuple[Conf, tuple[str,...]]:
    with open(json_file) as f:
        content = f.read()
    conf = Conf.model_validate_json(content)
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    image_files =  filedialog.askopenfilenames(
            title="请选择图片文件",
            initialdir=os.path.expanduser(os.path.curdir),
            filetypes=[("所有文件", "*.*")]
        )
    return conf, image_files
    
def parse_args_from_input() -> tuple[Conf, tuple[str,...]]:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_files', type=str, nargs="+", help='specify the image file(s)')
    parser.add_argument('--scale', type=float, help='specify the scale of image, unit in micrometer/pixel')
    parser.add_argument('--period_range', type=float, nargs=2, help='specify the period range, unit in micrometer')
    parser.add_argument('--width', type=float, help='specify the width of the nanobar, unit in micrometer')
    parser.add_argument('--height', type=float, help='specify the height  of the nanobar, unit in micrometer')

    parser.add_argument('--checked_gray', type=int, nargs="*", default=[], help='only specified gray scales will be checked, default is 0 to 255')
    parser.add_argument('--output_dir', type=str, default="./gds_output", help='sepcify the path to save the gds files')
    parser.add_argument('--multi_process', type=int, default=1, help='specify the number of working processes')
    
    args = parser.parse_args()
    image_files = args.__dict__.pop("image_files")
    conf = Conf.model_validate(args.__dict__)
    return conf, image_files

def gen_task(conf: Conf, image_files: list[str]) -> multiprocessing.Queue:
    scale = conf.scale
    checked_gray = conf.checked_gray if len(conf.checked_gray) > 0 else None
    period_range = conf.period_range
    output_dir = conf.output_dir
    multi_process = conf.multi_process
    width = conf.width
    height = conf.height
    
    task_queue = multiprocessing.Queue()
    for image in image_files:
        image_name_no_ext = os.path.splitext(os.path.basename(image))[0]
        gds_file_path = os.path.join(output_dir, image_name_no_ext+".gds")
        period_mapping = LinearGrayPeriodMapping(period_range[0], period_range[1])
        args = (image, scale, checked_gray, gds_file_path, period_mapping, width, height)
        task_queue.put((task, args))
    return task_queue

def main():
    if len(sys.argv) > 1:
        conf, image_files = parse_args_from_input()
    else:
        conf, image_files = parse_arg_from_json("conf.json")
        
    task_queue = gen_task(conf, image_files)
        
    if conf.multi_process <= 1:
        worker(task_queue)
    else:
        logger.info(f"working on {conf.multi_process} processor(s)")
        processes = []
        for _ in range(conf.multi_process):
            proc = multiprocessing.Process(target=worker, args=(task_queue,))
            processes.append(proc)
            proc.start()
        for proc in processes:
            proc.join()
        

if __name__ == "__main__":
    main()