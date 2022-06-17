# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import getpass
import os
import shutil
import sys

import mssqlscripter

MSSQL_SCRIPTER_CONNECTION_STRING = "MSSQL_SCRIPTER_CONNECTION_STRING"
MSSQL_SCRIPTER_PASSWORD = "MSSQL_SCRIPTER_PASSWORD"


def parse_arguments(args):
    """
    Initialize parser with scripter options.
    """
    parser = argparse.ArgumentParser(
        prog="mssql-scripter",
        description="Microsoft SQL Server Scripter Command Line Tool. "
        + f"Version {mssqlscripter.__version__}",
    )

    group_connection_options = parser.add_mutually_exclusive_group()
    group_connection_options.add_argument(
        "--connection-string",
        dest="ConnectionString",
        metavar="",
        help="Connection string of database to script. If connection string and server are not supplied, defaults to value in environment variable MSSQL_SCRIPTER_CONNECTION_STRING.",
    )
    group_connection_options.add_argument(
        "-S", "--server", dest="Server", metavar="", help="Server name."
    )

    parser.add_argument(
        "-d", "--database", dest="Database", metavar="", help="Database name."
    )

    parser.add_argument(
        "-U", "--user", dest="UserId", metavar="", help="Login ID for server."
    )

    parser.add_argument(
        "-P",
        "--password",
        dest="Password",
        metavar="",
        help="If not supplied, defaults to value in environment variable MSSQL_SCRIPTER_PASSWORD.",
    )

    # Basic parameters.
    parser.add_argument(
        "-f",
        "--file-path",
        dest="FilePath",
        metavar="",
        default=None,
        help="File to script out to or directory name if scripting file per object.",
    )

    parser.add_argument(
        "--file-per-object",
        dest="ScriptDestination",
        action="store_const",
        const="ToFilePerObject",
        default="ToSingleFile",
        help="By default script to a single file. If supplied and given a directory for --file-path, script a file per object to that directory.",
    )

    group_type_of_data = parser.add_mutually_exclusive_group()
    group_type_of_data.add_argument(
        "--data-only",
        dest="TypeOfDataToScript",
        action="store_const",
        const="DataOnly",
        default="SchemaOnly",
        help="By default only the schema is scripted. if supplied, generate scripts that contains data only.",
    )
    group_type_of_data.add_argument(
        "--schema-and-data",
        dest="TypeOfDataToScript",
        action="store_const",
        const="SchemaAndData",
        default="SchemaOnly",
        help="By default only the schema is scripted. if supplied, generate scripts that contain schema and data.",
    )

    group_create_drop = parser.add_mutually_exclusive_group()
    group_create_drop.add_argument(
        "--script-create",
        dest="ScriptCreateDrop",
        action="store_const",
        const="ScriptCreate",
        default="ScriptCreate",
        help="Script object CREATE statements.",
    )
    group_create_drop.add_argument(
        "--script-drop",
        dest="ScriptCreateDrop",
        action="store_const",
        const="ScriptDrop",
        default="ScriptCreate",
        help="Script object DROP statements.",
    )
    group_create_drop.add_argument(
        "--script-drop-create",
        dest="ScriptCreateDrop",
        action="store_const",
        const="ScriptCreateDrop",
        default="ScriptCreate",
        help="Script object CREATE and DROP statements.",
    )

    parser.add_argument(
        "--target-server-version",
        dest="ScriptCompatibilityOption",
        choices=[
            "2005",
            "2008",
            "2008R2",
            "2012",
            "2014",
            "2016",
            "vNext",
            "AzureDB",
            "AzureDW",
        ],
        default="2016",
        help="Script only features compatible with the specified SQL Version.",
    )

    parser.add_argument(
        "--target-server-edition",
        dest="TargetDatabaseEngineEdition",
        choices=["Standard", "Personal", "Express", "Enterprise", "Stretch"],
        default="Enterprise",
        help="Script only features compatible with the specified SQL Server database edition.",
    )

    parser.add_argument(
        "--include-objects",
        dest="IncludeObjects",
        nargs="*",
        type=str,
        metavar="",
        help="Database objects to include in script.",
    )

    parser.add_argument(
        "--exclude-objects",
        dest="ExcludeObjects",
        nargs="*",
        type=str,
        metavar="",
        help="Database objects to exclude from script.",
    )

    parser.add_argument(
        "--include-schemas",
        dest="IncludeSchemas",
        nargs="*",
        type=str,
        metavar="",
        help="Database objects of this schema to include in script.",
    )

    parser.add_argument(
        "--exclude-schemas",
        dest="ExcludeSchemas",
        nargs="*",
        type=str,
        metavar="",
        help="Database objects of this schema to exclude from script.",
    )

    parser.add_argument(
        "--include-types",
        dest="IncludeTypes",
        nargs="*",
        type=str,
        metavar="",
        help="Database objects of this type to include in script.",
    )

    parser.add_argument(
        "--exclude-types",
        dest="ExcludeTypes",
        nargs="*",
        type=str,
        metavar="",
        help="Database objects of this type to exclude from script.",
    )

    # General boolean Scripting Options
    parser.add_argument(
        "--ansi-padding",
        dest="ScriptAnsiPadding",
        action="store_true",
        default=False,
        help="Generates ANSI Padding statements.",
    )

    parser.add_argument(
        "--append",
        dest="AppendToFile",
        action="store_true",
        default=False,
        help="Append script to file.",
    )

    parser.add_argument(
        "--check-for-existence",
        dest="IncludeIfNotExists",
        action="store_true",
        default=False,
        help="Check that an object with the given name exists before dropping or altering or that an object with the given name does not exist before creating.",
    )

    parser.add_argument(
        "-r",
        "--continue-on-error",
        dest="ContinueScriptingOnError",
        action="store_true",
        default=False,
        help="Continue scripting on error.",
    )

    parser.add_argument(
        "--convert-uddts",
        dest="ConvertUDDTToBaseType",
        action="store_true",
        default=False,
        help="Convert user-defined data types to base types.",
    )

    parser.add_argument(
        "--include-dependencies",
        dest="GenerateScriptForDependentObjects",
        action="store_true",
        default=False,
        help="Generate script for the dependent objects for each object scripted.",
    )

    parser.add_argument(
        "--exclude-headers",
        dest="IncludeDescriptiveHeaders",
        action="store_false",
        default=True,
        help="Exclude descriptive headers for each object scripted.",
    )

    parser.add_argument(
        "--constraint-names",
        dest="IncludeSystemConstraintNames",
        action="store_true",
        default=False,
        help="Include system constraint names to enforce declarative referential integrity.",
    )

    parser.add_argument(
        "--unsupported-statements",
        dest="IncludeUnsupportedStatements",
        action="store_true",
        default=False,
        help="Include statements in the script that are not supported on the target SQL Server Version.",
    )

    parser.add_argument(
        "--disable-schema-qualification",
        dest="SchemaQualify",
        action="store_false",
        default=True,
        help="Do not prefix object names with the object schema.",
    )

    parser.add_argument(
        "--bindings",
        dest="Bindings",
        action="store_true",
        default=False,
        help="Script options to set binding options.",
    )

    parser.add_argument(
        "--collation",
        dest="Collation",
        action="store_true",
        default=False,
        help="Script the objects that use collation.",
    )

    parser.add_argument(
        "--exclude-defaults",
        dest="Default",
        action="store_false",
        default=True,
        help="Do not script the default values.",
    )

    parser.add_argument(
        "--exclude-extended-properties",
        dest="ScriptExtendedProperties",
        action="store_false",
        default=True,
        help="Exclude extended properties for each object scripted.",
    )

    parser.add_argument(
        "--logins",
        dest="ScriptLogins",
        action="store_true",
        default=False,
        help="Script all logins available on the server, passwords will not be scripted.",
    )

    parser.add_argument(
        "--object-permissions",
        dest="ScriptObjectLevelPermissions",
        action="store_true",
        default=False,
        help="Generate object-level permissions.",
    )

    parser.add_argument(
        "--owner",
        dest="ScriptOwner",
        action="store_true",
        default=False,
        help="Script owner for the objects.",
    )

    parser.add_argument(
        "--exclude-use-database",
        dest="ScriptUseDatabase",
        action="store_false",
        default=True,
        help="Do not generate USE DATABASE statement.",
    )

    parser.add_argument(
        "--statistics",
        dest="ScriptStatistics",
        action="store_const",
        const="ScriptStatsAll",
        default="ScriptStatsNone",
        help="Script all statistics.",
    )

    parser.add_argument(
        "--database-engine-type",
        dest="TargetDatabaseEngineType",
        # This parameter is determined based on engine edition and version in
        # the background. User cannot select it.
        action="store_const",
        const="SingleInstance",
        default="SingleInstance",
        help=argparse.SUPPRESS,
    )

    # Table/View Options
    parser.add_argument(
        "--change-tracking",
        dest="ScriptChangeTracking",
        action="store_true",
        default=False,
        help="Script the change tracking information.",
    )

    parser.add_argument(
        "--exclude-check-constraints",
        dest="ScriptCheckConstraints",
        action="store_false",
        default=True,
        help="Exclude check constraints for each table or view scripted.",
    )

    parser.add_argument(
        "--data-compressions",
        dest="ScriptDataCompressionOptions",
        action="store_true",
        default=False,
        help="Script the data compression information.",
    )

    parser.add_argument(
        "--exclude-foreign-keys",
        dest="ScriptForeignKeys",
        action="store_false",
        default=True,
        help="Exclude foreign keys for each table scripted.",
    )

    parser.add_argument(
        "--exclude-full-text-indexes",
        dest="ScriptFullTextIndexes",
        action="store_false",
        default=True,
        help="Exclude full-text indexes for each table or indexed view scripted.",
    )

    parser.add_argument(
        "--exclude-indexes",
        dest="ScriptIndexes",
        action="store_false",
        default=True,
        help="Exclude indexes (XML and clustered) for each table or indexed view scripted.",
    )

    parser.add_argument(
        "--exclude-primary-keys",
        dest="ScriptPrimaryKeys",
        action="store_false",
        default=True,
        help="Exclude primary keys for each table or view scripted.",
    )

    parser.add_argument(
        "--exclude-triggers",
        dest="ScriptTriggers",
        action="store_false",
        default=True,
        help="Exclude triggers for each table or view scripted.",
    )

    parser.add_argument(
        "--exclude-unique-keys",
        dest="UniqueKeys",
        action="store_false",
        default=True,
        help="Exclude unique keys for each table or view scripted.",
    )

    # Configuration Options.
    parser.add_argument(
        "--display-progress",
        dest="DisplayProgress",
        action="store_true",
        default=False,
        help="Display scripting progress.",
    )

    parser.add_argument(
        "--enable-toolsservice-logging",
        dest="EnableLogging",
        action="store_true",
        default=False,
        help="Enable verbose logging.",
    )

    parser.add_argument(
        "--version", action="version", version=f"{mssqlscripter.__version__}"
    )

    parameters = parser.parse_args(args)
    verify_directory(parameters)

    if parameters.Server:
        build_connection_string(parameters)
    elif parameters.ConnectionString is None:
        # Check environment variable for connection string.
        if not get_connection_string_from_environment(parameters):
            sys.stdout.write(
                "Please specify connection information using --connection-string or --server and/or --database --user.\n"
            )
            sys.exit()

    map_server_options(parameters)
    return parameters


