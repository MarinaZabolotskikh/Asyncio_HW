from aiohttp import ClientSession
import asyncio
from datetime import datetime
from more_itertools import chunked
from db import engine, Session, Base, People

URL = 'https://swapi.dev/api/people'
CHUNK_SIZE = 10
NUMBER_OF_PERSONS = 82


async def chunked_async(async_iter, size):
    buffer = []
    while True:
        try:
            item = await async_iter.__anext__()
        except StopAsyncIteration:
            break
        buffer.append(item)
        if len(buffer) == size:
            yield buffer
            buffer = []


async def get_person(people_id: int, session: ClientSession):
    async with session.get(f'{URL}/{people_id}') as response:
        person = await response.json()
        return person


async def get_people():
    async with ClientSession as session:
        for id_chunk in chunked(range(1, NUMBER_OF_PERSONS), CHUNK_SIZE):
            coroutines = [get_person(people_id=i, session=session) for i in id_chunk]
            people_list = await asyncio.gather(*coroutines)
            for item in people_list:
                yield item


async def get_inside_url(url, key, session):
    async with session.get(f'{url}') as response:
        data = await response.json()
        return data[key]


async def get_inside_urls(urls, key, session):
    tasks = (asyncio.create_task(get_inside_url(url, key, session)) for url in urls)
    for task in tasks:
        yield await task


async def get_inside_data(urls, key, session):
    result_list = []
    async for item in get_inside_urls(urls, key, session):
        result_list.append(item)
    return ', '.join(result_list)


async def past_to_db(people_list):
    async with Session() as session:
        async with ClientSession() as session_inside:
            for person_json in people_list:
                homeworld_str = await get_inside_data([person_json['homeworld']], 'name', session_inside)
                films_str = await get_inside_data(person_json['films'], 'title', session_inside)
                species_str = await get_inside_data(person_json['species'], 'name', session_inside)
                starships_str = await get_inside_data(person_json['starships'], 'name', session_inside)
                vehicles_str = await get_inside_data(person_json['vehicles'], 'name', session_inside)
                newperson = People(
                    birth_year=person_json['birth_year'],
                    eye_color=person_json['eye_color'],
                    gender=person_json['gender'],
                    hair_color=person_json['hair_color'],
                    height=person_json['height'],
                    mass=person_json['mass'],
                    name=person_json['name'],
                    skin_color=person_json['skin_color'],
                    homeworld=homeworld_str,
                    films=films_str,
                    species=species_str,
                    starships=starships_str,
                    vehicles=vehicles_str,
                )
                session.add(newperson)
                await session.commit()


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()
    async for chunk in chunked_async(get_people(), CHUNK_SIZE):
        asyncio.create_task(past_to_db(chunk))
    tasks = set(asyncio.all_tasks()) - {asyncio.current_task()}
    for task in tasks:
        await task


if __name__ == '__main__':
    start = datetime.now()
    asyncio.run(main())
    print(datetime.now() - start)
