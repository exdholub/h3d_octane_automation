#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# set Save Filename Prefix user value to Octane Kernel Save Filename Prefix
# ================================

from h3d_utilites.scripts.h3d_utils import get_user_value

from h3d_octane_automation.scripts.octane_automation import (
    USERVAL_NAME_FILENAME_PREFIX,
    set_kernel_filename_prefix,
    )


def main():
    filename_prefix = get_user_value(USERVAL_NAME_FILENAME_PREFIX)
    if filename_prefix is not None:
        set_kernel_filename_prefix(filename_prefix)


if __name__ == "__main__":
    main()
