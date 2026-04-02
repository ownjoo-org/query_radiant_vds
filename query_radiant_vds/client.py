import base64
import logging
from asyncio import Queue
from typing import AsyncGenerator, Optional

from httpx import AsyncClient, HTTPError, HTTPStatusError, Response
from ownjoo_utils import get_value
from ownjoo_utils.logging.decorators import timed_async_generator
from retry_async import retry

from query_radiant_vds.consts import RETRY_BACKOFF_FACTOR, RETRY_COUNT

logger = logging.getLogger(__name__)


@retry(
    exceptions=Exception,
    tries=RETRY_COUNT,
    delay=1,
    backoff=RETRY_BACKOFF_FACTOR,
    max_delay=5,
    logger=logger,
    is_async=True,
)
async def get_response(
    url: str,
    method: str = "GET",
    params=None,
    json: Optional[dict] = None,
    data: Optional[dict] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    proxies: Optional[dict] = None,
) -> Optional[dict]:
    async with AsyncClient(follow_redirects=True, http2=True) as session:
        try:
            if isinstance(proxies, dict):
                session.proxies = proxies

            session.headers.update(
                {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                }
            )

            # Add basic auth header if credentials provided
            if username and password:
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                session.headers.update({"Authorization": f"Basic {credentials}"})

            session.verify = (
                False  # for convenience...  evaluate for yourself if this is acceptable.
            )

            r: Response = await session.request(
                method=method or "GET",
                url=url,
                data=data,
                json=json,
                params=params,
                timeout=30,
            )
            r.raise_for_status()
            return r.json()
        except HTTPStatusError as exc_status:
            if exc_status.response.status_code == 404:
                return None
            else:
                logger.exception(
                    f"HTTP Error: {exc_status=}:\n"
                    f"{exc_status.response.status_code=}\n"
                    f"{exc_status.request.url=}\n"
                )
                raise
        except HTTPError as exc_http:
            logger.exception(f"HTTP Error: {exc_http=}:\n" f"{exc_http.request.url=}\n")
            raise
        except Exception as exc:
            logger.exception(f"UNEXPECTED ERROR: {exc=}")
            raise


@timed_async_generator(log_progress=False, log_level=logging.DEBUG, logger=logger)
async def list_results_paginated(
    url: str,
    additional_params: Optional[dict] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    proxies: Optional[dict] = None,
) -> AsyncGenerator[dict, None]:
    should_continue: bool = True
    params: dict = {
        "page": 1,
    }
    if isinstance(additional_params, dict):
        params.update(additional_params)
    while should_continue:
        data_raw: dict = await get_response(
            method="GET",
            url=url,
            params=params,
            username=username,
            password=password,
            proxies=proxies,
        )
        results: list[dict] = get_value(src=data_raw, path=["results"], exp=list, default=[])
        if not results or not get_value(src=data_raw, path=["info", "next"], exp=str):
            should_continue = False
        params["page"] += 1
        for result in results:
            yield result


async def list_results(
    url: str,
    additional_params: Optional[dict] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    proxies: Optional[dict] = None,
    q: Optional[Queue] = None,
) -> None:
    params: dict = {}
    if isinstance(additional_params, dict):
        params.update(additional_params)
    data_raw: dict = await get_response(
        method="GET",
        url=url,
        params=params,
        username=username,
        password=password,
        proxies=proxies,
    )
    for result in get_value(src=data_raw, path=["results"], exp=list, default=[]):
        await q.put(result)


async def search_adap(
    url: str,
    search_filter: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    proxies: Optional[dict] = None,
    q: Optional[Queue] = None,
) -> None:
    """Search ADAP endpoint with LDAP filter and paginate results.

    Args:
        url: Base ADAP endpoint URL (e.g., https://server:port/adap)
        search_filter: LDAP search filter (e.g., "(cn=*)")
        username: Username for authentication
        password: Password for authentication
        proxies: Optional proxy configuration
        q: Queue to put results into
    """
    async for result in list_results_paginated(
        url=url,
        additional_params={"searchFilter": search_filter},
        username=username,
        password=password,
        proxies=proxies,
    ):
        if q:
            await q.put(result)
