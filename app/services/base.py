from typing import Any, Literal, TypeAlias

import backoff
from httpx import AsyncClient, ConnectError, ConnectTimeout, ReadTimeout, Response
from httpx._types import HeaderTypes, QueryParamTypes, URLTypes, VerifyTypes

from app.settings.logs import logger

JsonContent: TypeAlias = dict


class AsyncRequestService:
    def __init__(
        self,
        *,
        base_url: URLTypes = "",
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        verify: VerifyTypes | None = False,
        **extra_client_kwargs,
    ) -> None:
        self._client_kwargs = dict(
            base_url=base_url,
            params=params,
            headers=headers,
            verify=verify,
            **extra_client_kwargs,
        )

    async def request(
        self,
        url: str = '',
        *,
        method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] = 'GET',
        params: QueryParamTypes | None = None,
        json: Any | None = None,
        **extra_kwargs,
    ) -> JsonContent:
        @backoff.on_exception(
            backoff.expo,
            (ReadTimeout, ConnectTimeout, ConnectError),
            max_tries=2,
            logger=logger,
            raise_on_giveup=True,
        )
        async def _request() -> Response:
            async with AsyncClient(**self._client_kwargs) as client:
                logger.debug(f'Request: {self} -> {method} -> {url or client.base_url}. ')
                return await client.request(method, url, params=params, json=json, **extra_kwargs)

        try:
            response = await _request()
            response.raise_for_status()
            return response.json()
        except (ReadTimeout, ConnectTimeout, ConnectError) as err:
            logger.exception(
                f'Request {method=} {self._client_kwargs.get("base_url")=} '
                f'{url=}, {params=}, {json=}, {extra_kwargs=}'
            )
            raise err
