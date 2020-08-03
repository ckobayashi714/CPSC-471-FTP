# CPSC 471 Project FTP Server

Implement simplified FTP Server and Client

## How to run, using 2 termial windows

Start Server

```
python serv.py 1234
```

Start Client

```
python cli.py localhost 1234
```

Send Commands to Server via Client

```
ls

get <filename>

put <filename>

exit
```