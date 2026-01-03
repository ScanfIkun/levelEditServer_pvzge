from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import uvicorn
import os,sys
# os.chdir(os.path.dirname(__file__)) 
# pyinstaller -F EditServer.py --add-data "resource:resource" --add-data "web:web" --exclude-module numpy


def get_static_path(relative_path):
    """获取静态文件路径"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class EditServer:
    RESOURCE_FILE = "./resource/modules.json"
    QUERY_DIR = "./resource/query"
    def __init__(self):
        self.target_dir=[]
        self.modules:dict={}
        self.query:dict={}
        self.read_json()
    def read_json(self):
        with open(get_static_path(self.RESOURCE_FILE), "r", encoding="utf-8") as f:
            self.modules = json.load(f)

        for file in os.listdir(get_static_path(self.QUERY_DIR)):#name = file[:-5]
            if file.endswith('.json'):
                with open(get_static_path(f"{self.QUERY_DIR}/{file}"), "r", encoding="utf-8") as f:
                    self.query[file[:-5]]=json.load(f)

    def get_query(self,path):
        p=path.split('/')
        if p[0] in self.query: # 在文件中能够查询到
            res={"string":[]}
            target=self.query[p[0]]["objdata"]
            for i in p[1:]:
                if i.isdigit(): i=0
                try:
                    target=target[i]
                except:
                    return {}
            #print(target)
            if isinstance(target, str): # 如果是字符串
                ls=self.query[p[0]].get(target) # 获取id对应的列表
                for i in ls:
                    if result:=self.extract_parts(i):
                        left, right=result
                        #print(left,right)
                        if m:=self.modules.get(right):
                            if c:=m.get(left):
                                for j in c:
                                    res.setdefault(left, []).append(f"RTID({j}@{right})")
                        elif right=="CurrentLevel":
                            res.setdefault("CurrentLevel", []).append(f"class:{left} from CurrentLevel")
                    else:
                        res["string"].append(i)
            else:
                res={"string":[target]}
            return res
        else:
            return {}
        return {"classname":["shrinkingviolet","[PLAYERS_TRIP_TO_PIRATE_SHIP]","<DangerRoomModuleProperties@CurrentLevel>",'<ZombossVictoryOutroProperties@LevelModules>']}
    
    def get_module(self,module_id):
        if module_id not in self.modules:
            return {"message": f"模块{module_id}不存在"}
        return self.modules[module_id]
    
    def extract_parts(self,s: str) -> bool:
        """如果是<...@...>形式，返回左右两边的字符串"""
        if len(s) < 5:  # 最小形式是<a@b>，长度至少5
            return None
        if s[0] != '<' or s[-1] != '>':
            return None
        inner = s[1:-1]  # 去掉尖括号
        if '@' not in inner:
            return None
        parts = inner.split('@', 1)  # 最多分割一次
        if len(parts) != 2:
            return None
        left, right = parts
        if len(left) == 0 or len(right) == 0:
            return None
        return left, right



app=FastAPI()
app.mount("/assets", StaticFiles(directory=get_static_path("web/assets")))# 挂载静态文件

es=EditServer()
# 前端路由（返回 index.html）
@app.get("/")
async def index():
    return FileResponse(get_static_path("web/index.html"))

# 处理 SPA 路由
# @app.get("/{full_path:path}")
# async def catch_all(full_path: str):
#     return FileResponse("dist/index.html")

@app.get("/api/query")
async def get_query(path: str):
    #print(es.get_query(path))
    return es.get_query(path)

@app.get("/api/modules/{module_id}")
async def get_module(module_id:str):
    return es.get_module(module_id)


if __name__ == "__main__":
    #uvicorn.run("EditServer:app", host="127.0.0.1", port=9966, reload=True)
    #print(get_static_path("web/index.html"))
    uvicorn.run(app, host="127.0.0.1", port=9966)