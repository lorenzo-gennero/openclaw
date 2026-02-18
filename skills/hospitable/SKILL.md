---
name: hospitable
description: Manage Airbnb properties, reservations and check-ins via Hospitable API. Use when Lorenzo asks about properties, bookings, check-ins, check-outs or guests.
metadata:
  openclaw:
    emoji: 🏠
---

# Hospitable 🏠

Always use exec to run curl commands. Use double quotes.

## API calls

Get properties:
```bash
TOKEN=$(cat ~/.openclaw/workspace/hospitable_token.txt) && curl -sg "https://public.api.hospitable.com/v2/properties" -H "Authorization: Bearer $TOKEN" -H "Accept: application/json"
```

Get reservations:
```bash
TOKEN=$(cat ~/.openclaw/workspace/hospitable_token.txt) && curl -sg "https://public.api.hospitable.com/v2/reservations?properties%5B%5D=cd4bf5fb-16ef-49c8-b3db-93437e5f009f&properties%5B%5D=912db8e2-ef92-44fa-b257-6f843c87e520&properties%5B%5D=ec148f18-8c8a-456b-8bd9-b86e1c4086f9&properties%5B%5D=4cb5b686-ed1e-470c-90e8-e50500b0d77a&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD" -H "Authorization: Bearer $TOKEN" -H "Accept: application/json"
```

## Rules
- Replace YYYY-MM-DD with actual dates.
- Today is Wednesday, Feb 18th, 2026.
- Always confirm before sending guest messages.
- Parse JSON response and present cleanly. Host names for IDs: Milano (cd4...), Bardonecchia (912...), Drovetti (ec1...), Giacinto Collegno (4cb...).