def verify_directory(parameters):
    """
    If creating a file per object, create the directory if it does not exist.
    """

    target_directory = parameters.FilePath
    if parameters.ScriptDestination == "ToFilePerObject":
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        # Give warning to user that target directory was not empty.
        if os.listdir(target_directory):
            sys.stdout.write(
                f"warning: Target directory {target_directory} was not empty."
            )


def get_connection_string_from_environment(parameters):
    """
    Get connection string from environment variable.
    """
    if MSSQL_SCRIPTER_CONNECTION_STRING in os.environ:
        parameters.ConnectionString = os.environ[MSSQL_SCRIPTER_CONNECTION_STRING]
        return True

    return False


def build_connection_string(parameters):
    """
    Build connection string.
    """
    connection_string = f"Server={parameters.Server};"
    if parameters.Database:
        connection_string += f"Database={parameters.Database};"

    # Standard connection if user id is supplied.
    if parameters.UserId:
        connection_string += f"User Id={parameters.UserId};"
        # If no password supplied, check for environment variable.
        if parameters.Password is None and MSSQL_SCRIPTER_PASSWORD in os.environ:
            parameters.Password = os.environ[MSSQL_SCRIPTER_PASSWORD]

        connection_string += f"Password={parameters.Password or getpass.getpass()};"
    else:
        connection_string += "Integrated Security=True;"

    parameters.ConnectionString = connection_string


