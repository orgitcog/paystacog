import * as z from "zod";

/**
 * ======= Plan schemas =======
 */
export const PlanCreate = z.object({
  name: z.string(),
  amount: z.number(),
  interval: z.string(),
  description: z.boolean().optional()
})


export const PlanUpdate = z.object({
  name: z.string().optional(),
  amount: z.number().optional(),
  interval: z.string().optional(),
  update_existing_subscriptions: z.boolean().optional()
})

/**
 * ======= Transaction schemas =======
 */

export const Transaction = z.object({
  email: z.email(),
  amount: z.number(),
  plan: z.string()
})

/**
 * ======== Subscription schema ========
 */
export const SubscriptionCreate = z.object({
  customer: z.string(),
  plan: z.string(),
  start_date: z.date().optional()
})

export const SubscriptionDisable = z.object({
  code: z.string(),
  token: z.string()
})

/**
 * ========= Customer schema ========
 */

export const Customer = z.object({
  first_name: z.string(),
  last_name: z.string(),
  email: z.email(),
  code: z.string().optional()
})

export const CustomerUpdate = z.object({
  email: z.email().optional(),
  code: z.string().optional()
})