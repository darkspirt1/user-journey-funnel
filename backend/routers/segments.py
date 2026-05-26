from fastapi import APIRouter
from database import get_connection

router = APIRouter()


def pct(n, d):
    return round(n / d * 100, 1) if d > 0 else 0


def get_funnel_for_segment(conn, column, value):
    total = conn.execute(
        f"SELECT COUNT(DISTINCT user_id) as cnt FROM users WHERE {column} = ?",
        (value,)
    ).fetchone()["cnt"]

    def count_step(step):
        return conn.execute(
            f"""SELECT COUNT(DISTINCT e.user_id) as cnt
                FROM funnel_events e
                JOIN users u ON e.user_id = u.user_id
                WHERE e.step = ? AND u.{column} = ?""",
            (step, value)
        ).fetchone()["cnt"]

    visits = total
    signups = count_step("signup")
    carts = count_step("add_to_cart")
    purchases = count_step("purchase")

    return {
        "segment": value,
        "visits": visits,
        "signups": signups,
        "carts": carts,
        "purchases": purchases,
        "signup_rate":   pct(signups, visits),
        "cart_rate":     pct(carts, signups),
        "purchase_rate": pct(purchases, carts),
        "overall_conversion": pct(purchases, visits),
    }


@router.get("/segments/device")
def segment_by_device():
    conn = get_connection()
    result = [get_funnel_for_segment(conn, "device", d)
              for d in ["mobile", "desktop"]]
    conn.close()
    return {"segments": result}


@router.get("/segments/location")
def segment_by_location():
    conn = get_connection()
    result = [get_funnel_for_segment(conn, "location", l) for l in [
        "IN", "US", "EU", "APAC"]]
    conn.close()
    return {"segments": result}


@router.get("/segments/source")
def segment_by_source():
    conn = get_connection()
    result = [get_funnel_for_segment(conn, "source", s) for s in [
        "organic", "paid", "referral", "social"]]
    conn.close()
    return {"segments": result}


@router.get("/segments/age")
def segment_by_age():
    conn = get_connection()
    result = [get_funnel_for_segment(conn, "age_group", a) for a in [
        "18-24", "25-34", "35-44", "45+"]]
    conn.close()
    return {"segments": result}
