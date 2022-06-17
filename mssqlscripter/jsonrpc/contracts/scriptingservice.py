# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import logging

from mssqlscripter.jsonrpc.contracts import Request

logger = logging.getLogger("mssqlscripter.jsonrpc.contracts.scriptingservice")


class ScriptingRequest(Request):
    """
    SqlTools Service scripting service scripting request.
    """

    METHOD_NAME = "scripting/script"

    def __init__(self, id, json_rpc_client, parameters):
        """
        Create a scripting request command.
        """
        assert id != 0
        self.id = id
        self.finished = False
        self.json_rpc_client = json_rpc_client
        self.params = ScriptingParams(parameters)
        self.decoder = ScriptingResponseDecoder()

    def execute(self):
        """
        submit scripting request to sql tools service.
        """
        logger.info(
            f"Submitting scripting request id: {self.id} with targetfile: {self.params.file_path}"
        )

        scrubbed_parameters = copy.deepcopy(self.params)
        scrubbed_parameters.connection_string = "*********"
        logger.debug(scrubbed_parameters.format())
        self.json_rpc_client.submit_request(
            self.METHOD_NAME, self.params.format(), self.id
        )

    def get_response(self):
        """
        Get latest response, event or exception if it occured.
        """
        try:
            response = self.json_rpc_client.get_response(self.id)
            decoded_response = None

            if response:
                logger.debug(response)
                # Decode response to either response or event type.
                decoded_response = self.decoder.decode_response(response)

                logger.debug(f"Scripting request received response: {decoded_response}")
                if isinstance(decoded_response, ScriptCompleteEvent):
                    self.finished = True
                    self.json_rpc_client.request_finished(self.id)

            return decoded_response

        except Exception as error:
            # Return a scripting error event.
            self.finished = True
            self.json_rpc_client.request_finished(self.id)
            logger.debug(f"Scripting request received exception: {str(error)}")
            exception = {
                "operationId": self.id,
                "sequenceNumber": None,
                "success": False,
                "canceled": False,
                "hasError": True,
                "errorMessage": "Scripting request encountered a exception",
                "errorDetails": error.args,
            }

            return ScriptCompleteEvent(exception)

    def completed(self):
        """
        Get current request state.
        """
        return self.finished


class ScriptingParams(object):
    """
    Scripting request parameters.
    """

    def __init__(self, parameters):
        self.file_path = parameters["FilePath"]
        self.connection_string = parameters["ConnectionString"]
        self.script_destination = parameters["ScriptDestination"]
        self.scripting_options = ScriptingOptions(parameters)

        self.include_schema = (
            parameters["IncludeSchemas"] if "IncludeSchemas" in parameters else None
        )
        self.exclude_schema = (
            parameters["ExcludeSchemas"] if "ExcludeSchemas" in parameters else None
        )
        self.include_type = (
            parameters["IncludeTypes"] if "IncludeTypes" in parameters else None
        )
        self.exclude_type = (
            parameters["ExcludeTypes"] if "ExcludeTypes" in parameters else None
        )

        # List of scripting objects.
        self.include_objects = ScriptingObjects(
            parameters["IncludeObjects"] if "IncludeObjects" in parameters else None
        )
        self.exclude_objects = ScriptingObjects(
            parameters["ExcludeObjects"] if "ExcludeObjects" in parameters else None
        )

    def format(self):
        """
        Format paramaters into a dictionary.
        """
        return {
            "FilePath": self.file_path,
            "ConnectionString": self.connection_string,
            "IncludeObjectCriteria": self.include_objects.format(),
            "ExcludeObjectCriteria": self.exclude_objects.format(),
            "IncludeSchemas": self.include_schema,
            "ExcludeSchemas": self.exclude_schema,
            "IncludeTypes": self.include_type,
            "ExcludeTypes": self.exclude_type,
            "ScriptOptions": self.scripting_options.get_options(),
            "ScriptDestination": self.script_destination,
        }


class ScriptingObjects(object):
    """
    Represent a database object via it's type, schema, and name.
    """

    def __init__(self, scripting_objects):
        self.list_of_objects = []
        if scripting_objects:
            for item in scripting_objects:
                index = item.find(".")
                if index > 0:
                    schema = item[0:index]
                    name = item[index + 1 :]
                else:
                    schema = None
                    name = item
                self.add_scripting_object(schema=schema, name=name)

    def add_scripting_object(self, script_type=None, schema=None, name=None):
        """
        Serialize scripting object into a JSON Scripting object.
        """
        object_dict = {"Type": script_type, "Schema": schema, "Name": name}

        self.list_of_objects.append(object_dict)

    def format(self):
        return self.list_of_objects


