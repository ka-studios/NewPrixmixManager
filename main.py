from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect, status
import docker
import random
import subprocess
import asyncio
import re
import time
import threading

client = docker.from_env()
api = FastAPI()

@api.post("/containers/create")
async def create_container(request: Request, response: Response):

    #if client !== "ip_here_later":
    #    response.status_code = status.HTTP_401_UNAUTHORIZED
    data = await request.json()
    novnc = random.randint(49153, 65560)
    vnc = random.randint(49153, 65550)
    while novnc == vnc:
      vnc = random.randint(49153, 65550)
    if data.get('auth') == "secretkey":
        container = client.containers.run("newprixmix", ports={6080:novnc, 5904:vnc}, detach=True, mem_limit="512m")
        return {
            "status":"success",
            "container":container.id,
            "novnc_port":novnc,
            "vnc_port":vnc
            }

    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status":"auth token invalid"}

@api.post("/containers/destroy")
async def destroy_container(request: Request, response: Response):
    #if client !== "ip_here_later":
    #    response.status_code = status.HTTP_401_UNAUTHORIZED
    data = await request.json()
    container_id = data.get('id')
    if data.get('auth') == "secretkey":
        try:
            container = client.containers.get(container_id)
            container.stop()
        except docker.errors.APIError:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"status":"container not found"}

    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status":"auth token invalid"}
@api.post("/containers/suspend")
async def suspend_container(request: Request, response: Response):
    data = await request.json()
    container_id = data.get('id')
    if data.get('auth') == "secretkey":
        try:
            container = client.containers.get(container_id)
            container.pause()
        except docker.errors.APIError:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"status":"container not found"}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status":"auth token invalid"}
@api.post("/containers/resume")
async def resume_container(request: Request, response: Response):
    data = await request.json()
    container_id = data.get('id')
    if data.get('auth') == "secretkey":
        try:
            container = client.containers.get(container_id)
            container.unpause()
        except docker.errors.APIError:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"status":"container not found"}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status":"auth token invalid"}
@api.post("/containers/killall")
async def killall_containers(request: Request, response: Response):
    data = await request.json()
    if data.get('auth') == "superdupersecret":
        subprocess.call(["systemctl", "stop", "docker"])
        subprocess.call(["systemctl", "stop", "containerd"])
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status":"not slick"}
async def stream_reader(stream, url_pattern):
    while True:
        line = await stream.readline()
        if not line:
            break
        line = line.decode('utf-8').strip()
        urls = url_pattern.findall(line)
        for url in urls:
            yield url

@api.post("/containers/novnc_expose")
async def websockify_connect(request: Request, response: Response):
    try:
        data = await request.json()
    except:
        return {"status":"missing auth token"}
    if not data.get('port'):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status":"port missing from request"}
    if data.get('auth') == "secretkey":
        command = ["zrok", "share", "public", f"172.17.0.1:{data.get('port')}", "--headless"]
        process = await asyncio.create_subprocess_exec(*command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')

        async def read_output(stream):
            async for url in stream_reader(stream, url_pattern):
                return url

        stdout_task = asyncio.create_task(read_output(process.stdout))
        stderr_task = asyncio.create_task(read_output(process.stderr))


        done, pending = await asyncio.wait([stdout_task, stderr_task], return_when=asyncio.FIRST_COMPLETED)


        for task in pending:
            task.cancel()


        url = next(iter(done)).result()

        return {"url": url}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status":"auth token invalid"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="127.0.0.1", port=5546)




