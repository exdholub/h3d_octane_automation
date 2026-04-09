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
from pathlib import Path
import time
import json

import lx
import modo

from h3d_utilites.scripts.h3d_utils import get_user_value

USERVAL_NAME_CURRENT_START = 'h3d_oa_start_frame'
USERVAL_NAME_CURRENT_END = 'h3d_oa_end_frame'
USERVAL_NAME_MOTION_BLUR_FRAMES = 'h3d_oa_motion_blur_frames'
USERVAL_NAME_SKIP_FRAMES = 'h3d_oa_skip_frames'
USERVAL_NAME_FRAME_TIMEOUT = 'h3d_oa_frame_timeout'
USERVAL_NAME_SLEEP_INTERVAL = 'h3d_oa_sleep_interval'
USERVAL_NAME_ANIMATION_OUTPUT_FOLDER = 'h3d_oa_animation_output_folder'
USERVAL_NAME_FILENAME_PREFIX = 'h3d_oa_save_filename_prefix'

PATH_SUFFIX_PROGRESS = '_progress.json'


@dataclass
class KernelSettings:
    frame_start: int
    frame_end: int
    skip_frames: int
    output_folder: str
    filename_prefix: str


@dataclass
class Settings:
    ui: KernelSettings
    backup: KernelSettings
    motion_blur_frames: int
    frame_timeout: float
    sleep_interval: float
    render_start_time: float


def main():
    settings = get_settings()

    if not is_folder_writable(settings.ui.output_folder, settings.ui.filename_prefix):
        modo.dialogs.alert(
            title='Output Folder Error',
            message='Failed to write to the output folder. Please check the folder path and permissions.',
            dtype='error',
        )
        return

    path_prefix = Path(settings.ui.output_folder) / f'{settings.ui.filename_prefix}'

    settings_backup = get_kernel_settings()
    save_settings(settings_backup, f'{path_prefix}{PATH_SUFFIX_BACKUP}')

    set_kernel_settings(settings)

    finished = render_animation(settings)

    if finished:
        set_kernel_settings(settings_backup)


def save_settings(settings: Settings, path: str):
    with open(path, 'w') as f:
        json.dump(settings.__dict__, f)


def load_settings(path: str) -> Settings:
    with open(path, 'r') as f:
        data = json.load(f)
        settings = Settings(**data)
        return settings


def get_kernel_output_folder() -> str:
    lx.eval('select.itemType renderer')
    kernel_output_folder = lx.eval('item.channel oc_animationFolder ?')

    if kernel_output_folder is None:
        raise ValueError('Cannot get Octane animation output folder')

    return kernel_output_folder


def set_kernel_output_folder(folder: str):
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


def get_kernel_settings() -> Settings:
    settings = Settings(
        frame_start = get_scene_range()[0],
        frame_end = get_scene_range()[1],
        skip_frames = get_kernel_skip_frames(),
        output_folder = get_kernel_output_folder(),
        filename_prefix = get_kernel_filename_prefix(),
        motion_blur_frames = get_user_value(USERVAL_NAME_MOTION_BLUR_FRAMES),
        frame_timeout = get_user_value(USERVAL_NAME_FRAME_TIMEOUT),
        sleep_interval = get_user_value(USERVAL_NAME_SLEEP_INTERVAL),
        render_start_time = time.time(),
    )

    return settings


def set_kernel_settings(settings: Settings):
    set_scene_range((settings.frame_start, settings.frame_end))
    set_kernel_output_folder(settings.output_folder)
    set_kernel_filename_prefix(settings.filename_prefix)
    set_kernel_skip_frames(settings.skip_frames)


def get_settings() -> Settings:
    ui = Settings(
        frame_start = get_user_value(USERVAL_NAME_CURRENT_START),
        frame_end = get_user_value(USERVAL_NAME_CURRENT_END),
        motion_blur_frames = get_user_value(USERVAL_NAME_MOTION_BLUR_FRAMES),
        skip_frames = get_user_value(USERVAL_NAME_SKIP_FRAMES),
        frame_timeout = get_user_value(USERVAL_NAME_FRAME_TIMEOUT),
        sleep_interval = get_user_value(USERVAL_NAME_SLEEP_INTERVAL),
        output_folder = get_user_value(USERVAL_NAME_ANIMATION_OUTPUT_FOLDER),
        filename_prefix = get_user_value(USERVAL_NAME_FILENAME_PREFIX),
        render_start_time = time.time(),
    )

    return ui


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
        return False


def render_animation(settings: Settings):
    brutto_start = settings.frame_start - settings.skip_frames
    brutto_end = settings.frame_end + settings.skip_frames

    working_range_start = brutto_start

    while working_range_start <= brutto_end:
        estimated_end = working_range_start + settings.motion_blur_frames - 1
        working_range_end = min(estimated_end, brutto_end)

        render_range((working_range_start, working_range_end))

        if not await_render_finish(settings=settings, frame=working_range_end-settings.skip_frames):
            return

        working_range_start += settings.motion_blur_frames


def render_range(range: tuple[int, int]):
    modo.Scene().currentRange = range
    lx.eval('octane.command animate')


def await_render_finish(settings: Settings, frame: int) -> bool:
    filename_template = f'{settings.filename_prefix}_{frame:05d}'
    working_range_timout = settings.frame_timeout * settings.motion_blur_frames
    working_range_render_start_time = time.time()
    while not is_frame_rendered(settings.output_folder, filename_template, settings.render_start_time):
        elapsed_time = time.time() - working_range_render_start_time
        if elapsed_time > working_range_timout:
            return False
        time.sleep(settings.sleep_interval)

    return True


def is_frame_rendered(directory: str, template: str, threshold_time: float) -> bool:
    files = Path(directory).glob(f'{template}.*')
    for file in files:
        if file.is_file() and is_file_recent(file, threshold_time):
            if is_file_recent(file, threshold_time):
                return True

    return False


def is_file_recent(path: Path, threshold_time: float) -> bool:
    if not path.exists() or not path.is_file():
        return False
    file_mod_time = path.stat().st_mtime
    is_recent = file_mod_time >= threshold_time
    return is_recent


if __name__ == '__main__':
    # h3dd.enable_debug_output()
    main()
