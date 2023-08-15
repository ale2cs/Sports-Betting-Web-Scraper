import { getPositiveEV } from './positive-ev-model.js';

let clients = []

export async function positiveEV() {
  return await getPositiveEV()
}

export function socketConnectionRequest(req, res, next) {
    const headers = {
        'Content-Type': 'text/event-stream', // To tell client, it is an event stream
        'Connection': 'keep-alive', // To tell client not to close connection
        'Cache-Control': 'no-cache'
    };
    res.writeHead(200, headers);

    const clientId = Symbol(Date.now())

    const client = {
        clientId,
        res,
    }
    console.log(`New connection established:`, clientId)

    clients.push(client)
    publishMessageToConnectedSockets();

    req.on('close', () => {
        console.log(clientId, `Connection closed`)
        clients = clients.filter((client) => client.clientId !== clientId)
    })
}

export async function publishMessageToConnectedSockets(data) {
  const positive = await getPositiveEV()
  clients.forEach((client) => {
    const { res } = client
    res.write(`data: ${JSON.stringify(positive)}\n\n`);
  })
}

setInterval(() => {
  publishMessageToConnectedSockets();
}, 30000);