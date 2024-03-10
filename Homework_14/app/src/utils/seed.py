import sys
import random
import asyncio
import json
import platform

import aiohttp
import faker
from anyio import Path

SCRIPT_DIR = Path(__file__).parent
print(f"{SCRIPT_DIR=}")
sys.path.append(str(SCRIPT_DIR.parent))


try:
    from ..conf.config import settings
except ImportError:
    from ..conf.config import settings


ACCESS_TOKEN = ""

NUMBER_CONTACTS = 10


fake_data = faker.Faker("uk_UA")


async def get_fake_contacts():
    """
    Асинхронна функція для отримання випадкових контактів.

    Yields:
        List: Список випадкових даних контакту.
    """
    for _ in range(NUMBER_CONTACTS):
        yield [
            fake_data.first_name(),
            fake_data.last_name(),
            fake_data.email(),
            fake_data.phone_number(),
            fake_data.date(),
            fake_data.address(),
            random.choice([False, True])
        ]


async def send_data_to_api() -> None:
    """
    Асинхронна функція для відправки даних на API.
    """
    headers = {
        "content-type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    session = aiohttp.ClientSession()
    async for first_name, last_name, email, phone, birthday, address, favorite in get_fake_contacts():
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "birthday": birthday,
            "address": address,
            "favorite": favorite,
        }
        try:
            result = await session.post(
                f"http://{settings.app_host}:{settings.app_port}/api/contacts",
                headers=headers,
                data=json.dumps(data),
            )
            if result.status == 429:
                print(f"ERROR: {result.status=}, sleep")
                await asyncio.sleep(6)
                print()
            elif result.status != 201:
                print(
                    f"ERROR: {result.status=}, Try set token. Get token link "
                    f"http://{settings.app_host}:{settings.app_port}/api/auth/login"
                )
                break
        except aiohttp.ClientOSError as err:
            print(f"Connection error: {str(err)}")
            break
    await session.close()
    print("Done")


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(send_data_to_api())