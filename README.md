# Worminator

Worminator is a Twitch chat raffle bot for coaching raffles.

See [tests/README.md](tests/README.md) for test suites, commands, and developer testing guidance.

## Database Schema

### users
| Column | Type | Description |
|--------|------|---------|
| user_id | bigint | Primary key |
| username | charvar50 | Discord username |
| ticket_count | int | Amount of tickets |

### coach_sessions
| Column | Type | Description |
|---|---|---|
| session_id | integer | Primary key |
| user_id | bigint | Foreign key to users |
|