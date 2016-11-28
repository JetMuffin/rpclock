# RPClock
A distributed application which generates and displays current time in several machines,
using remote process call mechanism.

## Prerequisites

- pip
- tornado

## Usage

Clone project and install dependencies.

```bash
git clone git@github.com:JetMuffin/rpclock.git
cd rpclock
sudu pip install -r requirements.txt
```

Run server.py on server node:

```bash
server.py -l <listen_host> -p <listen_port> -t [authentication_token]
```

Run client.py on client node:

```
client.py -l <remote_host> -p <remote_port> -t [authentication_token]
```

## License
Apache License