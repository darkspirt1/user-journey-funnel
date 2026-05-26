import sqlite3
import random
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/funnel.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     TEXT PRIMARY KEY,
            signed_up   TEXT NOT NULL,
            device      TEXT NOT NULL,
            location    TEXT NOT NULL,
            source      TEXT NOT NULL,
            age_group   TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS funnel_events (
            event_id    TEXT PRIMARY KEY,
            user_id     TEXT NOT NULL,
            step        TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            time_spent_s INTEGER NOT NULL
        );
    """)
    conn.commit()


def seed_data(conn):
    random.seed(99)

    DEVICES = ["mobile"] * 60 + ["desktop"] * 40
    LOCATIONS = ["IN"] * 45 + ["US"] * 25 + ["EU"] * 20 + ["APAC"] * 10
    SOURCES = ["organic"] * 40 + ["paid"] * \
        30 + ["referral"] * 20 + ["social"] * 10
    AGE_GROUPS = ["18-24"] * 30 + ["25-34"] * \
        35 + ["35-44"] * 20 + ["45+"] * 15

    # Drop-off rates by device
    SIGNUP_RATE = {"mobile": 0.42, "desktop": 0.74}
    CART_RATE = {"mobile": 0.40, "desktop": 0.62}
    PURCHASE_RATE = {"mobile": 0.10, "desktop": 0.16}

    # Time spent at each step in seconds
    TIME_SPENT = {
        "visit":       (10, 120),
        "signup":      (30, 240),
        "add_to_cart": (20, 180),
        "purchase":    (30, 300),
    }

    base_date = datetime.now() - timedelta(days=60)

    users, events = [], []

    for uid in range(1, 5001):
        user_id = f"u{uid:05d}"
        device = random.choice(DEVICES)
        location = random.choice(LOCATIONS)
        source = random.choice(SOURCES)
        age_group = random.choice(AGE_GROUPS)

        day_offset = int(random.betavariate(1.5, 1.0) * 60)
        signup_dt = base_date + timedelta(
            days=day_offset,
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        users.append((user_id, signup_dt.isoformat(),
                     device, location, source, age_group))

        # Visit — always happens
        ev_dt = signup_dt
        events.append((
            f"e{uid:05d}v", user_id, "visit",
            ev_dt.isoformat(),
            random.randint(*TIME_SPENT["visit"])
        ))

        # Signup
        if random.random() < SIGNUP_RATE[device]:
            ev_dt = ev_dt + timedelta(seconds=random.randint(30, 120))
            events.append((
                f"e{uid:05d}sg", user_id, "signup",
                ev_dt.isoformat(),
                random.randint(*TIME_SPENT["signup"])
            ))

            # Add to cart
            if random.random() < CART_RATE[device]:
                ev_dt = ev_dt + timedelta(seconds=random.randint(60, 300))
                events.append((
                    f"e{uid:05d}ac", user_id, "add_to_cart",
                    ev_dt.isoformat(),
                    random.randint(*TIME_SPENT["add_to_cart"])
                ))

                # Purchase
                if random.random() < PURCHASE_RATE[device]:
                    ev_dt = ev_dt + timedelta(seconds=random.randint(30, 180))
                    events.append((
                        f"e{uid:05d}pu", user_id, "purchase",
                        ev_dt.isoformat(),
                        random.randint(*TIME_SPENT["purchase"])
                    ))

    conn.executemany("INSERT OR IGNORE INTO users VALUES (?,?,?,?,?,?)", users)
    conn.executemany(
        "INSERT OR IGNORE INTO funnel_events VALUES (?,?,?,?,?)", events)
    conn.commit()

    print(f"Seeded: {len(users)} users | {len(events)} events")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    create_tables(conn)

    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count == 0:
        seed_data(conn)
    else:
        print(f"DB already has {count} users — skipping seed.")
    conn.close()


if __name__ == "__main__":
    init_db()
