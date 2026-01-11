#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# specify output directory
# ================================

import modo

from h3d_utilites.scripts.h3d_utils import get_user_value, set_user_value

from h3d_octane_automation.scripts.octane_automation import USERVAL_NAME_ANIMATION_OUTPUT_FOLDER


def main():
    openpath = get_user_value(USERVAL_NAME_ANIMATION_OUTPUT_FOLDER)
    outputpath = modo.dialogs.dirBrowse('Select Animation Output Folder', path=openpath)
    if not outputpath:
        return
    set_user_value(USERVAL_NAME_ANIMATION_OUTPUT_FOLDER, outputpath)


if __name__ == '__main__':
    main()
