"""
Seed the PostgreSQL knowledge base with comprehensive troubleshooting data
for AC, Washing Machine, and Microwave Oven.

Run: python seed_db.py
"""
from database import SessionLocal, init_db
from models import KnowledgeItem, ProductType

KNOWLEDGE_DATA = [
    # ═══════════════════════════════════════════
    #  AIR CONDITIONER
    # ═══════════════════════════════════════════
    {
        "product": ProductType.ac,
        "intent": "not_cooling",
        "title": "AC Not Cooling Properly",
        "severity": "high",
        "keywords": ["not cooling", "nahi thanda", "warm air", "hot air", "thanda nahi", "cooling nahi", "not cold"],
        "content": "The AC is running but not producing cold air. Common causes include dirty filters, low refrigerant, blocked condenser, or thermostat issues.",
        "solution_steps": [
            "Check if the temperature setting is below room temperature (e.g., set to 22°C).",
            "Clean or replace the air filter — a clogged filter reduces cooling by 30%.",
            "Ensure all doors and windows are closed to avoid hot air entry.",
            "Check the outdoor unit — make sure nothing is blocking it.",
            "Set the mode to COOL (not FAN or DRY).",
            "If still not cooling after 10 minutes, the refrigerant may be low — please create a service ticket.",
        ],
    },
    {
        "product": ProductType.ac,
        "intent": "water_leakage",
        "title": "AC Water Leakage / Dripping",
        "severity": "medium",
        "keywords": ["water leak", "drip", "leaking", "paani aa raha", "water dripping", "wet floor"],
        "content": "Water dripping from the indoor unit is usually caused by a clogged drain pipe, frozen coil, or improper installation angle.",
        "solution_steps": [
            "Turn off the AC immediately to prevent electrical damage.",
            "Check the drain pipe for blockage — pour some water to test flow.",
            "Clean the drain tray using a small brush.",
            "Ensure the AC unit is tilted slightly backward (drain side lower).",
            "Wipe off existing water to prevent damage to walls/floor.",
            "If leakage continues, book a service — the drain pipe may need professional cleaning.",
        ],
    },
    {
        "product": ProductType.ac,
        "intent": "remote_not_working",
        "title": "AC Remote Control Not Working",
        "severity": "low",
        "keywords": ["remote", "remote not working", "controller", "not responding", "remote kaam nahi"],
        "content": "The remote control fails to operate the AC. Common causes: dead batteries, blocked IR sensor, or remote damage.",
        "solution_steps": [
            "Replace the remote batteries with fresh AA or AAA batteries.",
            "Point the remote directly at the AC's IR sensor (usually on the indoor unit).",
            "Clean the IR sensor on the AC with a dry cloth.",
            "Try operating the AC using the manual power button on the unit.",
            "Test the remote using your phone camera — press any button and check if the IR LED flashes on screen.",
            "If the remote is damaged, contact us for a replacement remote.",
        ],
    },
    {
        "product": ProductType.ac,
        "intent": "power_issue",
        "title": "AC Not Turning On",
        "severity": "high",
        "keywords": ["power", "not turning on", "not starting", "no power", "dead", "on nahi"],
        "content": "The AC does not respond when powered on. Could be a power supply issue, tripped breaker, or internal fault.",
        "solution_steps": [
            "Check if the power plug is firmly inserted into the socket.",
            "Check the circuit breaker/fuse box — the AC breaker may have tripped.",
            "Try plugging another device into the same socket to test it.",
            "Check if the power indicator light on the AC is on.",
            "Ensure the voltage supply is stable (ACs need 220V–240V).",
            "If none of the above work, there may be an internal electrical fault — please create a service ticket.",
        ],
    },
    {
        "product": ProductType.ac,
        "intent": "noise_issue",
        "title": "AC Making Unusual Noise",
        "severity": "medium",
        "keywords": ["noise", "sound", "noisy", "rattling", "vibration", "loud", "grinding"],
        "content": "Unusual sounds like rattling, grinding, or humming indicate loose parts, debris in the fan, or compressor issues.",
        "solution_steps": [
            "Check if the outdoor unit cover panels are loose — tighten screws if needed.",
            "Look for debris (leaves, twigs) caught in the outdoor unit fan.",
            "Check if the indoor unit is properly mounted on the wall bracket.",
            "Rattling sounds often mean loose internal parts — do not ignore.",
            "Grinding sounds from the compressor indicate serious motor issues — turn off and book service.",
        ],
    },
    {
        "product": ProductType.ac,
        "intent": "error_code",
        "title": "AC Displaying Error Code",
        "severity": "high",
        "keywords": ["error", "error code", "E1", "E2", "F1", "blinking", "flashing", "code"],
        "content": "Error codes displayed on the AC panel indicate specific faults. Most require professional service.",
        "solution_steps": [
            "Note down the exact error code shown (e.g., E1, E2, F3).",
            "E1 usually means indoor temperature sensor error.",
            "E2 usually means outdoor temperature sensor error.",
            "F1 or E3 often indicates refrigerant pressure issue.",
            "Try turning off the AC, waiting 5 minutes, then turning back on.",
            "If the error persists, share the code with our technician when creating a service ticket.",
        ],
    },

    # ═══════════════════════════════════════════
    #  WASHING MACHINE
    # ═══════════════════════════════════════════
    {
        "product": ProductType.washing_machine,
        "intent": "not_spinning",
        "title": "Washing Machine Not Spinning",
        "severity": "high",
        "keywords": ["not spinning", "spin nahi", "drum not moving", "not rotating", "spin problem"],
        "content": "The drum does not rotate during the spin cycle. Common causes: overloaded machine, unbalanced load, faulty motor, or lid/door sensor issue.",
        "solution_steps": [
            "Check if the machine is overloaded — reduce clothes to 70% capacity.",
            "Redistribute clothes evenly inside the drum to balance the load.",
            "Ensure the lid or door is fully closed and latched.",
            "Cancel the current cycle, drain water, and restart a fresh spin cycle.",
            "Check for small objects (coins, clips) stuck in the drum or filter.",
            "If the drum still doesn't spin, the motor or belt may be faulty — create a service ticket.",
        ],
    },
    {
        "product": ProductType.washing_machine,
        "intent": "not_draining",
        "title": "Washing Machine Not Draining Water",
        "severity": "high",
        "keywords": ["not draining", "drain nahi", "water not going", "stuck water", "paani nahi ja"],
        "content": "Water remains in the drum after the wash cycle. Usually caused by a blocked drain pump, kinked drain hose, or clogged filter.",
        "solution_steps": [
            "Check the drain hose at the back — ensure it is not kinked or blocked.",
            "Make sure the drain hose outlet is not submerged in water (should be 60–90cm above ground).",
            "Clean the drain pump filter (usually behind a small flap at the front bottom).",
            "Run a separate DRAIN or SPIN cycle.",
            "Check if the drain pipe is clogged using a torch.",
            "If water still won't drain, the pump motor may be faulty — please create a service ticket.",
        ],
    },
    {
        "product": ProductType.washing_machine,
        "intent": "door_lock_issue",
        "title": "Washing Machine Door Not Opening / Locked",
        "severity": "medium",
        "keywords": ["door", "door not opening", "door locked", "lock", "darwaza", "latch", "door lock"],
        "content": "The washing machine door remains locked after the cycle ends. Safety lock engaged or faulty door interlock.",
        "solution_steps": [
            "Wait 2–3 minutes after the cycle ends — the door auto-unlocks after cooling down.",
            "Check if there is still water in the drum — drain it first before the door can open.",
            "Turn the machine off, wait 5 minutes, then try the door again.",
            "Some models have a child lock — check if it's enabled and disable it.",
            "Look for an emergency release cord inside the filter access panel.",
            "If the door remains stuck, the door interlock may be faulty — create a service ticket.",
        ],
    },
    {
        "product": ProductType.washing_machine,
        "intent": "power_issue",
        "title": "Washing Machine Not Starting",
        "severity": "high",
        "keywords": ["power", "not starting", "not turning on", "on nahi", "dead", "no power", "start nahi"],
        "content": "Washing machine does not turn on or shows no response. Could be power supply or control board issue.",
        "solution_steps": [
            "Check if the power cord is firmly plugged in.",
            "Inspect the circuit breaker — washing machines often trip breakers due to high power draw.",
            "Make sure the door/lid is fully shut — machines won't start with an open door.",
            "Check if the child lock is activated and turn it off.",
            "Try a different power outlet.",
            "If there is still no response, the control board may be faulty — create a service ticket.",
        ],
    },
    {
        "product": ProductType.washing_machine,
        "intent": "noise_issue",
        "title": "Washing Machine Making Loud Noise",
        "severity": "medium",
        "keywords": ["noise", "sound", "loud", "vibration", "rattling", "banging", "awaz"],
        "content": "Loud banging, rattling or vibration during wash/spin cycles. Usually unbalanced load, leveling issue, or foreign objects.",
        "solution_steps": [
            "Check for coins, keys, or zippers inside the drum.",
            "Make sure the machine is on a flat, level surface — adjust the leveling feet.",
            "Redistribute the clothes evenly in the drum.",
            "Do not overload — max 80% capacity.",
            "Remove transportation bolts if this is a new installation.",
            "If noise is a grinding/metal sound, the drum bearing may be worn — create a service ticket.",
        ],
    },
    {
        "product": ProductType.washing_machine,
        "intent": "error_code",
        "title": "Washing Machine Error Code",
        "severity": "high",
        "keywords": ["error", "error code", "blinking", "E1", "E3", "F2", "code", "display error"],
        "content": "Error codes indicate specific machine faults detected by the control board.",
        "solution_steps": [
            "Note the exact error code shown on the display.",
            "E1/OE: Drainage error — check drain hose and pump filter.",
            "E2/UE: Unbalanced load — redistribute clothes.",
            "E3/DE: Door error — ensure door is fully closed.",
            "F4/TE: Temperature sensor issue — requires technician.",
            "Turn off and restart after 5 minutes. If error returns, create a service ticket.",
        ],
    },

    # ═══════════════════════════════════════════
    #  MICROWAVE OVEN
    # ═══════════════════════════════════════════
    {
        "product": ProductType.microwave,
        "intent": "not_heating",
        "title": "Microwave Not Heating Food",
        "severity": "high",
        "keywords": ["not heating", "garam nahi", "food not hot", "heat nahi", "microwave not working"],
        "content": "Microwave runs but food does not get heated. Could be a faulty magnetron, capacitor, or power issue.",
        "solution_steps": [
            "Check the power level setting — ensure it's not set to 0% or very low.",
            "Place a cup of water inside and run for 1 minute — if water heats up, the microwave is working.",
            "Ensure the door closes properly — a poor door seal stops heating for safety.",
            "Check if you are using microwave-safe containers (metal blocks heating).",
            "If the water doesn't heat up, the magnetron (heating element) may be faulty — create a service ticket.",
        ],
    },
    {
        "product": ProductType.microwave,
        "intent": "turntable_issue",
        "title": "Microwave Turntable Not Rotating",
        "severity": "medium",
        "keywords": ["turntable", "plate not rotating", "plate stuck", "rotating plate", "ghoomna", "tray"],
        "content": "The glass turntable plate does not rotate during operation. Usually a dirty/dislodged roller ring or motor issue.",
        "solution_steps": [
            "Remove the turntable plate and roller ring — clean them thoroughly.",
            "Check that the roller ring is seated correctly in the center groove.",
            "Place the turntable plate back — it should click into the center coupler.",
            "Make sure no food debris is blocking the roller ring's path.",
            "Run the microwave for 30 seconds — check if the plate now rotates.",
            "If it still doesn't rotate, the turntable motor is likely faulty — create a service ticket.",
        ],
    },
    {
        "product": ProductType.microwave,
        "intent": "display_issue",
        "title": "Microwave Display Not Working",
        "severity": "medium",
        "keywords": ["display", "screen", "display off", "display not working", "screen blank", "डिस्प्ले"],
        "content": "The microwave display is blank, shows garbled text, or is flickering.",
        "solution_steps": [
            "Unplug the microwave and plug it back in after 30 seconds (hard reset).",
            "Check if the control panel lock / child lock is active — hold the STOP button for 3 seconds to deactivate.",
            "Make sure the power supply is stable and not fluctuating.",
            "If the display shows partial segments, the LCD/LED panel may be damaged.",
            "If display remains blank after reset, create a service ticket — may need control board replacement.",
        ],
    },
    {
        "product": ProductType.microwave,
        "intent": "power_issue",
        "title": "Microwave Not Turning On",
        "severity": "high",
        "keywords": ["power", "not turning on", "not starting", "no power", "dead", "start nahi"],
        "content": "Microwave shows no response when powered on. Could be power supply, fuse, or door switch issue.",
        "solution_steps": [
            "Check if the power cord is securely plugged in.",
            "Test the outlet with another device.",
            "Check the circuit breaker for the kitchen circuit.",
            "Microwaves have an internal fuse — if it blows, it needs professional replacement.",
            "Ensure the door is fully closed — microwaves won't start if the door switch is faulty.",
            "If still no power, create a service ticket for internal fuse/door switch inspection.",
        ],
    },
    {
        "product": ProductType.microwave,
        "intent": "noise_issue",
        "title": "Microwave Making Unusual Noise",
        "severity": "medium",
        "keywords": ["noise", "sound", "loud", "buzzing", "humming", "grinding", "crackling"],
        "content": "Unusual sounds during microwave operation. Buzzing, grinding, or crackling sounds each indicate different issues.",
        "solution_steps": [
            "Buzzing sound: Normal for magnetron operation — mild buzzing is acceptable.",
            "Crackling/sparking: Stop immediately — check for metal items, aluminum foil, or damaged interior coating.",
            "Grinding from turntable: Clean the roller ring and ensure it's properly seated.",
            "Loud humming: May indicate a failing magnetron or fan — requires service.",
            "If sparks are visible inside, STOP using immediately and create an urgent service ticket.",
        ],
    },
    {
        "product": ProductType.microwave,
        "intent": "error_code",
        "title": "Microwave Error Code",
        "severity": "high",
        "keywords": ["error", "error code", "E1", "E2", "F1", "blinking", "code", "एरर"],
        "content": "Error codes on the microwave indicate sensor or component faults.",
        "solution_steps": [
            "Note the exact error code displayed.",
            "E1: Door sensor error — check door closure and latch.",
            "E2: Temperature sensor error — requires technician.",
            "F1: Fan motor error — the cooling fan may be blocked or broken.",
            "Unplug and replug the microwave after 2 minutes (resets the control board).",
            "If error persists, create a service ticket with the error code noted.",
        ],
    },
]


def seed():
    init_db()
    db = SessionLocal()
    try:
        existing = db.query(KnowledgeItem).count()
        if existing > 0:
            print(f"⚠️  Knowledge base already has {existing} items. Skipping seed.")
            print("   To re-seed, delete all rows from knowledge_items table first.")
            return

        items = []
        for data in KNOWLEDGE_DATA:
            item = KnowledgeItem(**data)
            items.append(item)

        db.bulk_save_objects(items)
        db.commit()
        print(f"✅ Seeded {len(items)} knowledge base items successfully!")
        print("   → AC: 6 items")
        print("   → Washing Machine: 6 items")
        print("   → Microwave: 6 items")
    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
