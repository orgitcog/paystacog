# sample-subscription-backend
A simple backend to serve as a reference when building subscription or recurring bill payment apps [with Paystack](https://paystack.com/). You can [check out the documentation](https://paystack.com/docs/payments/subscriptions/) to learn more.

## Tech stack
- [Hono](https://hono.dev/)
- SQLite
- [Drizzle ORM](https://orm.drizzle.team/)
- Paystack Subscription

## Set up
- Clone the repo:
  ```sh
  git clone git@github.com:PaystackOSS/sample-subscription-backend.git
  ```
- Install dependencies
  ```
  pnpm install
  ```
- Set up the DB
  ```sh
  pnpm db:apply
  ```
- Start server
  ```sh
  pnpm dev
  ```
- Test endpoints
  ```sh
  open http://localhost:3030
  ```

## Code structure
The code has a simple structure where all configuration files are in the top level and core logic resides on the `src` directory:
- `db`: Contains the DB schema
- `routes`: Each feature is categorised by routes that is then exported for usage in the main Hono class
- `schema`: Contains basic [Zod schema](https://zod.dev/) request validation