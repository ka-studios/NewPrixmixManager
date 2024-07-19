from fastapi import FastAPI, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from prisma import Prisma
import docker
import datetime
import random
import subprocess
import asyncio
import time
import json
import logging
import sys
from pathlib import Path
import uvicorn

config = Path("config.json")
if not config.is_file():
    logging.error("Please create a config.json file with your secret key")
    sys.exit(127)
with open("config.json") as c:
    data = c.read()
    global auth
    auth = json.loads(data).get('auth')

try:
    client = docker.from_env()
except docker.errors.DockerException:
    print("The Docker Daemon is not running.")
    sys.exit(1)

api = FastAPI()
limiter = Limiter(key_func=get_remote_address)

# stop containers after 2hr timeout (delay value added for future use with premium tier)
def stopaftertimeout(container_id, delay):
    time.sleep(delay)
    container = client.containers.get(container_id)             
    container.remove()

@api.post("/containers/create")
@limiter.limit("60/minute")
async def create_container(request: Request, response: Response) -> None:
    db = Prisma()
    await db.connect()
    data = await request.json()
    novnc = random.randint(49153, 65560)
    vnc = random.randint(49153, 65550)
    premium = data.get('premium', None)
    recv_url = data.get('url')
    username = data.get('user')
    while novnc == vnc:
        vnc = random.randint(49153, 65550)  # ensure novnc port and vnc port do not conflict
    if data.get('auth') == auth:  # change this pls
        if 'premium' in data:
            if premium == 1:
                ram = 1024
            elif premium == 2:
                ram = 2048
            elif premium == 3:
                ram = 4096
            else:
                ram = 768
        else:
            ram = 768
        if premium is None: premium = 0
        container = client.containers.run("newprixmix", ports={6080:novnc, 5904:vnc}, detach=True, mem_limit=f"{ram}m", environment={"URL":recv_url})
        await db.container.create(
            {
                'cid': container.id,
                'expires': datetime.datetime.now() + datetime.timedelta(hours=premium+2),
                'ram': ram,
                'novnc': novnc,
                'bearer': username,
                'vnc': vnc,
                'prem': False if premium == 0 else True,
            }
        )
        payload = {
            "container":container.id,
            "novnc_port":novnc    
        }
        return payload
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status": "auth token invalid"}

@api.post("/containers/destroy")
@limiter.limit("60/minute")
async def destroy_container(request: Request, response: Response):
    data = await request.json()
    container_id = data.get('id')
    if data.get('auth') == auth:  # check auth
        try:
            container = client.containers.get(container_id)
            container.stop()  # self explanatory
            db = Prisma()
            await db.connect()
            await db.container.delete(where={'cid':container_id})
        except docker.errors.APIError:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"status": "container not found"}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status": "auth token invalid"}

@api.post("/containers/suspend")
@limiter.limit("60/minute")
async def suspend_container(request: Request, response: Response):
    data = await request.json()
    container_id = data.get('id')
    if data.get('auth') == auth:  # check auth
        try:
            container = client.containers.get(container_id)
            container.pause()  # self explanatory
        except docker.errors.APIError:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"status": "container not found"}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status": "auth token invalid"}

@api.post("/containers/resume")
@limiter.limit("60/minute")
async def resume_container(request: Request, response: Response):
    data = await request.json()
    container_id = data.get('id')
    if data.get('auth') == auth:  # check auth
        try:
            container = client.containers.get(container_id)
            container.unpause()  # self explanatory
        except docker.errors.APIError:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"status": "container not found"}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status": "auth token invalid"}

@api.post("/containers/killall")
@limiter.limit("60/minute")
async def killall_containers(request: Request, response: Response):
    data = await request.json()
    if data.get('auth') == "superdupersecret":  # Spooky!
        db = Prisma()
        await db.connect()
        await db.container.delete_many(where={'prem':False})
        await db.container.delete_many(where={'prem':True})
        subprocess.call(["systemctl", "stop", "docker"])  # not going to use the sdk for this one
        subprocess.call(["systemctl", "stop", "containerd"])  # just in case
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status": "not slick"}  # ehehehe

@api.get("/_healthcheck")
@limiter.limit("60/minute")
async def healthcheck(response: Response, request: Request):
    response.status_code = status.HTTP_200_OK
    return Response("OK")

@api.post("/_authcheck")
@limiter.limit("60/minute")
async def authcheck(response: Response, request: Request):
    data = await request.json()
    if data.get('auth') == auth:
        response.status_code = status.HTTP_200_OK
        return Response("OK")
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return Response("Unauthorized")
@api.post("/prune")
@limiter.limit("3/minute")
async def pruneContainers(request: Request, response: Response):
    data = await request.json()
    if data.get('auth') == auth:
        db = Prisma()
        await db.connect()
        print("NP: Purging stale sessions")
        found = await db.container.find_many(where={'expires': {'lt': datetime.datetime.now()}})
        for container in found:
            try:
                c = client.containers.get(container.cid)
                c.remove()
                logging.info(f"Container {container.cid} removed successfully.")
            except docker.errors.DockerException as e:
                logging.error(f"Error removing container {container.cid}: {e}")
        await db.container.delete_many(where={'expires': {'lt': datetime.datetime.now()}})
        return Response("OK", status_code=200)
@api.post("/sessions")
async def get_sessions(request: Request, response: Response) -> None:
    data = await request.json()
    if data.get("auth") == auth:
        db = Prisma()
        await db.connect()
        user = data.get('user')
        result = await db.container.find_many(where={"bearer":user})
        return result
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status":"invalid auth token"}
if __name__ == "__main__":
    uvicorn.run(api, host="127.0.0.1", port=5546)
