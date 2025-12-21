import { int, sqliteTable, text } from "drizzle-orm/sqlite-core";
import { plansTable } from "./plans.js";
import { customersTable } from "./customers.js";

export const transactionsTable = sqliteTable("transactions", {
  id: int().primaryKey({ autoIncrement: true }),
  amount: int().notNull().default(0),
  reference: text().notNull(),
  plan: int().references(() => plansTable.id),
  customer: int().references(() => customersTable.id),
});