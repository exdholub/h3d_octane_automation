#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# set Animation Output Folder user value to Octane Kernel Animation Output Folder
# ================================

from h3d_utilites.scripts.h3d_utils import get_user_value

from h3d_octane_automation.scripts.octane_automation import (
    USERVAL_NAME_ANIMATION_OUTPUT_FOLDER,
    set_kernel_output_folder
    )


def main():
    output_folder = get_user_value(USERVAL_NAME_ANIMATION_OUTPUT_FOLDER)
    if output_folder is not None:
        set_kernel_output_folder(output_folder)


if __name__ == "__main__":
    main()
