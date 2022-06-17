# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys


def handle_response(response, display=False):
    """
    Dispatch response based on scripting response or event.
    """

    def handle_script_response(response, display=False):
        if display:
            sys.stderr.write(
                f"Scripting request submitted with request id: {response.operation_id}\n"
            )

    def handle_script_plan_notification(response, display=False):
        if display:
            sys.stderr.write(
                f"Scripting request: {response.operation_id} plan: {response.count} database objects\n"
            )

    def handle_script_progress_notification(response, display=False):
        if display:
            sys.stderr.write(
                f"Scripting progress: Status: {response.status} Progress: {response.completed_count} out of {response.total_count} objects scripted\n"
            )

    def handle_script_complete(response, display=False):
        if response.has_error:
            # Always display error messages.
            sys.stdout.write(
                f"Scripting request: {response.operation_id} encountered error: {response.error_message}\n"
            )
            sys.stdout.write(f"Error details: {response.error_details}\n")
        elif display:
            sys.stderr.write(f"Scripting request: {response.operation_id} completed\n")

    response_handlers = {
        "ScriptResponse": handle_script_response,
        "ScriptPlanNotificationEvent": handle_script_plan_notification,
        "ScriptProgressNotificationEvent": handle_script_progress_notification,
        "ScriptCompleteEvent": handle_script_complete,
    }

    response_name = type(response).__name__

    if response_name in response_handlers:
        return response_handlers[response_name](response, display)
