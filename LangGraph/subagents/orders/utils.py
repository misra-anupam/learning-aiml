from uuid import uuid4

class TicketStore:
    async def create_ticket(self, thread_id: str, order, conversation, priority: str) -> str:
        ticket_id = str(uuid4())
        await self.db.execute(
            """INSERT INTO tickets (id, thread_id, order_id, status, priority, created_at)
               VALUES ($1, $2, $3, 'open', $4, now())""",
            ticket_id, thread_id, order.get("key") if order else None, priority,
        )
        return ticket_id