def map_server_options(parameters):
    """
    Map short form to long form name and maps Azure versions to their appropriate editions.
    """
    azure_server_edition_map = {
        "AzureDB": "SqlAzureDatabaseEdition",
        "AzureDW": "SqlDatawarehouseEdition",
    }

    on_prem_server_edition_map = {
        "Standard": "SqlServerStandardEdition",
        "Personal": "SqlServerPersonalEdition",
        "Express": "SqlServerExpressEdition",
        "Enterprise": "SqlServerEnterpriseEdition",
        "Stretch": "SqlServerStretchDatabaseEdition",
    }

    on_prem_server_version_map = {
        "2005": "Script90Compat",
        "2008": "Script100Compat",
        "2008R2": "Script105Compat",
        "2012": "Script110Compat",
        "2014": "Script120Compat",
        "2016": "Script130Compat",
        "vNext": "Script140Compat",
    }

    target_server_version = parameters.ScriptCompatibilityOption
    target_server_edition = parameters.TargetDatabaseEngineEdition
    # When targetting Azure, only the edition matters.
    if "Azure" in target_server_version:
        # SMO requires 120 compat or higher when scripting Azure or AzureDW.
        parameters.ScriptCompatibilityOption = "Script130Compat"
        parameters.TargetDatabaseEngineEdition = azure_server_edition_map[
            target_server_version
        ]
        parameters.TargetDatabaseEngineType = "SqlAzure"

    else:
        parameters.ScriptCompatibilityOption = on_prem_server_version_map[
            target_server_version
        ]
        parameters.TargetDatabaseEngineEdition = on_prem_server_edition_map[
            target_server_edition
        ]
        parameters.TargetDatabaseEngineType = "SingleInstance"

    return parameters
