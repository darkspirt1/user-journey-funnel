from fastapi import APIRouter
from database import get_connection

router = APIRouter()


def pct(n, d):
    return round(n / d * 100, 1) if d > 0 else 0


@router.get("/insights")
def get_insights():
    conn = get_connection()

    # --- Step counts ---
    total = conn.execute(
        "SELECT COUNT(DISTINCT user_id) FROM users").fetchone()[0]

    def count_step(step):
        return conn.execute(
            "SELECT COUNT(DISTINCT user_id) FROM funnel_events WHERE step = ?", (step,)
        ).fetchone()[0]

    def avg_time(step):
        val = conn.execute(
            "SELECT ROUND(AVG(time_spent_s), 1) FROM funnel_events WHERE step = ?", (step,)
        ).fetchone()[0]
        return val if val is not None else 0

    def conversion_for(column, value):
        v = conn.execute(
            f"SELECT COUNT(DISTINCT user_id) FROM users WHERE {column} = ?", (
                value,)
        ).fetchone()[0]
        p = conn.execute(
            f"""SELECT COUNT(DISTINCT e.user_id)
                FROM funnel_events e
                JOIN users u ON e.user_id = u.user_id
                WHERE e.step = 'purchase' AND u.{column} = ?""", (value,)
        ).fetchone()[0]
        return pct(p, v)

    # --- Funnel counts ---
    visits = total
    signups = count_step("signup")
    carts = count_step("add_to_cart")
    purchases = count_step("purchase")

    # --- Drop-offs ---
    drops = {
        "Visit → Signup":           pct(visits - signups, visits),
        "Signup → Add to cart":     pct(signups - carts, signups),
        "Add to cart → Purchase":   pct(carts - purchases, carts),
    }
    biggest_drop = max(drops, key=drops.get)

    # --- Segment conversions ---
    device_conv = {
        "mobile":  conversion_for("device", "mobile"),
        "desktop": conversion_for("device", "desktop"),
    }
    source_conv = {
        "organic":  conversion_for("source", "organic"),
        "paid":     conversion_for("source", "paid"),
        "referral": conversion_for("source", "referral"),
        "social":   conversion_for("source", "social"),
    }
    location_conv = {
        "IN":   conversion_for("location", "IN"),
        "US":   conversion_for("location", "US"),
        "EU":   conversion_for("location", "EU"),
        "APAC": conversion_for("location", "APAC"),
    }

    # --- Avg time per step ---
    avg_times = {
        "visit":       avg_time("visit"),
        "signup":      avg_time("signup"),
        "add_to_cart": avg_time("add_to_cart"),
        "purchase":    avg_time("purchase"),
    }

    conn.close()

    # --- Recommendations ---
    best_source = max(source_conv, key=source_conv.get)
    worst_source = min(source_conv, key=source_conv.get)

    recommendations = [
        {
            "issue":  f"Biggest drop-off at '{biggest_drop}' — {drops[biggest_drop]}% of users lost",
            "fix":    "Simplify that step: reduce form fields, add progress indicators, show social proof.",
            "impact": "High",
        },
        {
            "issue":  f"Mobile conversion ({device_conv['mobile']}%) is far below desktop ({device_conv['desktop']}%)",
            "fix":    "Optimize mobile checkout: larger tap targets, fewer steps, autofill support.",
            "impact": "High",
        },
        {
            "issue":  f"Add to cart → Purchase drop-off is {drops['Add to cart → Purchase']}%",
            "fix":    "Add urgency (limited stock), offer discount at checkout, simplify payment options.",
            "impact": "High",
        },
        {
            "issue":  f"Best traffic source '{best_source}' converts at {source_conv[best_source]}%",
            "fix":    f"Increase budget and focus on '{best_source}' — it converts best.",
            "impact": "Medium",
        },
        {
            "issue":  f"Worst traffic source '{worst_source}' converts at only {source_conv[worst_source]}%",
            "fix":    "Re-evaluate landing pages for this source or pause low-ROI campaigns.",
            "impact": "Medium",
        },
    ]

    return {
        "summary": {
            "total_visitors":        visits,
            "total_purchases":       purchases,
            "overall_conversion_pct": pct(purchases, visits),
            "biggest_drop_stage":    biggest_drop,
            "biggest_drop_pct":      drops[biggest_drop],
        },
        "drop_offs":        drops,
        "device_conversion":   device_conv,
        "source_conversion":   source_conv,
        "location_conversion": location_conv,
        "avg_time_per_step":   avg_times,
        "recommendations":     recommendations,
    }
