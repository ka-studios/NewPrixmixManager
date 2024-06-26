# NewPrixmixManager

## Running

Install Dependencies:
```bash
pip3 install -r requirements.txt
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
You must start nginx with the provided nginx.conf before starting NPM.
Access noVNC on containers at `<server ip>/port/<novnc port number>/vnc.html`
#### Create Container:
`POST 127.0.0.1:5546/containers/create`<br>
**Parameters**:<br>
&nbsp;&nbsp;&nbsp;&nbsp;**auth** : authorization token ("secretkey" by default)<br>
**Returns:**<br>
&nbsp;&nbsp;&nbsp;&nbsp;**container** : the id of the created container<br>
&nbsp;&nbsp;&nbsp;&nbsp;**novnc_port** : the port that novnc is running on (random from 49153-65560)<br>
&nbsp;&nbsp;&nbsp;&nbsp;**vnc_port** : port that the vnc server is running on (random from 49153-65560)<br>
**Note** : default VNC password is "pxmxpwd0". pass ?password=pxmxpwd0 to novnc url to automatically authenticate
#### Destroy Container:<br>
`POST 127.0.0.1:5546/containers/destroy`<br>
**Parameters**:<br>
&nbsp;&nbsp;&nbsp;&nbsp;**auth** : authorization token ("secretkey" by default)<br>
&nbsp;&nbsp;&nbsp;&nbsp;**id** : id of the container to destroy<br>
#### Suspend Container:
`POST 127.0.0.1:5546/containers/suspend`<br>
**Parameters:**<br>
&nbsp;&nbsp;&nbsp;&nbsp;**auth** : authorization token ("secretkey" by default)<br>
&nbsp;&nbsp;&nbsp;&nbsp;**id** : id of the container to suspend<br>
#### Unsuspend Container:
`POST 127.0.0.1:5546/containers/resume`<br>
**Parameters:**<br>
&nbsp;&nbsp;&nbsp;&nbsp;**auth** : authorization token ("secretkey" by default)<br>
&nbsp;&nbsp;&nbsp;&nbsp;**id** : id of the container to unsuspend<br>
#### Stop all Containers:
`POST 127.0.0.1:5546/containers/resume`<br>
**Parameters:**<br>
&nbsp;&nbsp;&nbsp;&nbsp;**auth** : authorization token ("superdupersecret" by default)<br>

---
Made with ❤️ by KAS and Charmunk
