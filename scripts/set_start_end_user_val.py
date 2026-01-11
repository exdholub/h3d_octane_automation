#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# get current start and end frames from scene and set user values for it
# ================================

import modo

from h3d_utilites.scripts.h3d_utils import set_user_value

from h3d_octane_automation.scripts.octane_automation import USERVAL_NAME_CURRENT_START, USERVAL_NAME_CURRENT_END


def main():
    start, end = modo.Scene().currentRange

    set_user_value(USERVAL_NAME_CURRENT_START, start)
    set_user_value(USERVAL_NAME_CURRENT_END, end)


if __name__ == '__main__':
    main()
