import 'dotenv/config';
import { Hono } from "hono";
import { db } from '../db.js';
import { zValidator } from '@hono/zod-validator';
import { Customer, CustomerUpdate } from '../schema/index.js';
import { eq } from 'drizzle-orm';
import { customersTable } from '../db/schema/customers.js';

const customersRouter = new Hono()

customersRouter.post("/insert", async (c) => {
  const data = await c.req.json()

  const {
    first_name,
    last_name,
    email,
    code
  } = data

  const customer = await db.insert(customersTable)
    .values({
      firstName: first_name,
      lastName: last_name,
      email: email,
      code: code
    })
    .returning()

  return c.json({
    status: true,
    data: customer[0]
  }, 201)
})

customersRouter.get("/", async (c) => {
  const customers = await db.select().from(customersTable)

  return c.json({
    status: true,
    data: customers,
  }, 200)
})

customersRouter.post("/",
  zValidator('json', Customer),
  async (c) => {
    const validateReq = c.req.valid('json')
    const api = await fetch(`${process.env.PAYSTACK_BASE_URL}/customer`, {
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
      first_name,
      last_name,
      email,
      customer_code
    } = data["data"]

    const customer = await db.insert(customersTable)
      .values({
        firstName: first_name,
        lastName: last_name,
        email: email,
        code: customer_code
      })
      .returning()

    return c.json({
      status: true,
      data: customer[0]
    }, 201)
  }
)

customersRouter.put("/:id",
  zValidator('json', CustomerUpdate),
  async (c) => {
    const validatedReq = c.req.valid('json')
    const id = c.req.param('id')

    const customer = await db.update(customersTable)
      .set({ ...validatedReq })
      .where(eq(customersTable.id, parseInt(id)))
      .returning();

    return c.json({
      status: true,
      data: customer[0]
    }, 200)
  }
)

export default customersRouter