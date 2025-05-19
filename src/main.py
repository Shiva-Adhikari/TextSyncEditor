# Built in Modules
import os
import asyncio
import logging

# Third party Module
from diff_match_patch import diff_match_patch
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, WebSocket, WebSocketDisconnect


app = FastAPI()

dmp = diff_match_patch()
logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

app.mount('/static', StaticFiles(directory='src'), name='static')

data_path = os.path.abspath('data')
os.makedirs(data_path, exist_ok=True)
file_path = os.path.join(data_path, 'text.txt')
src_path = os.path.abspath('src')
html_path = os.path.join(src_path, 'main.html')


@app.get('/')
async def get():
    with open(html_path, 'r', encoding='utf-8') as f:
        return HTMLResponse(content=f.read())


@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    current_text = ''

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            current_text = f.read()

    async def server_receive():
        nonlocal current_text
        while True:
            try:
                message = await websocket.receive_text()
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
            except WebSocketDisconnect:
                logging.info('Client disconnected')
            except Exception as e:
                logging.error(f'Failed to apply patch {e}')

    async def server_send():
        nonlocal current_text
        prev_text = ''
        try:
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
                    await websocket.send_text(patch_text)
                    prev_text = current_text
        except WebSocketDisconnect:
            logging.info('Client disconnected')
        except Exception as e:
            logging.error(f'Error while sending patch {e}')

    # gather is used to run function in parallel
    await asyncio.gather(server_send(), server_receive())
