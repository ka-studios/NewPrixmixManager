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

# stop containers after 2hr timeout (delay value added for future use with premium tier)
def stopaftertimeout(container_id, delay):
    time.sleep(delay)
    container = client.containers.get(container_id)
    container.stop()

@api.post("/containers/create")
async def create_container(request: Request, response: Response):

    #if client !== "ip_here_later":
    #    response.status_code = status.HTTP_401_UNAUTHORIZED
    data = await request.json()
    novnc = random.randint(49153, 65560)
    vnc = random.randint(49153, 65550)
    while novnc == vnc:
      vnc = random.randint(49153, 65550) # make sure novnc port and vnc port do not conflict (yes its a 1/20000 chance but things happen sometimes)
    if data.get('auth') == "secretkey": # change this pls
        container = client.containers.run("newprixmix", ports={6080:novnc, 5904:vnc}, detach=True, mem_limit="512m") # mem limit 512 for now, will make it higher for premium
        stopthread = threading.Thread(target=stopaftertimeout, args=(container.id, 7200)) # make it timeout after 2hr (need to modify this for premium)
        stopthread.start()
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
    if data.get('auth') == "secretkey": # check auth
        try:
            container = client.containers.get(container_id)
            container.stop() # self explanatory
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
    if data.get('auth') == "secretkey": # check auth
        try:
            container = client.containers.get(container_id)
            container.pause() # self explanatory
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
    if data.get('auth') == "secretkey": # check auth
        try:
            container = client.containers.get(container_id)
            container.unpause() # self explanatory
        except docker.errors.APIError:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"status":"container not found"}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status":"auth token invalid"}
@api.post("/containers/killall")
async def killall_containers(request: Request, response: Response):
    data = await request.json()
    if data.get('auth') == "superdupersecret": # Spooky!
        subprocess.call(["systemctl", "stop", "docker"]) # not going to use the sdk for this one
        subprocess.call(["systemctl", "stop", "containerd"]) # just in case
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status":"not slick"} # ehehehe
async def stream_reader(stream, url_pattern):
    while True:
        line = await stream.readline() # stupid stream reader for zrok process
        if not line:
            break
        line = line.decode('utf-8').strip()
        urls = url_pattern.findall(line)
        for url in urls:
            yield url

async def terminate_process_after_delay(process, delay):
    await asyncio.sleep(delay)
    process.terminate()
    await process.wait()

@api.post("/containers/novnc_expose")
async def websockify_connect(request: Request, response: Response):
    try:
        data = await request.json()
    except:
        return {"status":"missing auth token"} # check auth
    if not data.get('port'):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status":"port missing from request"}
    if data.get('auth') == "secretkey": # check auth
        command = ["zrok", "share", "public", f"172.17.0.1:{data.get('port')}", "--headless"] # that ip BETTER not change randomly
        process = await asyncio.create_subprocess_exec(*command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        asyncio.create_task(terminate_process_after_delay(process, 7200))
        url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+') # very scuffed regex here

        async def read_output(stream):
            async for url in stream_reader(stream, url_pattern):
                return url

        stdout_task = asyncio.create_task(read_output(process.stdout))
        stderr_task = asyncio.create_task(read_output(process.stderr)) # use 2 threads becaus yes


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
    uvicorn.run(api, host="127.0.0.1", port=5546) # uvicorn>>>>>>>>




