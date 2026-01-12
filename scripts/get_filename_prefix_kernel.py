#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# get Save Filename Prefix from Octane Kernel and set corresponding user value
# ================================

from h3d_utilites.scripts.h3d_utils import set_user_value

from h3d_octane_automation.scripts.octane_automation import (
    USERVAL_NAME_FILENAME_PREFIX,
    get_kernel_filename_prefix,
    )


def main():
    filename_prefix = get_kernel_filename_prefix()
    set_user_value(USERVAL_NAME_FILENAME_PREFIX, filename_prefix)


if __name__ == '__main__':
    main()
