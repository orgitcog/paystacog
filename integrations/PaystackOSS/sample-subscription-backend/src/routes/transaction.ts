import 'dotenv/config';
import { Hono } from "hono";
import { zValidator } from '@hono/zod-validator';
import { Transaction } from '../schema/index.js';

const transactionRouter = new Hono()

transactionRouter.post("/initialize",
  zValidator('json', Transaction),
  async (c) => {
    const validateReq = c.req.valid('json')
    const api = await fetch(`${process.env.PAYSTACK_BASE_URL}/transaction/initialize`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.PAYSTACK_SECRET_KEY}`,
        'Content-Type': "application/json"
      },
      body: JSON.stringify(validateReq)
    })

    const response = await api.json()

    if (!response["status"]) {
      return c.json({
        status: false,
        data: {}
      }, 500)
    }

    return c.json({
      status: true,
      data: response
    }, 200)
  }
)


export default transactionRouter