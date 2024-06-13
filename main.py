from fastapi import FastAPI, Request, Response, status
import docker
import random
import subprocess

client = docker.from_env()
api = FastAPI()

@api.post("/containers/create")
async def create_container(request: Request, response: Response):
    host = request.client.host
    #if client !== "ip_here_later":
    #    response.status_code = status.HTTP_401_UNAUTHORIZED
    data = await request.json()
    novnc = random.randint(49153, 65560)
    vnc = random.randint(49153, 65550)
    while novnc = vnc:
      vnc = random.randint(49153, 65550)
    if data.get('auth') == "secretkey":
        container = client.containers.run("kasplusplus/newprixmix:1.0.1", ports={6080:novnc, 5904:vnc}, detach=True, mem_limit="512m")
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
        container = client.containers.get(container_id)
        container.stop()

    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status":"auth token invalid"}
@api.post("/containers/suspend")
async def suspend_container(request: Request, response: Response):
    data = await request.json()
    container_id = data.get('id')
    if data.get('auth') == "secretkey":
        container = client.containers.get(container_id)
        container.pause()
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status":"auth token invalid"}
@api.post("/containers/resume")
async def resume_container(request: Request, response: Response):
    data = await request.json()
    container_id = data.get('id')
    if data.get('auth') == "secretkey":
        container = client.containers.get(container_id)
        container.unpause()
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
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, port=5546)


