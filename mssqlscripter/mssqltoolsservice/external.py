# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import sys
import tarfile
import zipfile

import utility

SQLTOOLSSERVICE_BASE = os.path.join(utility.ROOT_DIR, "sqltoolsservice/")

# Supported platform key's must match those in mssqlscript's setup.py.
SUPPORTED_PLATFORMS = {
    "manylinux1_x86_64": SQLTOOLSSERVICE_BASE
    + "manylinux1/"
    + "Microsoft.SqlTools.ServiceLayer-linux-x64-netcoreapp2.1.tar.gz",
    "macosx_10_11_intel": SQLTOOLSSERVICE_BASE
    + "macosx_10_11_intel/"
    + "Microsoft.SqlTools.ServiceLayer-osx-x64-netcoreapp2.1.tar.gz",
    "win_amd64": SQLTOOLSSERVICE_BASE
    + "win_amd64/"
    + "Microsoft.SqlTools.ServiceLayer-win-x64-netcoreapp2.1.zip",
    "win32": SQLTOOLSSERVICE_BASE
    + "win32/"
    + "Microsoft.SqlTools.ServiceLayer-win-x86-netcoreapp2.1.zip",
}

TARGET_DIRECTORY = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "bin"))


def copy_sqltoolsservice(platform):
    """
    For each supported platform, build a universal wheel.
    """
    # Clean up dangling directories if previous run was interrupted.
    utility.clean_up(directory=TARGET_DIRECTORY)

    if not platform or platform not in SUPPORTED_PLATFORMS:
        print(f"{platform} is not supported.")
        print(
            (
                "Please provide a valid platform flag."
                + "[win32, win_amd64, manylinux1_x86_64, macosx_10_11_intel]"
            )
        )
        sys.exit(1)

    copy_file_path = SUPPORTED_PLATFORMS[platform]

    print((f"Sqltoolsservice archive found at {copy_file_path}"))
    if copy_file_path.endswith("tar.gz"):
        compressed_file = tarfile.open(name=copy_file_path, mode="r:gz")
    elif copy_file_path.endswith(".zip"):
        compressed_file = zipfile.ZipFile(copy_file_path)

    if not os.path.exists(TARGET_DIRECTORY):
        os.makedirs(TARGET_DIRECTORY)

    print(f"Bin placing sqltoolsservice for this platform: {platform}.")
    print(f"Extracting files from {copy_file_path}")
    compressed_file.extractall(TARGET_DIRECTORY)


def clean_up_sqltoolsservice():
    utility.clean_up(directory=TARGET_DIRECTORY)
