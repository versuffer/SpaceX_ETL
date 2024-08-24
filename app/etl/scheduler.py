import asyncio
from datetime import datetime
from typing import Callable, Coroutine

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.settings.logs import logger


class ETLScheduler:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()

    def run(self, *, task: Callable[[], Coroutine] | None = None):
        logger.info('Run scheduled tasks for ETL scheduler.')
        logger.info(f'{task=}')

        if task:
            self.scheduler.add_job(
                task,
                'cron',
                name='ETL scheduler',
                minute='*/5',
                max_instances=1,
                misfire_grace_time=1 * 60,
                next_run_time=datetime.now(),
            )
        self.scheduler.start()

        try:
            asyncio.get_event_loop().run_forever()
        except (KeyboardInterrupt, SystemExit):
            pass


# if __name__ == '__main__':
#     ETLScheduler().run(task=task)
