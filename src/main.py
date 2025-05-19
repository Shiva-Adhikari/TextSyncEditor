# Built in Modules
import os
import asyncio
import logging

# Third party Module
import diff_match_patch
from websockets.asyncio.server import serve


logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s %(message)s'
)

root_path = os.path.abspath('data')
os.makedirs(root_path, exist_ok=True)
file_path = os.path.join(root_path, 'text.txt')
dmp = diff_match_patch.diff_match_patch()


async def main_py(websocket):
    current_text = ''
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            current_text = f.read()

    async def server_receive():
        nonlocal current_text
        async for message in websocket:
            try:
                logging.info(f'\nmessage: {message}\n\n')
                patches = dmp.patch_fromText(message)
                # creating an updated version. by changes of current and get updated
                updated_text, results = dmp.patch_apply(patches, current_text)
                logging.info(f'updated_text: {updated_text}')

                if all(results):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        logging.info(f'yo chai file ma basxa: {updated_text}')
                        f.write(updated_text)
                        current_text = updated_text
                else:
                    logging.warning('Some patch failed to apply')
            except Exception as e:
                logging.error(f'Failed to apply patch {e}')

    async def server_send():
        nonlocal current_text
        prev_text = ''
        while True:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    current_text = f.read()
            await asyncio.sleep(.5)
            if current_text != prev_text:
                # is used to compare both, which is added, removed or unchanged
                patches = dmp.patch_make(prev_text, current_text)
                patch_text = dmp.patch_toText(patches)
                logging.info(f'yo chai server bata client ma send gareko: {patch_text}')
                await websocket.send(patch_text)
                prev_text = current_text

    # gather is used to run function in parallel
    try:
        await asyncio.gather(server_send(), server_receive())
    except Exception as e:
        logging.error(f'Connection closed: {e}')
    finally:
        await websocket.close()


async def main():
    async with serve(main_py, 'localhost', 6789) as server:
        logging.info('Starting...')
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
