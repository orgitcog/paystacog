import { int, sqliteTable, text } from "drizzle-orm/sqlite-core";

export const plansTable = sqliteTable("plans", {
  id: int().primaryKey({ autoIncrement: true }),
  name: text().notNull(),
  amount: int().notNull().default(0),
  interval: text().notNull(),
  code: text().notNull().unique(),
  description: text()
});