import json
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
        """
        Runs the ahk file.
        """
        import subprocess
        subprocess.run(f'"{self.ahk_exe_filepath}" "{ahk_filepath}"')

    def run_ahk_script(self, ahk_script: str):
        """
        執行 AHK 腳本字串: 先下載檔案，再執行腳本
        """
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_filepath = Path(tmpdir) / 'ahk_script.ahk'
            tmp_filepath.write_text(ahk_script)
            self.run_ahk_file(tmp_filepath)


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