class ScriptingOptions(object):
    """
    Advanced scripting options.
    """

    scripting_option_map = {
        "TypeOfDataToScript": ["SchemaAndData", "DataOnly", "SchemaOnly"],
        "ScriptCreateDrop": ["ScriptCreate", "ScriptDrop", "ScriptCreateDrop"],
        "TargetDatabaseEngineType": ["SingleInstance", "SqlAzure"],
        "ScriptStatistics": ["ScriptStatsAll", "ScriptStatsNone", "ScriptStatsDll"],
        "ScriptCompatibilityOption": [
            "Script90Compat",
            "Script100Compat",
            "Script105Compat",
            "Script110Compat",
            "Script120Compat",
            "Script130Compat",
            "Script140Compat",
        ],
        "TargetDatabaseEngineEdition": [
            "SqlServerStandardEdition",
            "SqlServerPersonalEdition",
            "SqlServerExpressEdition",
            "SqlServerEnterpriseEdition",
            "SqlServerStretchDatabaseEdition",
            "SqlAzureDatabaseEdition",
            "SqlDatawarehouseEdition",
        ],
    }

    def __init__(self, parameters=None):
        """
        Create default or non default scripting options based on parameters.
        """
        # General Default scripting options.
        self.ScriptAnsiPadding = False
        self.AppendToFile = False
        self.IncludeIfNotExists = False
        self.ContinueScriptingOnError = False
        self.ConvertUDDTToBaseType = False
        self.GenerateScriptForDependentObjects = False
        self.IncludeDescriptiveHeaders = False
        self.IncludeSystemConstraintNames = False
        self.IncludeUnsupportedStatements = False
        self.SchemaQualify = False
        self.Bindings = False
        self.Collation = False
        self.Default = False
        self.ScriptExtendedProperties = False
        self.ScriptLogins = False
        self.ScriptObjectLevelPermissions = False
        self.ScriptOwner = False
        self.ScriptUseDatabase = False

        # Default Table/View options.
        self.ScriptChangeTracking = False
        self.ScriptCheckConstraints = False
        self.ScriptDataCompressionOptions = False
        self.ScriptForeignKeys = False
        self.ScriptFullTextIndexes = False
        self.ScriptIndexes = False
        self.ScriptPrimaryKeys = False
        self.ScriptTriggers = False
        self.UniqueKeys = False

        # Scripting options that are limited.
        self.TypeOfDataToScript = "SchemaOnly"
        self.ScriptCreateDrop = "ScriptCreate"
        self.TargetDatabaseEngineType = "SingleInstance"
        self.ScriptStatistics = "ScriptStatsNone"
        self.ScriptCompatibilityOption = "Script140Compat"
        self.TargetDatabaseEngineEdition = "SqlServerStandardEdition"

        if parameters:
            self.update_options(parameters)

    def update_options(self, parameters):
        """
        Update default options to passed in options.
        """
        default_options = vars(self)
        for option, value in list(parameters.items()):
            if option in default_options:
                if option in self.scripting_option_map:
                    if value not in self.scripting_option_map[option]:
                        raise ValueError(f"Option: {option} has invalid value: {value}")
                elif not isinstance(value, bool):
                    raise ValueError(
                        f'Option: {option} has unexpected value type" {value}'
                    )
                # set the value if we pass all the checks.
                default_options[option] = value

    def get_options(self):
        """
        Return a dictionary of all options
        """
        return vars(self)


#
#   Various Scripting Events.
#


class ScriptCompleteEvent(object):
    def __init__(self, params):
        self.operation_id = params["operationId"]
        self.sequenceNumber = params["sequenceNumber"]
        self.error_details = params["errorDetails"]
        self.error_message = params["errorMessage"]
        self.has_error = params["hasError"]
        self.canceled = params["canceled"]
        self.success = params["success"]


class ScriptPlanNotificationEvent(object):
    def __init__(self, params):
        self.operation_id = params["operationId"]
        self.sequenceNumber = params["sequenceNumber"]
        self.scripting_objects = params["scriptingObjects"]
        self.count = params["count"]


class ScriptProgressNotificationEvent(object):
    def __init__(self, params):
        self.operation_id = params["operationId"]
        self.sequenceNumber = params["sequenceNumber"]
        self.scripting_object = params["scriptingObject"]
        self.status = params["status"]
        self.completed_count = params["completedCount"]
        self.total_count = params["totalCount"]


class ScriptResponse(object):
    def __init__(self, params):
        self.operation_id = params["operationId"]


class ScriptingResponseDecoder(object):
    """
    Decode response dictionary into scripting parameter type.
    """

    def __init__(self):
        # response map.
        self.response_dispatcher = {
            "scripting/scriptComplete": ScriptCompleteEvent,
            "scripting/scriptPlanNotification": ScriptPlanNotificationEvent,
            "scripting/scriptProgressNotification": ScriptProgressNotificationEvent,
            "id": ScriptResponse,
        }

    def decode_response(self, obj):
        """
        Decode valid response.
        """
        if "method" in obj:
            response_name = obj["method"]
            if response_name in self.response_dispatcher:
                # Handle event received.
                return self.response_dispatcher[response_name](obj["params"])

        if "id" in obj and "result" in obj:
            # Handle response received.
            return self.response_dispatcher["id"](obj["result"])

        logger.debug(f"Unable to decode response to a event type: {obj}")
        # Unable to decode, return json string.
        return obj
