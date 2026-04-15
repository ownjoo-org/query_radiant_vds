import argparse
import json
import logging
from asyncio import run
from sys import stderr
from typing import Optional

from query_radiant_vds.oj_toolkit.logging.consts import LOG_FORMAT
from query_radiant_vds.oj_toolkit.parsing.consts import TimeFormats

from query_radiant_vds.main import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--username",
        type=str,
        required=True,
        help="Username for authentication",
    )
    parser.add_argument(
        "--password",
        type=str,
        required=True,
        help="Password for authentication",
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="RadiantOne server URL with FQDN or IP address (ie. http://localhost)",
    )
    parser.add_argument(
        "--base-dn",
        type=str,
        required=True,
        help="Base DN",
    )
    parser.add_argument(
        "--port",
        type=int,
        required=False,
        default=8080,
        help="ADAP endpoint port (default: 8080)",
    )
    parser.add_argument(
        "--search-filter",
        type=str,
        required=True,
        help='LDAP search filter (e.g., "(cn=*)" or "(objectClass=*)")',
        dest="search_filter",
    )
    parser.add_argument(
        "--attributes",
        type=str,
        required=False,
        help="Comma-separated attributes to return (default: all)",
    )
    parser.add_argument(
        "--scope",
        type=str,
        required=False,
        default="sub",
        help="Search scope: base, one, sub (default: sub)",
    )
    parser.add_argument(
        "--context",
        type=str,
        required=False,
        help="Search context (default: all)",
    )
    parser.add_argument(
        "--return-mode",
        type=str,
        required=False,
        help="Return mode for results",
        dest="return_mode",
    )
    parser.add_argument(
        "--result-limit",
        type=int,
        required=False,
        default=0,
        help="Max results to return (0 = all results, default: 0)",
        dest="result_limit",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        required=False,
        default=100,
        help="Results per page for pagination (default: 100)",
        dest="page_size",
    )
    parser.add_argument(
        "--proxies",
        type=str,
        required=False,
        help="JSON structure specifying 'http' and 'https' proxy URLs",
    )
    parser.add_argument(
        "--log-level",
        type=int,
        required=False,
        help="0 (NOTSET) - 50 (CRITICAL)",
        default=logging.INFO,
        dest="log_level",
    )

    args = parser.parse_args()

    logging.basicConfig(
        format=LOG_FORMAT,
        level=args.log_level,
        datefmt=TimeFormats.DATE_AND_TIME.value,
        stream=stderr,
    )
    logger = logging.getLogger(__name__)

    proxies: Optional[dict] = None
    if args.proxies:
        try:
            proxies: dict = json.loads(args.proxies)
        except Exception as exc_json:
            logger.warning(f"failure parsing proxies: {exc_json}: proxies provided: {args.proxies}")

    run(
        main(
            url=args.url,
            port=args.port,
            base_dn=args.base_dn,
            search_filter=args.search_filter,
            attributes=args.attributes,
            scope=args.scope,
            context=args.context,
            return_mode=args.return_mode,
            result_limit=args.result_limit,
            page_size=args.page_size,
            username=args.username,
            password=args.password,
            proxies=proxies,
        )
    )
