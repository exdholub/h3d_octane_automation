#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# Octane. Render the animation range, dividing it into fragments to optimize Octane motion blur
# ================================

from dataclasses import dataclass

import time
from pathlib import Path
import asyncio

import lx
import modo

from h3d_utilites.scripts.h3d_utils import get_user_value

from h3d_utilites.scripts.h3d_debug import h3dd, prints, fn_in, fn_out

USERVAL_NAME_CURRENT_START = 'h3d_oa_start_frame'
USERVAL_NAME_CURRENT_END = 'h3d_oa_end_frame'
USERVAL_NAME_WORKING_RANGE = 'h3d_oa_working_range'
USERVAL_NAME_SKIP_FRAMES = 'h3d_oa_skip_frames'
USERVAL_NAME_FRAME_TIMEOUT = 'h3d_oa_frame_timeout'
USERVAL_NAME_SLEEP_INTERVAL = 'h3d_oa_sleep_interval'
USERVAL_NAME_ANIMATION_OUTPUT_FOLDER = 'h3d_oa_animation_output_folder'
USERVAL_NAME_FILENAME_PREFIX = 'h3d_oa_save_filename_prefix'

STATUS_COMPLETED = 4


@dataclass
class InitialData:
    fps: float
    frame_start: int
    frame_end: int
    motion_blur_range: int
    skip_frames: int
    frame_timeout: float
    sleep_interval: float
    output_folder: str
    filename_prefix: str
    render_start_time: float


def main():
    backup_current_range = get_scene_range()
    prints(f'backup_current_range: {backup_current_range}')

    backup_output_folder = get_kernel_output_folder()
    prints(f'backup_output_folder: {backup_output_folder}')

    backup_filename_prefix = get_kernel_filename_prefix()
    prints(f'backup_filename_prefix: {backup_filename_prefix}')

    backup_skip_frames = get_kernel_skip_frames()
    prints(f'backup_skip_frames: {backup_skip_frames}')

    ui_data = get_ui_data()
    set_scene_range((ui_data.frame_start, ui_data.frame_end))
    set_kernel_output_folder(ui_data.output_folder)
    set_kernel_filename_prefix(ui_data.filename_prefix)
    set_kernel_skip_frames(ui_data.skip_frames)

    prints('Render Octane Animation started with the following parameters:')
    prints(f'  Start Frame: {ui_data.frame_start}   End Frame: {ui_data.frame_end}')
    prints(f'  output_folder: {ui_data.output_folder}')
    prints(f'  filename_prefix: {ui_data.filename_prefix}')
    prints(f'  skip_frames: {ui_data.skip_frames}')
    prints(f'  frame_timeout: {ui_data.frame_timeout}')
    prints(f'  sleep_interval: {ui_data.sleep_interval}')

    if not is_folder_writable(ui_data.output_folder, ui_data.filename_prefix):
        prints('Output folder is not writable, aborting rendering.')
        modo.dialogs.alert(
            title='Output Folder Error',
            message='Failed to write to the output folder. Please check the folder path and permissions.',
            dtype='error',
        )
        return
    prints('Output folder is writable.')

    render_animation(ui_data)

    # set_scene_range(backup_current_range)
    # set_kernel_output_folder(backup_output_folder)
    # set_kernel_filename_prefix(backup_filename_prefix)
    # set_kernel_skip_frames(backup_skip_frames)


def get_kernel_output_folder() -> str:
    lx.eval('select.itemType renderer')
    kernel_output_folder = lx.eval('item.channel oc_animationFolder ?')

    if kernel_output_folder is None:
        raise ValueError('Cannot get Octane animation output folder')

    return kernel_output_folder


def set_kernel_output_folder(folder: str):
    # lx.eval('layout.createOrClose octaneAnimationLayoutCookie octaneAnimationLayout title:"OctaneRender Animation" width:300 height:70 persistent:false style:standard')
    lx.eval('select.itemType renderer')
    lx.eval(f'item.channel oc_animationFolder "{folder}"')


def get_kernel_filename_prefix() -> str:
    lx.eval('select.itemType renderer')
    kernel_filename_prefix = lx.eval('item.channel oc_animationSavePrefix ?')

    if kernel_filename_prefix is None:
        raise ValueError('Cannot get Octane filename prefix')

    return kernel_filename_prefix


def set_kernel_filename_prefix(name: str):
    lx.eval('select.itemType renderer')
    lx.eval(f'item.channel oc_animationSavePrefix "{name}"')


def get_kernel_skip_frames() -> int:
    lx.eval('select.itemType renderer')
    kernel_skip_frames = lx.eval('item.channel oc_animateSaveSkipFrames ?')

    if kernel_skip_frames is None:
        raise ValueError('Cannot get Octane skip frames value')

    return kernel_skip_frames


def set_kernel_skip_frames(count: int):
    lx.eval('select.itemType renderer')
    lx.eval(f'item.channel oc_animateSaveSkipFrames "{count}"')


