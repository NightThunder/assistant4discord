import aiohttp
import asyncio
from aiohttp.client_exceptions import InvalidURL, ContentTypeError


async def fetch(session, url, json):

    if json:
        try:
            async with session.get(url) as response:
                return await response.json()

        except ContentTypeError:
            return None

    else:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    response.raise_for_status()

                try:
                    return await response.text()        # string
                except UnicodeDecodeError:
                    return await response.read()        # bytes

        except InvalidURL:
            return None


async def fetch_all(session, urls, client, json):

    # if only one url of type str else it's a list of urls
    if type(urls) == str:
        results = await fetch(session, urls, json)
    else:
        results = await asyncio.gather(*[client.loop.create_task(fetch(session, url, json)) for url in urls])

    return results


async def get_content(urls, client, json=False):
    """ Get content of a website.

    Parameters
    ----------
    urls: str or list of str
        "http://..."
    client: obj
        Discord client object.
    json: bool
        True if website returns json format.

    Note
    ----
    Works with list of websites or with string. Websites in message must be split with any whitespace.

    References
    ----------
    https://aiohttp.readthedocs.io/en/stable/client_reference.html
    https://stackoverflow.com/questions/35879769/fetching-multiple-urls-with-aiohttp-in-python-3-5
    https://faust.readthedocs.io/en/latest/_modules/aiohttp/client.html
    https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientResponse.json

    Returns
    -------
    List of website html for each website or html string if single string input. If json returns dict.
    None if content type error or if invalid url.

    """
    async with aiohttp.ClientSession() as session:
        htmls = await fetch_all(session, urls, client, json)
        return htmls
