#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# get Animation Output Folder from Octane Kernel and set corresponding user value
# ================================

import lx

from h3d_utilites.scripts.h3d_utils import set_user_value

from h3d_octane_automation.scripts.octane_automation import USERVAL_NAME_ANIMATION_OUTPUT_FOLDER


def main():
    output_folder = lx.eval()
    set_user_value(USERVAL_NAME_ANIMATION_OUTPUT_FOLDER, output_folder)


if __name__ == '__main__':
    main()
