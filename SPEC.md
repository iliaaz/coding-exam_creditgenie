# Design spec

Customers need to see their past orders. The support team also needs to look up customer orders. Build something that works.

## Summary

We're building a simple API for requesting order history. Implement a minimal backend using sqllite that will store order data. Implement a toy API endpoint that will query the backend and return order data as expected.

Incoming requests will be have a user object that indicates a profile as either support agent or customer. 

Response should be filtered according to user requester profile

Customer users should see the following:
- Order status
- Price
- Number of objects
- Order time
- Delivery time

Support agents should see all data.

Data can only be accessed by an appropriate requester; verify user profile explicitly.
- A requester user can see data associated with their own orders only
- A requester support agent can see data associated with any orders

Requests will filter the expected output by following:
- customer id
- order id
- status
- order date
All parameters except customer id are option as part of the reuqest.

Responses will be paginated according to a default page size (50). Include a total number of pages and next and previous page token.

## Context

- Max number of users: 1000
- Max numer of orders per user: 5000
- Max date range of: 5 years

## Must haves

- [ ] API response according to submitted parameters and requester type
- [ ] API only responds with data of requesting user if user
- [ ] API responds with data of any user if requesting user is support agent
- [ ] Preload the database with customer order data for the sake of testing

## Won't do

- Any auth beyond requester profile check

## Scenarios

_Behaviour in GIVEN / WHEN / THEN form. Include positive and negative cases._

### Scenario: Happy path: Customer

- **GIVEN** A valid customer request
- **WHEN** _
- **THEN** Return a filtered set of that customer's data

### Scenario: Happy path: Agent

- **GIVEN** A valid agent request
- **WHEN** _
- **THEN** Return a filtered set of requested data

### Scenario: Invalid customer request

- **GIVEN** A customer requests another customer's data
- **WHEN** Upon request validation
- **THEN** Error is thrown that a customer has requested data they aren't allowed


## Acceptance criteria

- [ ] Output must reflect example in sample_output.json; you are free to expand upon it
- [ ] Customers can only access their own order data
- [ ] Support agents can access all order data

## Implementation notes

- Assume an authenticated, valid user
- Assume requester has a user profile 