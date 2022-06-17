# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
import os
import time
import unittest

import mssqlscripter.jsonrpc.contracts.scriptingservice as scripting
import mssqlscripter.jsonrpc.jsonrpcclient as json_rpc_client


class ScriptingRequestTests(unittest.TestCase):
    """
    Scripting request tests.
    """

    def test_succesful_scripting_response_AdventureWorks2014(self):
        """
        Verifies that the scripting response of a successful request is read succesfully with a sample request against AdventureWorks2014.
        """
        with open(
            self.get_test_baseline("adventureworks2014_baseline.txt"),
            "r+b",
            buffering=0,
        ) as response_file:
            request_stream = io.BytesIO()
            rpc_client = json_rpc_client.JsonRpcClient(request_stream, response_file)
            rpc_client.start()
            # Submit a dummy request.
            parameters = {
                "FilePath": "Sample_File_Path",
                "ConnectionString": "Sample_connection_string",
                "IncludeObjectCriteria": None,
                "ExcludeObjectCriteria": None,
                "IncludeSchemas": None,
                "ExcludeSchemas": None,
                "IncludeTypes": None,
                "ExcludeTypes": None,
                "ScriptingObjects": None,
                "ScriptDestination": "ToSingleFile",
            }
            request = scripting.ScriptingRequest(1, rpc_client, parameters)

            self.verify_response_count(
                request=request,
                response_count=1,
                plan_notification_count=1,
                progress_count=1736,
                complete_count=1,
            )

            rpc_client.shutdown()

    def test_scripting_criteria_parameters(self):
        """
        Verify scripting objects are properly parsed.
        """
        include_objects = ["schema1.table1", "table2"]
        include_criteria = scripting.ScriptingObjects(include_objects)
        include_formatted = include_criteria.format()

        scripting_object_1 = include_formatted[0]
        scripting_object_2 = include_formatted[1]

        self.assertEqual(scripting_object_1["Schema"], "schema1")
        self.assertEqual(scripting_object_1["Name"], "table1")
        self.assertEqual(scripting_object_1["Type"], None)

        self.assertEqual(scripting_object_2["Schema"], None)
        self.assertEqual(scripting_object_2["Name"], "table2")
        self.assertEqual(scripting_object_2["Type"], None)

    def test_scripting_response_decoder(self):
        complete_event = {
            "jsonrpc": "2.0",
            "method": "scripting/scriptComplete",
            "params": {
                "operationId": "e18b9538-a7ff-4502-9c33-ac63ed42e5a5",
                "sequenceNumber": "3",
                "hasError": "false",
                "errorMessage": "",
                "errorDetails": "",
                "canceled": "false",
                "success": "true",
            },
        }

        progress_notification = {
            "jsonrpc": "2.0",
            "method": "scripting/scriptProgressNotification",
            "params": {
                "operationId": "e18b9538-a7ff-4502-9c33-ac63ed42e5a5",
                "sequenceNumber": "2",
                "status": "Completed",
                "completedCount": 3,
                "totalCount": 12,
                "scriptingObject": {
                    "type": "FullTextCatalog",
                    "schema": "null",
                    "name": "SampleFullTextCatalog",
                },
            },
        }

        plan_notification = {
            "jsonrpc": "2.0",
            "method": "scripting/scriptPlanNotification",
            "params": {
                "operationId": "e18b9538-a7ff-4502-9c33-ac63ed42e5a5",
                "sequenceNumber": "1",
                "scriptingObjects": [
                    {"type": "Database", "schema": "null", "name": "AdventureWorks2014"}
                ],
                "count": 10,
            },
        }

        decoder = scripting.ScriptingResponseDecoder()

        complete_decoded = decoder.decode_response(complete_event)
        progress_notification_decoded = decoder.decode_response(progress_notification)
        plan_notification_decoded = decoder.decode_response(plan_notification)

        self.assertIsNotNone(complete_decoded)
        self.assertIsNotNone(progress_notification_decoded)
        self.assertIsNotNone(plan_notification_decoded)

    def test_scripting_response_decoder_invalid(self):
        """
        Verify decode invalid response.
        """
        complete_event = {
            "jsonrpc": "2.0",
            "method": "connect/connectionComplete",
            "params": {"operationId": "e18b9538-a7ff-4502-9c33-ac63ed42e5a5"},
        }

        decoder = scripting.ScriptingResponseDecoder()

        complete_decoded = decoder.decode_response(complete_event)

        # events should remain untouched.
        self.assertTrue(isinstance(complete_decoded, dict))

    def test_default_script_options(self):
        """
        Verify default scripting options created.
        """
        scripting_options = scripting.ScriptingOptions()
        expected = {
            "ScriptAnsiPadding": False,
            "AppendToFile": False,
            "IncludeIfNotExists": False,
            "ContinueScriptingOnError": False,
            "ConvertUDDTToBaseType": False,
            "GenerateScriptForDependentObjects": False,
            "IncludeDescriptiveHeaders": False,
            "IncludeSystemConstraintNames": False,
            "IncludeUnsupportedStatements": False,
            "SchemaQualify": False,
            "Bindings": False,
            "Collation": False,
            "Default": False,
            "ScriptExtendedProperties": False,
            "ScriptLogins": False,
            "ScriptObjectLevelPermissions": False,
            "ScriptOwner": False,
            "ScriptUseDatabase": False,
            "ScriptChangeTracking": False,
            "ScriptCheckConstraints": False,
            "ScriptDataCompressionOptions": False,
            "ScriptForeignKeys": False,
            "ScriptFullTextIndexes": False,
            "ScriptIndexes": False,
            "ScriptPrimaryKeys": False,
            "ScriptTriggers": False,
            "UniqueKeys": False,
            "TypeOfDataToScript": "SchemaOnly",
            "ScriptCreateDrop": "ScriptCreate",
            "TargetDatabaseEngineType": "SingleInstance",
            "ScriptStatistics": "ScriptStatsNone",
            "ScriptCompatibilityOption": "Script140Compat",
            "TargetDatabaseEngineEdition": "SqlServerStandardEdition",
        }

        self.assertEqual(scripting_options.get_options(), expected)

    def test_nondefault_script_options(self):
        """
        Verify scripting options updated.
        """
        new_options = {
            "ScriptAnsiPadding": True,
            "AppendToFile": True,
            "TypeOfDataToScript": "SchemaOnly",
            "ScriptDropAndCreate": "ScriptCreate",
            "ScriptForTheDatabaseEngineType": "SingleInstance",
            "ScriptStatistics": "ScriptStatsNone",
            "ScriptCompatibilityOption": "Script140Compat",
            "TargetDatabaseEngineEdition": "SqlServerStandardEdition",
        }
        scripting_options = scripting.ScriptingOptions(new_options)

        expected = {
            "ScriptAnsiPadding": True,
            "AppendToFile": True,
            "IncludeIfNotExists": False,
            "ContinueScriptingOnError": False,
            "ConvertUDDTToBaseType": False,
            "GenerateScriptForDependentObjects": False,
            "IncludeDescriptiveHeaders": False,
            "IncludeSystemConstraintNames": False,
            "IncludeUnsupportedStatements": False,
            "SchemaQualify": False,
            "Bindings": False,
            "Collation": False,
            "Default": False,
            "ScriptExtendedProperties": False,
            "ScriptLogins": False,
            "ScriptObjectLevelPermissions": False,
            "ScriptOwner": False,
            "ScriptUseDatabase": False,
            "ScriptChangeTracking": False,
            "ScriptCheckConstraints": False,
            "ScriptDataCompressionOptions": False,
            "ScriptForeignKeys": False,
            "ScriptFullTextIndexes": False,
            "ScriptIndexes": False,
            "ScriptPrimaryKeys": False,
            "ScriptTriggers": False,
            "UniqueKeys": False,
            "TypeOfDataToScript": "SchemaOnly",
            "ScriptCreateDrop": "ScriptCreate",
            "TargetDatabaseEngineType": "SingleInstance",
            "ScriptStatistics": "ScriptStatsNone",
            "ScriptCompatibilityOption": "Script140Compat",
            "TargetDatabaseEngineEdition": "SqlServerStandardEdition",
        }

        self.assertEqual(scripting_options.get_options(), expected)

    def test_invalid_script_options(self):
        """
        Verify invalid script options.
        """
        invalid_options = {"ScriptAnsiPadding": "NonValid"}

        invalid_server_version = {"ScriptCompatibilityOption": "SQL Server 1689"}

        with self.assertRaises(ValueError):
            scripting.ScriptingOptions(invalid_options)
        with self.assertRaises(ValueError):
            scripting.ScriptingOptions(invalid_server_version)

    def test_script_database_params_format(self):
        """
        Verify scripting parameters format.
        """
        params = {
            "FilePath": "C:\\temp\\sample_db.sql",
            "ConnectionString": "Sample_connection_string",
            "IncludeObjectCriteria": [],
            "ExcludeObjectCriteria": [],
            "IncludeSchemas": None,
            "ExcludeSchemas": None,
            "IncludeTypes": None,
            "ExcludeTypes": None,
            "ScriptingObjects": ["Person.Person"],
            "ScriptDestination": "ToSingleFile",
        }
        scripting_params = scripting.ScriptingParams(params)

        formatted_params = scripting_params.format()
        expected_script_options = {
            "ScriptAnsiPadding": False,
            "AppendToFile": False,
            "IncludeIfNotExists": False,
            "ContinueScriptingOnError": False,
            "ConvertUDDTToBaseType": False,
            "GenerateScriptForDependentObjects": False,
            "IncludeDescriptiveHeaders": False,
            "IncludeSystemConstraintNames": False,
            "IncludeUnsupportedStatements": False,
            "SchemaQualify": False,
            "Bindings": False,
            "Collation": False,
            "Default": False,
            "ScriptExtendedProperties": False,
            "ScriptLogins": False,
            "ScriptObjectLevelPermissions": False,
            "ScriptOwner": False,
            "ScriptUseDatabase": False,
            "ScriptChangeTracking": False,
            "ScriptCheckConstraints": False,
            "ScriptDataCompressionOptions": False,
            "ScriptForeignKeys": False,
            "ScriptFullTextIndexes": False,
            "ScriptIndexes": False,
            "ScriptPrimaryKeys": False,
            "ScriptTriggers": False,
            "UniqueKeys": False,
            "TypeOfDataToScript": "SchemaOnly",
            "ScriptCreateDrop": "ScriptCreate",
            "TargetDatabaseEngineType": "SingleInstance",
            "ScriptStatistics": "ScriptStatsNone",
            "ScriptCompatibilityOption": "Script140Compat",
            "TargetDatabaseEngineEdition": "SqlServerStandardEdition",
        }

        self.assertEqual(formatted_params["FilePath"], "C:\\temp\\sample_db.sql")
        self.assertEqual(
            formatted_params["ConnectionString"], "Sample_connection_string"
        )
        # Reenable assertion below when the option is supported.
        # self.assertEqual(formatted_params['DatabaseObjects'], ['Person.Person'])
        self.assertEqual(formatted_params["ScriptOptions"], expected_script_options)

    def verify_response_count(
        self,
        request,
        response_count,
        plan_notification_count,
        progress_count,
        complete_count,
        func=None,
    ):
        """
        Helper to verify expected response count from a request.
        """
        progress_notification_event = 0
        complete_event = 0
        response_event = 0
        plan_notification_event = 0
        request.execute()

        # There is a intermittent failure where for a moment there is no response read so we throw a exception,
        # and lose all previous responses. This only happens in a test scenario when reading from a file.
        # For now the fix is to add a timer to allow the request to process in the background so we can process
        # the response.
        time.sleep(1)

        while not request.completed():
            response = request.get_response()
            if func:
                func(self, response)
            if response:
                if isinstance(response, scripting.ScriptProgressNotificationEvent):
                    progress_notification_event += 1
                elif isinstance(response, scripting.ScriptCompleteEvent):
                    complete_event += 1
                elif isinstance(response, scripting.ScriptResponse):
                    response_event += 1
                elif isinstance(response, scripting.ScriptPlanNotificationEvent):
                    plan_notification_event += 1

        self.assertEqual(response_event, response_count)
        self.assertEqual(plan_notification_event, plan_notification_count)
        self.assertEqual(progress_notification_event, progress_count)
        self.assertEqual(complete_event, complete_count)

    # Helper to generate a baseline for AdventureWorks
    #
    def generate_new_baseline(self, file_name):
        """
        Helper function to generate new baselines for scripting request test.
        """
        import subprocess
        import time

        # Point sqltoolsservice output to file.
        with io.open(file_name, "wb") as baseline:
            tools_service_process = subprocess.Popen(
                "D:\\GitHub\\sqltoolsservice\\src\\Microsoft.SqlTools.ServiceLayer\\bin\\Debug\\netcoreapp2.0\\win7-x64\\MicrosoftSqlToolsServiceLayer.exe",
                bufsize=0,
                stdin=subprocess.PIPE,
                stdout=baseline,
            )

            # Update these parameters in order to user function.
            parameters = {
                "FilePath": "D:\\Temp\\adventureworks2014.temp.sql",
                "ConnectionString": "server=bro-hb;database=AdventureWorks2014;Integrated Security=true",
                "IncludeObjectCriteria": None,
                "ExcludeObjectCriteria": None,
                "IncludeSchemas": None,
                "ExcludeSchemas": None,
                "IncludeTypes": None,
                "ExcludeTypes": None,
                "ScriptingObjects": None,
            }

            writer = json_rpc_client.JsonRpcWriter(tools_service_process.stdin)
            writer.send_request("scripting/script", parameters, id=1)
            # submit raw request.
            time.sleep(30)

            tools_service_process.kill()

    # Uncomment to generate a baseline for AdventureWorks
    #
    # def test_gen_baseline(self):
    #    self.generate_new_baseline(u'adventureworks2014_baseline.txt')

    def get_test_baseline(self, file_name):
        """
        Helper method to get baseline file.
        """
        return os.path.abspath(
            os.path.join(
                os.path.abspath(__file__), "..", "scripting_baselines", file_name
            )
        )


if __name__ == "__main__":
    unittest.main()
