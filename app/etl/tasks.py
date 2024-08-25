import asyncio

from pydantic import TypeAdapter

from app.db.models.launches import LaunchModel
from app.schemas.etl.launches import LaunchSchema
from app.services.base import AsyncRequestService
from app.services.repositories.postgres import (
    launch_links_repository,
    launches_repository,
)
from app.settings.config import app_settings


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

    async def launches_etl(self):
        # Extract
        data = await self.request_service.request(method='POST', json=self.queries['launches'])

        # Transform
        parsed_data = (TypeAdapter(LaunchSchema).validate_python(launch) for launch in data['data']['launches'])

        # Load
        for launch_schema in parsed_data:
            launch_id = launch_schema.launch_id
            launch_data = launch_schema.model_dump()
            launch_links_data = launch_data.pop('launch_links')

            launch_model = await self.create_or_update_launch(launch_id, launch_data)
            await self.create_or_update_launch_links(launch_model, launch_links_data)

    async def create_or_update_launch(self, launch_id: str, launch_data: dict) -> LaunchModel:
        if not (launch_model := await launches_repository.get_one(launch_id=launch_id)):
            launch_model = await launches_repository.create(launch_data)
        else:
            launch_model = await launches_repository.update(launch_model.id, launch_data)

        return launch_model

    async def create_or_update_launch_links(self, launch_model: LaunchModel, launch_links_data: dict):
        if not (launch_links_model := await launch_links_repository.get_one(launch_uuid=launch_model.id)):
            await launch_links_repository.create(launch_links_data, launch_uuid=launch_model.id)
        else:
            await launch_links_repository.update(launch_links_model.id, launch_links_data)

    async def missions_etl(self):
        data = await self.request_service.request(method='POST', json=self.queries['missions'])

    async def rockets_etl(self):
        data = await self.request_service.request(method='POST', json=self.queries['rockets'])


if __name__ == '__main__':
    asyncio.run(ETLTasks().launches_etl())
