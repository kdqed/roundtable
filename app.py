import aiohttp
import aiohttp.web
import asyncio
import json
from members import member_dict
import traceback

members = {}

async def register(m, ws):
  if member_dict.get(m["id"])==m["key"]:
    ws.id = m["id"]
    members[m["id"]] = {"id": m["id"], "type": m["type"], "ws": ws}

async def member_list(m, ws):
  data = []
  for key in members:
    data.append({"id": members[key]["id"], "type": members[key]["type"]})
  await ws.send_str(json.dumps({"method": "members", "ref": m.get("ref"), "members": data}))

async def remove(ws):
  if ws.id and members.get(ws.id):
    del members[ws.id]

methods = {
  "register": register,
  "member_list": member_list
}

async def ws_handler(request):
  print('Websocket connection starting')
  ws = aiohttp.web.WebSocketResponse()
  await ws.prepare(request)
  ws.id = None
  print('Websocket connection ready')
  
  async for msg in ws:
    print(ws.id, msg)
    if msg.type == aiohttp.WSMsgType.TEXT:
      try:
        m = json.loads(msg.data)
        if m["method"] == 'close':
          await remove(ws)
          await ws.close()
        else:
          await methods[m["method"]](m, ws)
      except Exception as e:
        traceback.print_exc()
  print('Websocket connection closed')
  await remove(ws)
  return ws

app = aiohttp.web.Application()
app.add_routes([
  aiohttp.web.get('/ws', ws_handler),
])

if __name__=="__main__":
  aiohttp.web.run_app(app)
  
