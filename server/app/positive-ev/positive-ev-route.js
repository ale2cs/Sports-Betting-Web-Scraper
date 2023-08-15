import express from "express";
import { 
    positiveEV,
    socketConnectionRequest,
    publishMessageToConnectedSockets,
} from './positive-ev-controller.js'

const router = express.Router();

router.get('/send-message-to-client', (req, res, next) => {
    publishMessageToConnectedSockets(`Data: ${new Date()}`)
    res.sendStatus(200)
});

router.get('/socket-connection-request', socketConnectionRequest);

router.get("/positive-ev", async (req, res) => {
  try {
    const positiveLines = await positiveEV();
    res.json(positiveLines);
  } catch (error) {
    res.status(500).json({
      message: "Something went wrong",
    });
  }
});

export default router;