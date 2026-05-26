from fastapi import APIRouter, Query
from database import get_connection

router = APIRouter()


@router.get("/funnel")
def get_funnel(
    device: str = Query(default="all"),
    location: str = Query(default="all"),
    source: str = Query(default="all"),
    age_group: str = Query(default="all"),
):
    conn = get_connection()

    where = []
    params = []
    if device != "all":
        where.append("u.device = ?")
        params.append(device)
    if location != "all":
        where.append("u.location = ?")
        params.append(location)
    if source != "all":
        where.append("u.source = ?")
        params.append(source)
    if age_group != "all":
        where.append("u.age_group = ?")
        params.append(age_group)

    user_filter = ("AND " + " AND ".join(where)) if where else ""

    total = conn.execute(
        f"SELECT COUNT(DISTINCT u.user_id) as cnt FROM users u WHERE 1=1 {user_filter}",
        params
    ).fetchone()["cnt"]

    def count_step(step):
        return conn.execute(
            f"""SELECT COUNT(DISTINCT e.user_id) as cnt
                FROM funnel_events e
                JOIN users u ON e.user_id = u.user_id
                WHERE e.step = ? {user_filter}""",
            [step] + params
        ).fetchone()["cnt"]

    def avg_time(step):
        return conn.execute(
            f"""SELECT ROUND(AVG(e.time_spent_s), 1) as avg
                FROM funnel_events e
                JOIN users u ON e.user_id = u.user_id
                WHERE e.step = ? {user_filter}""",
            [step] + params
        ).fetchone()["avg"] or 0

    def pct(n, d):
        return round(n / d * 100, 1) if d > 0 else 0

    visits = total
    signups = count_step("signup")
    carts = count_step("add_to_cart")
    purchases = count_step("purchase")

    stages = [
        {
            "stage": "Visit",
            "users": visits,
            "pct_of_total": 100.0,
            "drop_pct": None,
            "avg_time_spent_s": avg_time("visit"),
        },
        {
            "stage": "Signup",
            "users": signups,
            "pct_of_total": pct(signups, visits),
            "drop_pct": pct(visits - signups, visits),
            "avg_time_spent_s": avg_time("signup"),
        },
        {
            "stage": "Add to cart",
            "users": carts,
            "pct_of_total": pct(carts, visits),
            "drop_pct": pct(signups - carts, signups),
            "avg_time_spent_s": avg_time("add_to_cart"),
        },
        {
            "stage": "Purchase",
            "users": purchases,
            "pct_of_total": pct(purchases, visits),
            "drop_pct": pct(carts - purchases, carts),
            "avg_time_spent_s": avg_time("purchase"),
        },
    ]

    conn.close()
    return {
        "filters": {
            "device": device,
            "location": location,
            "source": source,
            "age_group": age_group,
        },
        "stages": stages,
        "biggest_leakage": max(stages[1:], key=lambda s: s["drop_pct"] or 0)["stage"],
        "overall_conversion_pct": pct(purchases, visits),
    }
