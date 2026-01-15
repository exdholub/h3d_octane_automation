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

import lx
import modo

from h3d_utilites.scripts.h3d_utils import get_user_value

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
    start: int
    end: int
    working_range: int
    skip_frames: int
    frame_timeout: float
    sleep_interval: float
    output_folder: str
    filename_prefix: str


def main():
    backup_current_range = modo.Scene().currentRange
    backup_output_folder = get_kernel_output_folder()
    backup_filename_prefix = get_kernel_filename_prefix()
    backup_skip_frames = get_kernel_skip_frames()

    ui_data = get_ui_data()
    print('Render Octane Animation started with the following parameters:')
    print(f'  Start Frame: {ui_data.start}   End Frame: {ui_data.end}')
    render_animation(ui_data)
    print('Render Octane Animation finished.')

    modo.Scene().currentRange = backup_current_range
    set_kernel_output_folder(backup_output_folder)
    set_kernel_filename_prefix(backup_filename_prefix)
    set_kernel_skip_frames(backup_skip_frames)


def get_kernel_output_folder() -> str:
    lx.eval('select.itemType renderer')
    kernel_output_folder = lx.eval('item.channel oc_animationFolder ?')

    if not kernel_output_folder:
        raise ValueError('Cannot get Octane animation output folder')

    return kernel_output_folder


def get_kernel_filename_prefix() -> str:
    lx.eval('select.itemType renderer')
    kernel_filename_prefix = lx.eval('item.channel oc_animationSavePrefix ?')

    if not kernel_filename_prefix:
        raise ValueError('Cannot get Octane filename prefix')

    return kernel_filename_prefix


def get_kernel_skip_frames() -> int:
    lx.eval('select.itemType renderer')
    kernel_skip_frames = lx.eval('item.channel oc_animateSaveSkipFrames ?')

    if not kernel_skip_frames:
        raise ValueError('Cannot get Octane skip frames value')

    return kernel_skip_frames


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
        start=start,
        end=end,
        working_range=working_range,
        skip_frames=skip_frames,
        frame_timeout=frame_timeout,
        sleep_interval=sleep_interval,
        output_folder=output_folder,
        filename_prefix=filename_prefix,
        )

    return info


def set_kernel_output_folder(folder: str):
    lx.eval('select.itemType renderer')
    lx.eval(f'item.channel oc_animationFolder "{folder}"')


def set_kernel_filename_prefix(name: str):
    lx.eval('select.itemType renderer')
    lx.eval(f'item.channel oc_animationSavePrefix "{name}"')


def set_kernel_skip_frames(count: int):
    lx.eval('select.itemType renderer')
    lx.eval(f'item.channel oc_animateSaveSkipFrames "{count}"')


def render_animation(data: InitialData):
    set_kernel_output_folder(data.output_folder)
    set_kernel_filename_prefix(data.filename_prefix)
    set_kernel_skip_frames(data.skip_frames)

    brutto_start = data.start - data.skip_frames
    brutto_end = data.end + data.skip_frames

    working_range_start = brutto_start

    while working_range_start <= brutto_end:
        estimated_end = working_range_start + data.working_range - 1
        working_range_end = min(estimated_end, brutto_end)

        render_range(working_range_start, working_range_end)

        if not wait_for_status(
            frames=working_range_end - working_range_start + 1,
            ui_data=data,
            ):
            print('Rendering timeout exceeded, aborting further rendering.')
            return

        working_range_start += data.working_range


def render_range(start: int, end: int):
    modo.Scene().currentRange = (start, end)
    print(f'Rendering frames from {start} to {end}...')
    lx.eval('octane.command animate')
    print('Done.')


def wait_for_status(
        frames: int,
        ui_data: InitialData,
        status: int = STATUS_COMPLETED,
        ) -> bool:
    timer = ui_data.frame_timeout
    while timer > 0:
        current_status = lx.eval('octane.getRenderStatus ?')
        print(f'Waiting for render status {status}, current status is {current_status}...')

        # if current_status == status:
        #     print('frame fiished. frames left:', frames - 1)
        #     frames -= 1
        #     if frames <= 0:
        #         return True
        #     # reset timer for next frame
        #     timer = timeout_seconds

        print(f'Sleeping for {ui_data.sleep_interval} seconds...')
        time.sleep(ui_data.sleep_interval)
        print('Woke up.')
        timer -= ui_data.sleep_interval

    return False


if __name__ == '__main__':
    main()
