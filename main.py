from threading import Timer
import tempfile
import subprocess
import time
import json
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path
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

from utils import AHK_PROCESS_PID_FILENAME


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

    def _run_ahk_file(self, ahk_filepath: str):
        """ Runs the ahk file. (Delete the file after running.)
        """
        subprocess.run(f'"{self.ahk_exe_filepath}" "{ahk_filepath}"')
        # 並於數秒後刪除腳本檔案
        Timer(5, Path(ahk_filepath).unlink, None).start()

    def run_ahk_script(self, ahk_script: str):
        """ 執行 AHK 腳本字串
        """
        # 產生臨時 AHK 腳本檔案
        ahk_file = tempfile.NamedTemporaryFile(
            prefix='ahk_script_', suffix='.ahk', delete=False
        )
        ahk_file = Path(ahk_file.name)
        ahk_file.write_text(ahk_script, encoding='utf-8-sig')

        # 執行腳本
        self._run_ahk_file(ahk_file)

    def _get_ahk_process_pid(self) -> Optional[int]:
        """ Get the pid of the ahk script.
        """
        ahk_process_pid_file = Path(
            tempfile.gettempdir()) / f'{AHK_PROCESS_PID_FILENAME}.txt'
        if ahk_process_pid_file.exists():
            return int(ahk_process_pid_file.read_text())
        return None

    def _kill_process_as_admin(self, pid: int):
        """ Kill the process as admin
        """
        # 生成一個具管理員權限的 AHK 腳本，並執行 [終止 PID 進程] 指令
        self.run_ahk_script(
            ahk_script="\n".join([
                "SwitchToAdmin()",
                f"Process, Close, {pid}",
                f"{app.AHK_FUNC_NAME_MAPPING_SCR_DICT['SwitchToAdmin']}"
            ]),
        )

    def stop_ahk_script(self):
        """ 停止 AHK 腳本
        """
        ahk_process_pid = self._get_ahk_process_pid()
        if ahk_process_pid:
            self._kill_process_as_admin(ahk_process_pid)


class App(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = Config.get()


# 建立 app 實例
app = App(
    title="ahkblockly - fastapi",
)

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
app.mount("/utils", StaticFiles(directory="utils"), name="utils")
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
        """ 執行腳本
        """
        # 終止先前的腳本
        app.config.stop_ahk_script()
        # 執行腳本
        app.config.run_ahk_script(self.ahkscr)


@app.post("/api/run_ahkscr")
async def run_ahkscr(ahkscrPost: RunAhkscrPost, background_tasks: BackgroundTasks):
    """ 執行 AHK 腳本字串
    """
    background_tasks.add_task(ahkscrPost.run)
    return


@app.get("/api/stop_ahkscr")
async def stop_ahkscr(background_tasks: BackgroundTasks):
    """ 停止 AHK 腳本
    """
    background_tasks.add_task(app.config.stop_ahk_script)
    return


@app.get("/api/ahk_funcs", response_model=List[str])
async def get_ahk_funcions():
    """ 獲取 AHK 函式名稱列表
    """
    return list(app.AHK_FUNC_NAME_MAPPING_SCR_DICT.keys())


@app.get('/api/ahk_funcs_script', response_model=str)
async def get_ahk_funcions_script(ahk_func_names: str):
    """ 獲取 AHK 函式腳本
    """
    # 根據提供的函式名稱列表獲取腳本字串
    ahk_func_name_set = set(ahk_func_names.split(','))
    ahk_func_script_list = [
        app.AHK_FUNC_NAME_MAPPING_SCR_DICT[func_name] for func_name in ahk_func_name_set
        if func_name in app.AHK_FUNC_NAME_MAPPING_SCR_DICT
    ]
    ahk_func_script = '\n\n'.join(ahk_func_script_list)

    # 分析函數列表的腳本內容，若有提到新的函式名稱，則添加到腳本列表中
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
