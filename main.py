import time
import json
from typing import List
from pydantic import BaseModel
from loguru import logger
from fastapi import (
    FastAPI,
    Request,
    BackgroundTasks,
)
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic.types import FilePath

# from models import *
# from schema import *

from pathlib import Path


class Config(BaseModel):
    host: str = "127.0.0.1"
    port: int
    ahk_exe_filepath: FilePath

    def endpoint(self):
        return f"http://{self.host}:{self.port}"

    @classmethod
    def get(cls, json_path: Path = Path(__file__).parent / 'config.json'):
        """ 根據設定檔獲取實例
        """
        with open(json_path, encoding='utf-8') as f:
            return cls(**json.load(f))

    def run_ahk_file(self, ahk_filepath: str):
        """ Runs the ahk file.
        """
        import subprocess
        subprocess.run(f'"{self.ahk_exe_filepath}" "{ahk_filepath}"')

    def run_ahk_script(self, ahk_script: str):
        """ 執行 AHK 腳本字串: 先下載檔案，再執行腳本
        """
        import tempfile
        tmp_filepath = Path(tempfile.gettempdir()) / 'ahk_script.ahk'
        tmp_filepath.write_text(ahk_script, encoding='utf-8-sig')
        self.run_ahk_file(tmp_filepath)
        time.sleep(5)
        tmp_filepath.unlink()


# 建立 app 實例
app = FastAPI(
    title="ahkblockly - fastapi",
)
app.config = Config.get()

# 解決 CORS 問題
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 設定前端文件:靜態文件與HTML檔
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/pysrc", StaticFiles(directory="pysrc"), name="pysrc")
templates = Jinja2Templates(directory="templates")

# 設定 app 全域變數: AHK 函式名稱與腳本內容字典
ahk_func_dirpath = Path(__file__).parent / 'ahk_funcs'
app.AHK_FUNC_NAME_MAPPING_SCR_DICT = {
    f.stem: f.read_text('utf-8') for f in ahk_func_dirpath.glob('*.ahk')
}


@app.get("/", response_class=HTMLResponse, tags=['HTML頁面'])
async def root_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


class RunAhkscrPost(BaseModel):
    ahkscr: str

    def run(self):
        app.config.run_ahk_script(self.ahkscr)


@app.post("/api/run_ahkscr")
async def run_ahkscr(ahkscrPost: RunAhkscrPost, background_tasks: BackgroundTasks):
    """ 執行 AHK 腳本字串 """
    background_tasks.add_task(ahkscrPost.run)
    return


@app.get("/api/ahk_funcs", response_model=List[str])
async def get_ahk_funcions():
    """ 獲取 AHK 函式名稱列表 """
    return list(app.AHK_FUNC_NAME_MAPPING_SCR_DICT.keys())


@app.get('/api/ahk_funcs_script', response_model=str)
async def get_ahk_funcions_script(ahk_func_names: str):
    """ 獲取 AHK 函式腳本 """

    # 根據提供的函式名稱列表獲取腳本字串
    ahk_func_name_set = set(ahk_func_names.split(','))
    ahk_func_script_list = [
        app.AHK_FUNC_NAME_MAPPING_SCR_DICT[func_name] for func_name in ahk_func_name_set
        if func_name in app.AHK_FUNC_NAME_MAPPING_SCR_DICT
    ]
    ahk_func_script = '\n\n'.join(ahk_func_script_list)

    # 計算腳本列表提到的函式名稱數量，若有提到新的函式名稱，則添加到腳本列表中
    used_ahk_func_name_set = set(
        func_name for func_name in (await get_ahk_funcions())
        if f"{func_name}(" in ahk_func_script
    )
    if len(used_ahk_func_name_set) > len(ahk_func_name_set):
        return await get_ahk_funcions_script(','.join(used_ahk_func_name_set))

    return ahk_func_script


def main():
    import uvicorn
    import os

    #獲取本檔案檔名並運行伺服器 (fastapi)
    thisFileName_str = os.path.basename(__file__).replace('.py', '')

    logger.info(
        'docs url: ' +
        f"{app.config.endpoint().replace('0.0.0.0','127.0.0.1')}/docs"
    )

    # 執行服務
    uvicorn.run(
        f'{thisFileName_str}:app',
        host=app.config.host,
        port=app.config.port,
        # reload=True,
        debug=True,
    )


# 定義啟動方式
if __name__ == '__main__':
    main()

    # # app.config.run_ahk_file(R"C:\Users\Peter Wang\Desktop\00.ahk")
    # ahk_script = '''
    # Msgbox % "Hello World!!!123"
    # '''
    # app.config.run_ahk_script(ahk_script)