def get_ui_data() -> InitialData:
    fps = modo.Scene().fps
    if not fps:
        raise ValueError('Cannot get scene FPS')
    start = get_user_value(USERVAL_NAME_CURRENT_START)
    end = get_user_value(USERVAL_NAME_CURRENT_END)
    working_range = get_user_value(USERVAL_NAME_WORKING_RANGE)
    skip_frames = get_user_value(USERVAL_NAME_SKIP_FRAMES)
    frame_timeout = get_user_value(USERVAL_NAME_FRAME_TIMEOUT)
    sleep_interval = get_user_value(USERVAL_NAME_SLEEP_INTERVAL)
    output_folder = get_user_value(USERVAL_NAME_ANIMATION_OUTPUT_FOLDER)
    filename_prefix = get_user_value(USERVAL_NAME_FILENAME_PREFIX)


    info = InitialData(
        fps=fps,
        frame_start=start,
        frame_end=end,
        motion_blur_range=working_range,
        skip_frames=skip_frames,
        frame_timeout=frame_timeout,
        sleep_interval=sleep_interval,
        output_folder=output_folder,
        filename_prefix=filename_prefix,
        render_start_time=time.time(),
        )

    return info


def get_scene_range() -> tuple[int, int]:
    current_range = modo.Scene().currentRange
    if current_range is None:
        raise ValueError('Cannot get scene range')
    return current_range


def set_scene_range(frame_range: tuple[int, int]):
    modo.Scene().currentRange = (frame_range)


def is_folder_writable(folder: str, filename: str) -> bool:
    test_file = Path(folder) / f'{filename}.tmp'
    try:
        with open(test_file, 'w') as f:
            f.write('test')

        # Remove the test file
        test_file.unlink()
        return True

    except IOError as e:
        prints(f'Folder "{folder}" is not writable: {e}')
        return False


def render_animation(data: InitialData):
    fn_in()
    brutto_start = data.frame_start - data.skip_frames
    brutto_end = data.frame_end + data.skip_frames

    working_range_start = brutto_start

    prints(f'Starting animation render:')
    prints(f'brutto_start: {brutto_start}')
    prints(f'brutto_end: {brutto_end}')

    while working_range_start <= brutto_end:
        estimated_end = working_range_start + data.motion_blur_range - 1
        prints(f'Estimated range end: {estimated_end}')
        working_range_end = min(estimated_end, brutto_end)
        prints(f'Working range end (max of brutto_end and estimated_end): {working_range_end}')

        prints(f'Processing frames {working_range_start} to {working_range_end}...')
        asyncio.run(render_range((working_range_start, working_range_end)))

        if not asyncio.run(await_render_finish(data=data, frame=working_range_end-data.skip_frames)):
            prints('Rendering timeout exceeded, aborting further rendering.')
            fn_out()
            return

        working_range_start += data.motion_blur_range

    fn_out()


async def render_range(range: tuple[int, int]):
    fn_in()
    modo.Scene().currentRange = range
    prints(f'render_range(): [{range[0]}..{range[1]}]')
    lx.eval('octane.command animate')
    fn_out()


async def await_render_finish(data: InitialData, frame: int) -> bool:
    fn_in()
    filename_template = f'{data.filename_prefix}_{frame:05d}'
    prints(f'Checking if frame {frame} is rendered with filename template: {filename_template}')
    working_range_timout = data.frame_timeout * data.motion_blur_range
    working_range_render_start_time = time.time()
    while not is_frame_rendered(data.output_folder, filename_template, data.render_start_time):
        elapsed_time = time.time() - working_range_render_start_time
        prints(f'Elapsed time: {elapsed_time:.2f} seconds')
        if elapsed_time > working_range_timout:
            prints(f'Working range render timeout of {working_range_timout} seconds exceeded.')
            fn_out()
            return False
        prints(f'Frame not rendered yet, sleeping for {data.sleep_interval} seconds...')
        await asyncio.sleep(data.sleep_interval)

    # TODO check render status (?)
    fn_out()
    return True


def is_frame_rendered(directory: str, template: str, threshold_time: float) -> bool:
    fn_in()
    files = Path(directory).glob(f'{template}.*')
    prints(directory, label='directory')
    prints(template, label='template')
    prints(list(files), label='files')
    for file in files:
        if file.is_file() and is_file_recent(file, threshold_time):
            prints(f'Found rendered file: {file}')
            if is_file_recent(file, threshold_time):
                prints(f'File {file} is recent enough to be considered rendered.')
                fn_out()
                return True
            else:
                prints(f'File {file} is not recent enough, ignoring.')

    prints('No matching rendered files found.')
    fn_out()
    return False


def is_file_recent(path: Path, threshold_time: float) -> bool:
    fn_in()
    if not path.exists() or not path.is_file():
        fn_out('File does not exist or is not a file.')
        return False
    file_mod_time = path.stat().st_mtime
    prints(f'File modification time: {file_mod_time}, Threshold time: {threshold_time}')
    is_recent = file_mod_time >= threshold_time
    prints(f'Is file recent? {is_recent}')
    fn_out()
    return is_recent


if __name__ == '__main__':
    h3dd.enable_debug_output()
    main()
