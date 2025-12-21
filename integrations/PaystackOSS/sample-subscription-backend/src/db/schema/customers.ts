import { int, sqliteTable, text } from "drizzle-orm/sqlite-core";

export const customersTable = sqliteTable("customers", {
  id: int().primaryKey({ autoIncrement: true }),
  firstName: text().notNull(),
  lastName: text().notNull(),
  email: text().notNull().unique(),
  code: text().notNull().unique(),
});