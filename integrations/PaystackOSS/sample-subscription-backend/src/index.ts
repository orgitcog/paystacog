import { serve } from '@hono/node-server'
import { Hono } from 'hono'
import plansRouter from './routes/plans.js'
import { showRoutes } from 'hono/dev'
import transactionRouter from './routes/transaction.js'
import webhookRouter from './routes/webhooks.js'
import customersRouter from './routes/customer.js'
import subscriptionsRouter from './routes/subscriptions.js'

const app = new Hono()

app.get('/', (c) => {
  return c.text('Server running fine')
})

app.route("/plan", plansRouter)
app.route("/customer", customersRouter)
app.route("/transaction", transactionRouter)
app.route("/subscription", subscriptionsRouter)
app.route("/webhook", webhookRouter)

// To list all routes
showRoutes(app)

serve({
  fetch: app.fetch,
  port: 3030
}, (info) => {
  console.log(`Server is running on http://localhost:${info.port}`)
})
