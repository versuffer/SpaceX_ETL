import asyncio
from collections.abc import Coroutine

from pydantic import TypeAdapter

from app.db.models.launches import LaunchModel
from app.db.models.missions import MissionModel
from app.db.models.rockets import RocketModel
from app.schemas.etl.launches import LaunchSchema
from app.schemas.etl.missions import MissionSchema
from app.schemas.etl.rockets import RocketSchema
from app.services.base import AsyncRequestService
from app.services.repositories.postgres import (
    launch_links_repository,
    launches_repository,
    missions_repository,
    rockets_repository,
)
from app.settings.config import app_settings
from app.settings.logs import logger


class ETLTasks:
    def __init__(self, fetch_url: str = app_settings.SPACEX_URL):
        self.request_service = AsyncRequestService(base_url=fetch_url)
        self.queries = {
            'launches': {
                "query": "{ launches { id links { article_link flickr_images mission_patch mission_patch_small "
                "presskit reddit_campaign reddit_launch reddit_media reddit_recovery video_link wikipedia } } }"
            },
            'missions': {"query": "{ missions { id twitter wikipedia website } }"},
            'rockets': {"query": "{ rockets { id wikipedia } }"},
        }

    async def run_etl(self):
        tasks: list[Coroutine] = [
            self.launches_etl(),
            self.rockets_etl(),
            self.missions_etl(),
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def launches_etl(self):
        logger.info('Started launches ETL pipeline.')
        # Extract
        logger.info('Trying to fetch launches data.')
        data = await self.request_service.request(method='POST', json=self.queries['launches'])

        # Transform
        parsed_data_gen = (TypeAdapter(LaunchSchema).validate_python(launch) for launch in data['data']['launches'])

        # Load
        logger.info('Loading launches data to DB.')
        for launch_schema in parsed_data_gen:
            launch_id = launch_schema.launch_id
            launch_data = launch_schema.model_dump()
            launch_links_data = launch_data.pop('launch_links')

            launch_model = await self.create_or_update_launch(launch_id, launch_data)
            await self.create_or_update_launch_links(launch_model, launch_links_data)

        logger.info('Finished launches ETL pipeline.')

    @staticmethod
    async def create_or_update_launch(launch_id: str, launch_data: dict) -> LaunchModel:
        if not (launch_model := await launches_repository.get_one(launch_id=launch_id)):
            launch_model = await launches_repository.create(launch_data)
        else:
            launch_model = await launches_repository.update(launch_model.id, launch_data)

        return launch_model

    @staticmethod
    async def create_or_update_launch_links(launch_model: LaunchModel, launch_links_data: dict):
        if not (launch_links_model := await launch_links_repository.get_one(launch_uuid=launch_model.id)):
            await launch_links_repository.create(launch_links_data, launch_uuid=launch_model.id)
        else:
            await launch_links_repository.update(launch_links_model.id, launch_links_data)

    async def missions_etl(self):
        logger.info('Started missions ETL pipeline.')
        # Extract
        logger.info('Trying to fetch missions data.')
        data = await self.request_service.request(method='POST', json=self.queries['missions'])

        # Transform
        parsed_data_gen = (TypeAdapter(MissionSchema).validate_python(mission) for mission in data['data']['missions'])

        logger.info('Loading missions data to DB.')
        # Load
        for mission_schema in parsed_data_gen:
            mission_id = mission_schema.mission_id
            mission_data = mission_schema.model_dump()
            await self.create_or_update_mission(mission_id, mission_data)

        logger.info('Finished missions ETL pipeline.')

    @staticmethod
    async def create_or_update_mission(mission_id: str, mission_data: dict) -> MissionModel:
        if not (mission_model := await missions_repository.get_one(mission_id=mission_id)):
            mission_model = await missions_repository.create(mission_data)
        else:
            mission_model = await missions_repository.update(mission_model.id, mission_data)

        return mission_model

    async def rockets_etl(self):
        logger.info('Started rockets ETL pipeline.')
        # Extract
        logger.info('Trying to fetch rockets data.')
        data = await self.request_service.request(method='POST', json=self.queries['rockets'])

        # Transform
        parsed_data_gen = (TypeAdapter(RocketSchema).validate_python(rocket) for rocket in data['data']['rockets'])

        logger.info('Loading rockets data to DB.')
        # Load
        for rocket_schema in parsed_data_gen:
            rocket_id = rocket_schema.rocket_id
            rocket_data = rocket_schema.model_dump()
            await self.create_or_update_rocket(rocket_id, rocket_data)

        logger.info('Finished rockets ETL pipeline.')

    @staticmethod
    async def create_or_update_rocket(rocket_id: str, rocket_data: dict) -> RocketModel:
        if not (rocket_model := await rockets_repository.get_one(rocket_id=rocket_id)):
            rocket_model = await rockets_repository.create(rocket_data)
        else:
            rocket_model = await rockets_repository.update(rocket_model.id, rocket_data)

        return rocket_model


if __name__ == '__main__':
    asyncio.run(ETLTasks().run_etl())
