import logging
from asyncio import Queue, gather
from typing import Coroutine, List, Optional

from template_cli.client import search_adap
from template_cli.parser import json_out

logger = logging.getLogger(__name__)


async def main(
    domain: str,
    port: int,
    search_filter: str,
    username: str,
    password: str,
    proxies: Optional[dict] = None,
) -> None:
    """Orchestrate ADAP search and JSON output.

    Args:
        domain: RadiantOne server FQDN or IP
        port: ADAP endpoint port
        search_filter: LDAP search filter
        username: Authentication username
        password: Authentication password
        proxies: Optional proxy configuration
    """
    adap_url = f"https://{domain}:{port}/adap"
    q = Queue(maxsize=100)
    client_coroutines: List[Coroutine] = [
        search_adap(
            url=adap_url,
            search_filter=search_filter,
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
