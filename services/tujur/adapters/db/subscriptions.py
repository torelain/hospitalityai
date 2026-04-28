from dataclasses import dataclass
from datetime import datetime

from psycopg_pool import ConnectionPool


@dataclass(frozen=True)
class GraphSubscription:
    subscription_id: str
    hotel_mailbox: str
    client_state: str


class GraphSubscriptionRepo:
    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def find_expiring_before(self, cutoff: datetime) -> list[GraphSubscription]:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT subscription_id, hotel_mailbox, client_state "
                "FROM graph_subscriptions WHERE expires_at < %s",
                (cutoff,),
            )
            return [GraphSubscription(*row) for row in cur.fetchall()]

    def update_expiry(self, subscription_id: str, expires_at: datetime) -> None:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE graph_subscriptions SET expires_at = %s WHERE subscription_id = %s",
                (expires_at, subscription_id),
            )

    def replace(
        self,
        old_id: str,
        new_id: str,
        mailbox: str,
        client_state: str,
        expires_at: datetime,
    ) -> None:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "DELETE FROM graph_subscriptions WHERE subscription_id = %s",
                (old_id,),
            )
            cur.execute(
                "INSERT INTO graph_subscriptions "
                "(subscription_id, hotel_mailbox, client_state, expires_at) "
                "VALUES (%s, %s, %s, %s)",
                (new_id, mailbox, client_state, expires_at),
            )
