import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from tests.support.dependency_stubs import install_test_environment
from tests.support.fakes import FakeCloseablePool, FakeReadyEvent, FakeTask


install_test_environment()

from main import Worminator


async def successful_operation(value):
    return value * 2


async def failing_operation():
    raise RuntimeError("boom")


class WorminatorTests(unittest.IsolatedAsyncioTestCase):
    async def test_OnReady_WhenPoolAndWorkerMissing_ShouldJoinChannelCreatePoolAndStartWorker(self):
        bot = Worminator()
        ready_event = FakeReadyEvent()
        pool = FakeCloseablePool()
        task = FakeTask()

        def fake_create_task(coro):
            coro.close()
            return task

        with patch("main.TARGET_CHANNEL", "test_channel"), \
             patch("main.create_pool", new=AsyncMock(return_value=pool)) as create_pool, \
             patch("main.asyncio.create_task", side_effect=fake_create_task) as create_task:
            await bot.on_ready(ready_event)

        self.assertEqual(ready_event.chat.joined_rooms, ["test_channel"])
        create_pool.assert_awaited_once()
        create_task.assert_called_once()
        self.assertIs(bot.pool, pool)
        self.assertIs(bot.db_worker_task, task)

    async def test_OnReady_WhenPoolAndWorkerExist_ShouldReuseExistingResources(self):
        bot = Worminator()
        ready_event = FakeReadyEvent()
        pool = FakeCloseablePool()
        task = FakeTask()
        bot.pool = pool
        bot.db_worker_task = task

        with patch("main.TARGET_CHANNEL", "test_channel"), \
             patch("main.create_pool", new=AsyncMock()) as create_pool, \
             patch("main.asyncio.create_task") as create_task:
            await bot.on_ready(ready_event)

        self.assertEqual(ready_event.chat.joined_rooms, ["test_channel"])
        create_pool.assert_not_awaited()
        create_task.assert_not_called()
        self.assertIs(bot.pool, pool)
        self.assertIs(bot.db_worker_task, task)

    async def test_QueueDb_WhenOperationSucceeds_ShouldReturnOperationResult(self):
        bot = Worminator()
        bot.db_worker_task = asyncio.create_task(bot.db_worker())

        try:
            result = await bot.queue_db(successful_operation, 21)
        finally:
            await bot.stop()

        self.assertEqual(result, 42)
        self.assertIsNone(bot.db_worker_task)

    async def test_QueueDb_WhenOperationFails_ShouldPropagateException(self):
        bot = Worminator()
        bot.db_worker_task = asyncio.create_task(bot.db_worker())

        try:
            with self.assertRaisesRegex(RuntimeError, "boom"):
                await bot.queue_db(failing_operation)
        finally:
            await bot.stop()

    async def test_Stop_WhenWorkerAndPoolExist_ShouldStopWorkerAndClosePool(self):
        bot = Worminator()
        pool = FakeCloseablePool()
        bot.pool = pool
        bot.db_worker_task = asyncio.create_task(bot.db_worker())

        await bot.stop()

        self.assertTrue(pool.closed)
        self.assertIsNone(bot.pool)
        self.assertIsNone(bot.db_worker_task)
