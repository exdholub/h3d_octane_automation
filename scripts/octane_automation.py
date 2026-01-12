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

import lx
import modo

from h3d_utilites.scripts.h3d_utils import get_user_value, set_user_value

USERVAL_NAME_CURRENT_START = 'h3d_oa_start_frame'
USERVAL_NAME_CURRENT_END = 'h3d_oa_end_frame'
USERVAL_NAME_WORKING_RANGE = 'h3d_oa_working_range'
USERVAL_NAME_ANIMATION_OUTPUT_FOLDER = 'h3d_oa_animation_output_folder'
USERVAL_NAME_FILENAME_PREFIX = 'h3d_oa_save_filename_prefix'


@dataclass
class InitialData:
    fps: float
    start: int
    end: int
    working_range: int
    output_folder: str
    filename_prefix: str


def main():
    backup_output_folder = get_kernel_output_folder()
    backup_filename_prefix = get_kernel_filename_prefix()

    initial_data: InitialData = get_initial_data()
    print(initial_data)

    set_kernel_output_folder(backup_output_folder)
    set_kernel_filename_prefix(backup_filename_prefix)


def get_initial_data() -> InitialData:

    fps = modo.Scene().fps
    start = get_user_value(USERVAL_NAME_CURRENT_START)
    end = get_user_value(USERVAL_NAME_CURRENT_END)
    working_range = get_user_value(USERVAL_NAME_WORKING_RANGE)
    output_folder = get_user_value(USERVAL_NAME_ANIMATION_OUTPUT_FOLDER)
    filename_prefix = get_user_value(USERVAL_NAME_FILENAME_PREFIX)


    info = InitialData(
        fps=fps,
        start=start,
        end=end,
        working_range=working_range,
        output_folder=output_folder,
        filename_prefix=filename_prefix,
        )

    return info


def get_kernel_output_folder() -> str:
    lx.eval('select.itemType renderer')
    kernel_output_folder = lx.eval('item.channel oc_animationFolder ?')

    return kernel_output_folder


def set_kernel_output_folder(folder: str):
    lx.eval('select.itemType renderer')
    lx.eval(f'item.channel oc_animationFolder {folder}')


def get_kernel_filename_prefix() -> str:
    lx.eval('select.itemType renderer')
    kernel_filename_prefix = lx.eval('item.channel item.channel oc_animationSavePrefix ?')

    return kernel_filename_prefix


def set_kernel_filename_prefix(name: str):
    lx.eval('select.itemType renderer')
    lx.eval(f'item.channel item.channel oc_animationSavePrefix {name}')


if __name__ == '__main__':
    main()
