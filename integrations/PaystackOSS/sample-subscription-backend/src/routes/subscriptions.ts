import 'dotenv/config';
import { Hono } from "hono";
import { db } from '../db.js';
import { zValidator } from '@hono/zod-validator';
import { SubscriptionCreate, SubscriptionDisable } from '../schema/index.js';
import { eq } from 'drizzle-orm';
import { subscriptionsTable } from '../db/schema/subscriptions.js';
import { plansTable } from '../db/schema/plans.js';
import { customersTable } from '../db/schema/customers.js';

const subscriptionsRouter = new Hono()

subscriptionsRouter.get("/", async (c) => {
  const subscriptions = await db.select().from(subscriptionsTable)

  return c.json({
    status: true,
    data: subscriptions,
  }, 200)
})

subscriptionsRouter.post("/",
  zValidator('json', SubscriptionCreate),
  async (c) => {
    const validateReq = c.req.valid('json')
    const api = await fetch(`${process.env.PAYSTACK_BASE_URL}/subscription`, {
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

    const {
      subscription_code,
      status,
      plan: planCode,
      customer: customerCode,
      email_token,
      next_payment_date
    } = data["data"]
    const plan = await db.select({ id: plansTable.id })
      .from(plansTable)
      .where(eq(plansTable.code, planCode))
    const customer = await db.select({ id: customersTable.id })
      .from(customersTable)
      .where(eq(customerCode.code, customerCode))

    const subscription = await db.insert(subscriptionsTable)
      .values({
        code: subscription_code,
        status: status,
        emailToken: email_token,
        plan: plan[0].id,
        customer: customer[0].id,
        nextPaymentDate: next_payment_date
      })
      .returning()

    return c.json({
      status: true,
      data: subscription[0]
    }, 201)
  }
)

subscriptionsRouter.post("/disable",
  zValidator('json', SubscriptionDisable),
  async (c) => {
    const validateReq = c.req.valid('json')
    const api = await fetch(`${process.env.PAYSTACK_BASE_URL}/subscription/disable`, {
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

    const subscription = await db.update(subscriptionsTable).set({
      status: "disabled"
    }).where(eq(subscriptionsTable.code, validateReq.code))
      .returning()

    return c.json({
      status: true,
      data: subscription[0]
    }, 200)
  }
)

subscriptionsRouter.post("/:code/manage/email", async (c) => {
    const code = c.req.param('code')
    const api = await fetch(`${process.env.PAYSTACK_BASE_URL}/subscription/${code}/manage/email`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.PAYSTACK_SECRET_KEY}`,
        'Content-Type': "application/json"
      }
    })

    const data = await api.json()

    if (!data["status"]) {
      return c.json({
        status: false,
        data: {}
      }, 500)
    }

    return c.json({data}, 200)
  }
)


export default subscriptionsRouter