import logging
from asyncio import Queue, gather
from typing import Coroutine, List, Optional

from query_radiant_vds.client import search_adap
from query_radiant_vds.parser import json_out

logger = logging.getLogger(__name__)


async def main(
    url: str,
    port: int,
    base_dn: str,
    search_filter: str,
    username: str,
    password: str,
    attributes: Optional[str] = None,
    scope: str = "sub",
    context: Optional[str] = None,
    return_mode: Optional[str] = None,
    result_limit: int = 0,
    page_size: int = 100,
    proxies: Optional[dict] = None,
) -> None:
    """Orchestrate ADAP search and JSON output.

    Args:
        url: RadiantOne server FQDN or IP
        port: ADAP endpoint port
        base_dn: Base DN for ADAP search
        search_filter: LDAP search filter
        username: Authentication username
        password: Authentication password
        attributes: Comma-separated attributes to return (None = all)
        scope: Search scope (base, one, sub) - default "sub"
        context: Search context (None = all)
        return_mode: Return mode (None = default)
        result_limit: Max results to return (0 = no limit)
        page_size: Results per page
        proxies: Optional proxy configuration
    """
    adap_url = f"{url}:{port}/adap/{base_dn}"
    q = Queue(maxsize=100)
    client_coroutines: List[Coroutine] = [
        search_adap(
            url=adap_url,
            search_filter=search_filter,
            attributes=attributes,
            scope=scope,
            context=context,
            return_mode=return_mode,
            result_limit=result_limit,
            page_size=page_size,
            username=username,
            password=password,
            proxies=proxies,
            q=q,
        ),
    ]
    parser_coroutines: List[Coroutine] = [
        json_out(q=q),
    ]
    await gather(
        *client_coroutines,
        *parser_coroutines,
        q.join(),
    )
