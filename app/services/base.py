from json import JSONDecodeError
from typing import Any, Literal, TypeAlias, Union

import backoff
from httpx import AsyncClient, ConnectError, ConnectTimeout, ReadTimeout, Response
from httpx._types import HeaderTypes, QueryParamTypes, URLTypes, VerifyTypes

from app.settings.logs import logger

StatusCode: TypeAlias = int
JsonContent: TypeAlias = dict
TextContent: TypeAlias = str


class AsyncRequestService:
    def __init__(
        self,
        *,
        base_url: URLTypes = "",
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        verify: VerifyTypes | None = False,
        trust_env: bool = False,
        **extra_client_kwargs,
    ) -> None:
        self._client_kwargs = dict(
            base_url=base_url,
            params=params,
            headers=headers,
            verify=verify,
            trust_env=trust_env,
            **extra_client_kwargs,
        )

    async def make_request(
        self,
        url: str = '',
        *,
        method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] = 'GET',
        params: QueryParamTypes | None = None,
        json: Any | None = None,
        **extra_kwargs,
    ) -> tuple[StatusCode, Union[JsonContent | TextContent]]:
        @backoff.on_exception(
            backoff.expo,
            (ReadTimeout, ConnectTimeout, ConnectError),
            max_tries=2,
            logger=logger,
            raise_on_giveup=True,
        )
        async def _make_request() -> Response:
            async with AsyncClient(**self._client_kwargs) as client:
                logger.debug(f'Request: {self} -> {method} -> {url or client.base_url}. ')
                return await client.request(method, url, params=params, json=json, **extra_kwargs)

        try:
            response = await _make_request()
        except (ReadTimeout, ConnectTimeout, ConnectError) as err:
            message = 'One of services is not available.'
            logger.exception(
                f'{message} {method=} {self._client_kwargs.get("base_url")=} '
                f'{url=}, {params=}, {json=}, {extra_kwargs=}'
            )
            raise err

        try:
            content = response.json()
        except JSONDecodeError:
            content = response.text

        return response.status_code, content
