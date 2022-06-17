#!/usr/bin/env python


# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import platform

import mssqlscripter.mssqltoolsservice.external as mssqltoolsservice
import utility

print("Running dev setup...")
print(f"Root directory '{utility.ROOT_DIR}'\n")

# install general requirements.
utility.exec_command("pip install -r dev_requirements.txt", utility.ROOT_DIR)
run_time_id = utility.get_current_platform()

if run_time_id:
    mssqltoolsservice.copy_sqltoolsservice(run_time_id)
else:
    print("This platform does not support mssqltoolsservice.")


print("Finished dev setup.")
