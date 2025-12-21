import 'dotenv/config';
import { Hono } from "hono";
import { db } from '../db.js';
import { createHmac } from 'node:crypto';
import { customersTable } from '../db/schema/customers.js';
import { eq } from 'drizzle-orm';
import { transactionsTable } from '../db/schema/transactions.js';
import { plansTable } from '../db/schema/plans.js';
import { subscriptionsTable } from '../db/schema/subscriptions.js';

const webhookRouter = new Hono()

async function handleChargeSuccess(data: any) {
  const { reference, amount, plan, customer } = data

  let planId: number | null = null
  let customerId: number | null = null
  let planDb: { id: number }[] = []
  let customerDb: { id: number }[] = []

  if ("plan_code" in plan) {
    planDb = await db.select({ id: plansTable.id })
      .from(plansTable)
      .where(eq(plansTable.code, plan["plan_code"]))
  }
  if ("customer_code" in customer) {
    customerDb = await db.select({ id: customersTable.id })
      .from(customersTable)
      .where(eq(customersTable.code, customer["customer_code"]))
  }

  if (planDb.length > 0) {
    planId = planDb[0].id
  }

  if (customerDb.length > 0) {
    customerId = customerDb[0].id
  }
  
  const transaction = await db.insert(transactionsTable)
    .values({ reference, amount, plan: planId, customer: customerId })
    .returning({ insertedId: transactionsTable.id })

  console.log("Transaction inserted successfully: ", transaction[0].insertedId)
}


async function handleSubscriptionCreate(data: any) {
  const { subscription_code, email_token, status, next_payment_date, plan, customer } = data

  const planDb = await db.select({ id: plansTable.id })
    .from(plansTable)
    .where(eq(plansTable.code, plan["plan_code"]))

  const customerDb = await db.select({ id: customersTable.id })
    .from(customersTable)
    .where(eq(customersTable.code, customer["customer_code"]))

  const subscriptionDb = await db.insert(subscriptionsTable)
    .values({
      code: subscription_code,
      status,
      emailToken: email_token,
      plan: planDb[0].id,
      customer: customerDb[0].id,
      nextPaymentDate: next_payment_date
    })
    .returning()

  console.log("Subscription inserted successfully: ", subscriptionDb[0])
}

async function handleSubscriptionDisable(data: any) {
  const { subscription_code, status, next_payment_date } = data

  const subscriptionDb = await db.update(subscriptionsTable).set({
    nextPaymentDate: next_payment_date,
    status
  }).where(eq(subscriptionsTable.code, subscription_code))
  .returning()

  console.log("Subscription disabled successfully: ", subscriptionDb[0])
}

webhookRouter.post("/", async (c) => {
  const secretKey = process.env.PAYSTACK_SECRET_KEY
  const body = await c.req.json()
  const hash = createHmac('sha512', secretKey!).update(JSON.stringify(body)).digest('hex')
  const signature = c.req.header('x-paystack-signature')

  if (hash !== signature) {
    return c.json({}, 200)
  }

  switch (body.event) {
    case "charge.success":

      handleChargeSuccess(body.data)
      break;
    case "subscription.create":
      // handle subscription creation
      handleSubscriptionCreate(body.data)
      break;
    case "invoice.create":
      // handle invoice creation
      console.log("In invoice.create")
      break;
    case "invoice.payment_failed":
      // handle invoice payment failure
      console.log("In invoice.payment_failed")
      break;
    case "invoice.update":
      // handle invoice update
      console.log("In invoice.update")
      break;
    case "subscription.disable":
      handleSubscriptionDisable(body.data)
      break;
    case "subscription.not_renew":
      // handle subscription not renewing
      console.log("In subscription.not_renew")
      break;
    default:
      break;
  }

  return c.json({}, 200)
})


export default webhookRouter