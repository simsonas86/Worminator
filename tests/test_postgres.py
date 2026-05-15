import unittest

from tests.support.dependency_stubs import install_test_environment
from tests.support.db_fakes import FakeConnection, FakePool


install_test_environment()

import postgres


class PostgresTests(unittest.IsolatedAsyncioTestCase):
    async def test_GetConn_WhenWrappedFunctionRaises_ShouldReraiseException(self):
        expected_error = RuntimeError("database failure")

        @postgres.get_conn
        async def failing_query(connection):
            raise expected_error

        with self.assertRaisesRegex(RuntimeError, "database failure"):
            await failing_query(FakePool(FakeConnection()))

    async def test_GetAllTickets_WhenRowsExist_ShouldReturnUserTicketMapping(self):
        connection = FakeConnection()
        connection.fetch_rows = [
            {"user_id": 1, "ticket_count": 4},
            {"user_id": 2, "ticket_count": 0},
        ]

        tickets = await postgres.get_all_tickets(FakePool(connection))

        self.assertEqual(tickets, {1: 4, 2: 0})

    async def test_GetUserTickets_WhenUserMissing_ShouldReturnZero(self):
        connection = FakeConnection()
        connection.fetchrow_result = None

        tickets = await postgres.get_user_tickets(FakePool(connection), 1)

        self.assertEqual(tickets, 0)

    async def test_ResolveRaffleTickets_WhenWinnerAndUsersToCredit_ShouldExecuteInSingleTransaction(self):
        connection = FakeConnection()

        await postgres.resolve_raffle_tickets(
            FakePool(connection),
            (1, "alice"),
            [(2, "bob"), (3, "cora")],
            2,
        )

        self.assertTrue(connection.transaction_context.entered)
        self.assertTrue(connection.transaction_context.exited)
        self.assertEqual(len(connection.operations), 1)
        operation, query, args = connection.operations[0]
        self.assertEqual(operation, "execute")
        self.assertIn("times_coached = users.times_coached + 1", query)
        self.assertEqual(args, (1, "alice"))
        self.assertEqual(len(connection.executemany_calls), 1)
        _, values = connection.executemany_calls[0]
        self.assertEqual(values, [(2, "bob", 2), (3, "cora", 2)])

    async def test_ResolveRaffleTickets_WhenNoWinner_ShouldOnlyCreditParticipants(self):
        connection = FakeConnection()

        await postgres.resolve_raffle_tickets(
            FakePool(connection),
            None,
            [(2, "bob")],
            3,
        )

        self.assertEqual(connection.operations, [])
        self.assertEqual(len(connection.executemany_calls), 1)
        _, values = connection.executemany_calls[0]
        self.assertEqual(values, [(2, "bob", 3)])
