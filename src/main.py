# Built in Modules
import os
import asyncio

# Third party Module
from websockets.asyncio.server import serve


root_path = os.path.abspath('src')
file_path = os.path.join(root_path, 'text.txt')


async def main_py(websocket):
    async def receive():
        async for message in websocket:
            with open(file_path, 'w') as file:
                file.write(message)

    async def send():
        last_text = ''
        while True:
            await asyncio.sleep(.5)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    text = f.read()
                    if text != last_text:
                        await websocket.send(text)
                        last_text = text

    # gather is used to run function in parallel
    await asyncio.gather(send(), receive())


async def main():
    async with serve(main_py, 'localhost', 6789) as server:
        print('Starting...')
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
