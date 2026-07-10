import pandas as pd
import random
from datetime import datetime, timedelta

# Fixed list of "employees" - keeps our fake company small and realistic
USERS = ["alice", "bob", "carol", "dave", "erin", "frank", "grace", "heidi"]

# A pool of "normal" IPs - each user mostly logs in from their own regular IP
NORMAL_IPS = {
    "alice": "192.168.1.10",
    "bob": "192.168.1.11",
    "carol": "192.168.1.12",
    "dave": "192.168.1.13",
    "erin": "192.168.1.14",
    "frank": "192.168.1.15",
    "grace": "192.168.1.16",
    "heidi": "192.168.1.17",
}

# Real public IPs from different countries, used only for injected attack patterns
ATTACK_IPS = ["8.8.8.8", "9.9.9.9", "1.1.1.1", "185.228.168.9", "103.86.96.100"]


def random_normal_timestamp(base_date):
    """Generates a random timestamp during normal working hours (8 AM - 7 PM)."""
    hour = random.randint(8, 19)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return base_date.replace(hour=hour, minute=minute, second=second)


def generate_normal_logs(num_rows, base_date):
    """
    Generates realistic 'normal' login behavior:
    mostly successful, from the user's usual IP, during working hours.
    """
    rows = []
    for _ in range(num_rows):
        user = random.choice(USERS)
        timestamp = random_normal_timestamp(base_date)
        # 95% success, 5% a single accidental failed attempt (typo realism)
        status = random.choices(["success", "failed"], weights=[95, 5])[0]

        rows.append({
            "timestamp": timestamp,
            "source_ip": NORMAL_IPS[user],
            "destination_ip": "10.0.0.5",
            "user": user,
            "action": "login",
            "status": status
        })
    return rows


def inject_brute_force_attack(base_date, target_user=None):
    """
    Generates a burst of failed logins (seconds apart) followed by a success -
    simulates a brute force attack.
    """
    user = target_user or random.choice(USERS)
    attacker_ip = random.choice(ATTACK_IPS)
    start_time = base_date.replace(hour=random.randint(0, 23), minute=random.randint(0, 59))

    rows = []
    num_failures = random.randint(4, 8)
    for i in range(num_failures):
        rows.append({
            "timestamp": start_time + timedelta(seconds=i * 5),
            "source_ip": attacker_ip,
            "destination_ip": "10.0.0.5",
            "user": user,
            "action": "login",
            "status": "failed"
        })
    # Final successful login - the attacker eventually guesses correctly
    rows.append({
        "timestamp": start_time + timedelta(seconds=num_failures * 5),
        "source_ip": attacker_ip,
        "destination_ip": "10.0.0.5",
        "user": user,
        "action": "login",
        "status": "success"
    })
    return rows


def inject_impossible_travel_attack(base_date, target_user=None):
    """
    Generates two successful logins from very different IPs, minutes apart -
    simulates a compromised account being used from two places at once.
    """
    user = target_user or random.choice(USERS)
    ip1, ip2 = random.sample(ATTACK_IPS, 2)
    start_time = base_date.replace(hour=random.randint(8, 19), minute=random.randint(0, 59))

    rows = [
        {
            "timestamp": start_time,
            "source_ip": ip1,
            "destination_ip": "10.0.0.5",
            "user": user,
            "action": "login",
            "status": "success"
        },
        {
            "timestamp": start_time + timedelta(minutes=random.randint(2, 8)),
            "source_ip": ip2,
            "destination_ip": "10.0.0.5",
            "user": user,
            "action": "login",
            "status": "success"
        }
    ]
    return rows


def generate_dataset(num_normal=300, num_brute_force_attacks=15, num_travel_attacks=15):
    """
    Builds the full synthetic dataset by combining normal behavior with
    injected attack patterns, then shuffling everything into realistic order.
    """
    base_date = datetime(2024, 1, 15)
    all_rows = []

    all_rows.extend(generate_normal_logs(num_normal, base_date))

    for _ in range(num_brute_force_attacks):
        all_rows.extend(inject_brute_force_attack(base_date))

    for _ in range(num_travel_attacks):
        all_rows.extend(inject_impossible_travel_attack(base_date))

    df = pd.DataFrame(all_rows)
    df = df.sort_values(by="timestamp").reset_index(drop=True)
    return df


if __name__ == "__main__":
    dataset = generate_dataset(num_normal=300, num_brute_force_attacks=15, num_travel_attacks=15)
    dataset.to_csv("data/raw/synthetic_logs.csv", index=False)
    print(f"Generated {len(dataset)} log rows.")
    print(dataset.head(10))
    print("\nStatus counts:")
    print(dataset["status"].value_counts())