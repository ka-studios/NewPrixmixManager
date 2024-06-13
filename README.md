# NewPrixmixManager

## Running

Install Dependencies:
```bash
pip3 install fastapi docker
```
Build the docker image:
```bash
docker build -t newprixmix .
```
Run NewPrixmixManager:
```bash
python3 main.py
```

## Usage
NewPrixmixManager runs on port 5546.

#### Create Container:
`POST 127.0.0.1:5546/containers/create`<br>
Parameters:<br>
  **auth** : authorization token ("secretkey" by default)<br>
Returns:<br>
  **container** : the id of the created container<br>
  **novnc_port** : the port that novnc is running on (random from 49153-65560)<br>
  **vnc_port** : port that the vnc server is running on (random from 49153-65560)<br>
  **Note** : default VNC password is "pxmxpwd0". pass ?password=pxmxpwd0 to novnc url to automatically authenticate
#### Destroy Container:<br>
`POST 127.0.0.1:5546/containers/destroy`<br>
Parameters:<br>
  **auth** : authorization token ("secretkey" by default)<br>
  **id** : id of the container to destroy<br>
#### Suspend Container:
`POST 127.0.0.1:5546/containers/suspend`<br>
Parameters:<br>
  **auth** : authorization token ("secretkey" by default)<br>
  **id** : id of the container to suspend<br>
#### Unsuspend Container:
`POST 127.0.0.1:5546/containers/resume`<br>
Parameters:<br>
  **auth** : authorization token ("secretkey" by default)<br>
  **id** : id of the container to unsuspend<br>
#### Stop all Containers:
`POST 127.0.0.1:5546/containers/resume`<br>
Parameters:<br>
  **auth** : authorization token ("superdupersecret" by default)<br><br>

---
Created by KAS
