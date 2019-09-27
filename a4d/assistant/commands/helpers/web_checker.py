import aiohttp
import asyncio
from aiohttp.client_exceptions import InvalidURL


async def fetch(session, url):

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


async def fetch_all(session, urls, client):

    # if only one url of type str else it's a list of urls
    if type(urls) == str:
        results = await fetch(session, urls)
    else:
        results = await asyncio.gather(*[client.loop.create_task(fetch(session, url)) for url in urls])

    return results


async def get_content(urls, client):
    """ Get content of a website.

    Note
    ----
    Works with list of websites. Websites in message must be split with any whitespace.

    References
    ----------
    https://aiohttp.readthedocs.io/en/stable/client_reference.html
    https://stackoverflow.com/questions/35879769/fetching-multiple-urls-with-aiohttp-in-python-3-5
    https://faust.readthedocs.io/en/latest/_modules/aiohttp/client.html

    Returns
    -------
    List of html of each url.

    """
    async with aiohttp.ClientSession() as session:
        htmls = await fetch_all(session, urls, client)
        return htmls
