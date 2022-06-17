# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

import mssqlscripter.argparser as parser


class TestParser(unittest.TestCase):
    def test_connection_string_builder(self):
        """
        Verify connection string is built correctly based on auth type.
        """

        trusted_connection = ["-S", "TestServer"]
        parameters = parser.parse_arguments(trusted_connection)
        self.assertEqual(
            parameters.ConnectionString, "Server=TestServer;Integrated Security=True;"
        )

        trusted_connection = ["-S", "TestServer", "-d", "mydatabase"]
        parameters = parser.parse_arguments(trusted_connection)
        self.assertEqual(
            parameters.ConnectionString,
            "Server=TestServer;Database=mydatabase;Integrated Security=True;",
        )

        trusted_connection = [
            "--connection-string",
            "Server=TestServer;Database=mydatabase;Integrated Security=True;",
        ]
        parameters = parser.parse_arguments(trusted_connection)
        self.assertEqual(
            parameters.ConnectionString,
            "Server=TestServer;Database=mydatabase;Integrated Security=True;",
        )

        standard_connection = [
            "-S",
            "TestServer",
            "-d",
            "mydatabase",
            "-U",
            "my_username",
            "-P",
            "PLACEHOLDER",
        ]
        parameters = parser.parse_arguments(standard_connection)
        self.assertEqual(
            parameters.ConnectionString,
            "Server=TestServer;Database=mydatabase;User Id=my_username;Password=PLACEHOLDER;",
        )

    def test_connection_string_with_environment(self):
        """
        Verify parser picks up connection string and password from environment variable.
        """
        os.environ[
            parser.MSSQL_SCRIPTER_CONNECTION_STRING
        ] = "Server=TestServer;Database=mydatabase;User Id=my_username;Password=PLACEHOLDER;"
        parameters = parser.parse_arguments(["--append"])
        self.assertEqual(
            parameters.ConnectionString,
            "Server=TestServer;Database=mydatabase;User Id=my_username;Password=PLACEHOLDER;",
        )

        standard_connection = [
            "-S",
            "TestServer",
            "-d",
            "mydatabase",
            "-U",
            "my_username",
        ]
        os.environ[parser.MSSQL_SCRIPTER_PASSWORD] = "PLACEHOLDER"
        parameters = parser.parse_arguments(standard_connection)
        self.assertEqual(
            parameters.ConnectionString,
            "Server=TestServer;Database=mydatabase;User Id=my_username;Password=PLACEHOLDER;",
        )


if __name__ == "__main__":
    unittest.main()
