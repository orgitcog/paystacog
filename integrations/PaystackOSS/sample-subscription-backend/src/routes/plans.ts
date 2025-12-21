import 'dotenv/config';
import { Hono } from "hono";
import { db } from '../db.js';
import { plansTable } from '../db/schema/plans.js';
import { zValidator } from '@hono/zod-validator';
import { PlanCreate, PlanUpdate } from '../schema/index.js';
import { eq } from 'drizzle-orm';

const plansRouter = new Hono()

plansRouter.get("/", async (c) => {
  const plans = await db.select().from(plansTable)

  return c.json({
    status: true,
    data: plans,
  }, 200)
})

plansRouter.post("/",
  zValidator('json', PlanCreate),
  async (c) => {
    const validateReq = c.req.valid('json')
    const api = await fetch(`${process.env.PAYSTACK_BASE_URL}/plan`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.PAYSTACK_SECRET_KEY}`,
        'Content-Type': "application/json"
      },
      body: JSON.stringify(validateReq)
    })

    const data = await api.json()

    if (!data["status"]) {
      return c.json({
        status: false,
        data: {}
      }, 500)
    }

    const plan = await db.insert(plansTable)
      .values({
        name: data["data"]["name"],
        amount: data["data"]["amount"],
        interval: data["data"]["interval"],
        code: data["data"]["plan_code"],
      })
      .returning()

    return c.json({
      status: true,
      data: plan[0]
    }, 201)
  })

plansRouter.put("/:id",
  zValidator('json', PlanUpdate),
  async (c) => {
    const validatedReq = c.req.valid('json')
    const id = c.req.param('id')
    const result = await db.select({ code: plansTable.code }).from(plansTable)
    const { code } = result[0]

    const api = await fetch(`${process.env.PAYSTACK_BASE_URL}/plan/${code}`, {
      method: "PUT",
      headers: {
        "Authorization": `Bearer ${process.env.PAYSTACK_SECRET_KEY}`,
        'Content-Type': "application/json"
      },
      body: JSON.stringify(validatedReq)
    })

    const data = await api.json()
    console.log("Data: ", data)

    if (!data["status"]) {
      return c.json({
        status: false,
        data: {}
      }, 500)
    }

    const plan = await db.update(plansTable)
      .set({ ...validatedReq })
      .where(eq(plansTable.id, parseInt(id)))
      .returning();

    return c.json({
      status: true,
      data: plan[0]
    }, 200)
  })

export default plansRouter