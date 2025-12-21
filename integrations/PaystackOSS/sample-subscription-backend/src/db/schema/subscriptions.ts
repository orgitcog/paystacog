import { int, sqliteTable, text } from "drizzle-orm/sqlite-core";
import { customersTable } from "./customers.js";
import { plansTable } from "./plans.js";

export const subscriptionsTable = sqliteTable("subscriptions", {
  id: int().primaryKey({ autoIncrement: true }),
  code: text().notNull(),
  status: text().notNull(),
  plan: int().notNull().references(() => plansTable.id),
  customer: int().notNull().references(() => customersTable.id),
  emailToken: text().notNull(),
  nextPaymentDate: text().notNull()
});