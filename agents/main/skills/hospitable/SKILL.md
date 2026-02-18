---
name: hospitable
description: Manage Airbnb properties, reservations, guest messages and calendar via the Hospitable API. Use this skill whenever Lorenzo asks about properties, bookings, check-ins, check-outs, guests, or wants to send messages to guests.
metadata:
  openclaw:
    emoji: 🏠
---

# Hospitable 🏠

Use the Hospitable API to answer questions about Lorenzo's properties and reservations.

Base URL: https://public.api.hospitable.com/v1
Auth header: Authorization: Bearer $HOSPITABLE_TOKEN

## Key endpoints
- GET /properties — list all properties
- GET /reservations?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD — get reservations
- GET /reservations/{id}/messages — get guest messages
- POST /reservations/{id}/messages — send message (always confirm with Lorenzo first)

## Rules
- Always confirm before sending any message to a guest
- Format dates as YYYY-MM-DD
- Use today's date dynamically for check-in/check-out queries
