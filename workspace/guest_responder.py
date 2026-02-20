#!/usr/bin/env python3
"""
Guest Message Responder — "Respond Like Lorenzo"

Template-based message generator trained on 23,153 real messages (5,625 host).

Usage:
  python3 guest_responder.py --welcome <name> <property> [--lang it]
  python3 guest_responder.py --checkin <name> <property> [--code XXXX] [--lang it]
  python3 guest_responder.py --during-stay <name> [--lang it]
  python3 guest_responder.py --checkout <name> <property> [--lang it]
  python3 guest_responder.py --post-stay <name> [--lang it]
  python3 guest_responder.py --form <name> <property> [<booking_ref>] [--lang it]
  python3 guest_responder.py --list-templates
  python3 guest_responder.py --help

Properties: Milano, Drovetti, Bardonecchia, "Giacinto Collegno"
Languages: en (default), it
"""

import sys
import json
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────

CONFIG_PATH = Path.home() / ".openclaw/workspace/guest_config.json"

PROPERTY_ALIASES = {
    "milano": "Milano",
    "milan": "Milano",
    "brianza": "Milano",
    "drovetti": "Drovetti",
    "torino": "Drovetti",
    "turin": "Drovetti",
    "bardonecchia": "Bardonecchia",
    "bardo": "Bardonecchia",
    "giacinto": "Giacinto Collegno",
    "collegno": "Giacinto Collegno",
    "giacinto collegno": "Giacinto Collegno",
}

# ── Config Loader ────────────────────────────────────────────────────────────

def _load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text())
    except json.JSONDecodeError as e:
        print(f"  Warning: invalid JSON in {CONFIG_PATH}: {e}")
        return {}

def _resolve_property(name: str) -> str:
    """Resolve property alias to canonical name."""
    key = name.lower().strip()
    if key in PROPERTY_ALIASES:
        return PROPERTY_ALIASES[key]
    # Direct match
    config = _load_config()
    for prop in config:
        if prop.lower() == key:
            return prop
    return name

def _get_prop(name: str) -> dict:
    """Get property config by name."""
    config = _load_config()
    canonical = _resolve_property(name)
    return config.get(canonical, {})

# ── Templates ────────────────────────────────────────────────────────────────

TEMPLATES = {
    "welcome": {
        "en": [
            {
                "name": "standard",
                "template": """Hello {name}, and thanks for your reservation!

I will contact you a couple of days before your arrival to make sure that everything is okay on your side, and give you some additional instructions for a smooth check-in.

If you have any questions in the meantime, don't hesitate to ask!

All the best,
Lorenzo""",
            },
            {
                "name": "short",
                "template": """Dear {name},

Thanks for having booked with us!

A couple of days before your arrival we will share the check-in information.

Kind regards,
Lorenzo""",
            },
            {
                "name": "with_recommendations",
                "template": """Hello {name}, and thanks for your reservation!

I will contact you a couple of days before your arrival to make sure that everything is okay on your side, and give you some additional instructions for a smooth check-in.

If you're a planner, here are some of my local recommendations:
{recommendations_link}

All the best,
Lorenzo""",
            },
        ],
        "it": [
            {
                "name": "standard",
                "template": """Ciao {name} e grazie per la tua prenotazione!

Se hai bisogno di ulteriori informazioni, non esitare a chiedere, sarò lieto di rispondere a qualsiasi domanda tu possa avere!

In ogni caso, ti contatterò qualche giorno prima del tuo arrivo per assicurarmi che tutto vada bene dalla tua parte e ti darò alcune istruzioni aggiuntive per un check-in senza problemi.

Non vedo l'ora di ospitarti!

Cordiali saluti,
Lorenzo""",
            },
            {
                "name": "short",
                "template": """Ciao {name},

Grazie per aver prenotato da noi! Ti contatterò qualche giorno prima del tuo arrivo con le istruzioni per il check-in.

A presto!
Lorenzo""",
            },
        ],
    },

    "checkin": {
        "en": {
            "Milano": {
                "name": "milano_nuki",
                "template": """Dear {name},

1. Please send us a message on this chat 20 minutes before your arrival
2. Your code for the keypad is {code} the apartment is on the 7th (top floor)
3. You will find two keys on the table: one for the outdoor building and one for the trash bin.
4. No key is provided for the apartment, to lock the door you can press the arrow key.

One minute video showing you the Check-In:
{checkin_video}

I've also created an electronic house manual for your viewing pleasure:
{recommendations_link}
It has all the info you'd want: nice food spots nearby, how to use the appliances, etc.

Kind regards,
Lorenzo""",
            },
            "Drovetti": {
                "name": "drovetti_lockbox",
                "template": """Dear {name},

1. Please send us a message 20 minutes on this chat before your arrival so that we can prepare to buzz you in remotely.
2. You will find your keys in the Master lock the code will be {lockbox_code}
Once you inserted the code twist the knob to open it.

This video will guide you through the check in:
{checkin_video}

I've also created an electronic house manual for your viewing pleasure:
{recommendations_link}
It has all the info you'd want: you can find out how to open the door, turn on the hot water (house manual section), property address, nice food spots nearby, etc.

Kind regards,
Lorenzo""",
            },
            "Giacinto Collegno": {
                "name": "giacinto_lockbox",
                "template": """Dear {name},

1. Please send us a message 20 minutes before your arrival so that we can prepare to buzz you in remotely.
2. You will find your keys in the Master lock the code will be {lockbox_code}
Once you inserted the code pull the lever to open it.

This video will guide you through the check in:
{checkin_video}

I've also created an electronic house manual for your viewing pleasure:
{recommendations_link}

Kind regards,
Lorenzo""",
            },
            "Bardonecchia": {
                "name": "bardonecchia_lockbox",
                "template": """Dear {name},

This video will guide you through the check in:
{checkin_video}

The code for the lockbox will be {lockbox_code}

I hope that you settle in alright and that you experience a 5-star stay :) Please let me know if there is anything you need or if I can assist you in any way!

All the best,
Lorenzo""",
            },
            "_default": {
                "name": "generic",
                "template": """Dear {name},

I look forward to welcoming you!

I'll share the check-in details with you shortly. If you have any questions, don't hesitate to ask!

Kind regards,
Lorenzo""",
            },
        },
        "it": {
            "Milano": {
                "name": "milano_nuki_it",
                "template": """Gentile {name},

1. Mandaci un messaggio su questa chat 20 minuti prima del vostro arrivo
2. Il codice per il tastierino sarà {code}, l'appartamento è al 7° piano (ultimo piano)
3. Troverete due chiavi sul tavolo: una per il portone e una per i bidoni della spazzatura.
4. Non viene fornita una chiave per l'appartamento, per chiudere la porta basta premere la freccia sul tastierino.

Video di un minuto per il Check-In:
{checkin_video}

Ho anche creato una guida digitale della casa per voi:
{recommendations_link}

Cordiali saluti,
Lorenzo""",
            },
            "Drovetti": {
                "name": "drovetti_lockbox_it",
                "template": """Gentile {name},

Check-In:
1) Avvisateci 20 minuti prima del vostro arrivo tramite la chat in modo da essere pronti ad aprirvi il portone condominiale da remoto.

2) Dentro il condominio potrete ritirare le chiavi nel lockbox che avrà il seguente codice: {lockbox_code}
Una volta inserito bisogna girare la manopola per aprirlo.

Troverai tutte le informazioni per il Check-in nel seguente video:
{checkin_video}

Ho anche creato una guida digitale della casa per voi:
{recommendations_link}

Cordiali saluti,
Lorenzo""",
            },
            "Giacinto Collegno": {
                "name": "giacinto_lockbox_it",
                "template": """Gentile {name},

Check-In:
1) Avvisateci 20 minuti prima del vostro arrivo tramite la chat in modo da essere pronti ad aprirvi il portone condominiale da remoto.

2) Dentro il condominio potrete ritirare le chiavi nel lockbox che avrà il seguente codice: {lockbox_code}
Una volta inserito bisogna tirare la levetta per aprirlo.

Troverai tutte le informazioni per il Check-in nel seguente video:
{checkin_video}

Ho anche creato una guida digitale della casa per voi:
{recommendations_link}

Cordiali saluti,
Lorenzo""",
            },
            "Bardonecchia": {
                "name": "bardonecchia_lockbox_it",
                "template": """Gentile {name},

Ecco una veloce video spiegazione di come raggiungere il nostro appartamento:
{checkin_video}

Se c'è qualcos'altro di cui hai bisogno, ad esempio consigli, indicazioni o qualsiasi dubbio sul tuo alloggio, faccelo sapere. Siamo molto felici di aiutarti e di farti vivere un'esperienza a 5 stelle.

Il codice per l'appartamento sarà {lockbox_code}

Cordiali saluti,
Lorenzo""",
            },
            "_default": {
                "name": "generic_it",
                "template": """Gentile {name},

Non vedo l'ora di darti il benvenuto! Ti invierò i dettagli per il check-in a breve. Se hai domande, non esitare a chiedere!

Cordiali saluti,
Lorenzo""",
            },
        },
    },

    "during_stay": {
        "en": [
            {
                "name": "standard",
                "template": """Good morning {name}!

I hope that you have settled in alright and that you are experiencing a 5-star stay :) Please let me know if there is anything you need or if I can assist you in any way!

All the best and enjoy your stay!
Lorenzo""",
            },
            {
                "name": "short",
                "template": """Hi {name}, hope you're settling in well! Let me know if you need anything 😊

All the best,
Lorenzo""",
            },
        ],
        "it": [
            {
                "name": "standard",
                "template": """Buongiorno {name}!

Spero tu abbia trascorso una piacevole notte di riposo.

Ti scrivo per assicurarmi che tutto vada bene e sia in linea con le tue aspettative.

Se hai bisogno di qualcosa o pensi che possiamo rendere la tua permanenza più confortevole, faccelo sapere!

Cordiali saluti,
Lorenzo""",
            },
        ],
    },

    "checkout": {
        "en": {
            "_default": {
                "name": "standard",
                "template": """Dear {name},

I hope that you have had a wonderful stay so far! I would like to remind you that the normal check-out time is by 10:00 AM.

Before leaving, please:
1. Clean the dishes and cutlery.
2. Make sure that you have turned off all lights and closed all windows.
3. Lock the door and {key_return_instruction}.

I wish you a good trip and goodbye!

Safe travels,
Lorenzo""",
            },
            "Bardonecchia": {
                "name": "bardonecchia",
                "template": """Dear {name},

Thank you for staying with us!
Your checkout time is tomorrow before 10:00 AM

Please before check out:
1. Leave the fridge empty and open.
2. Clean the dishes and cutlery.
3. Throw away the garbage (the baskets are on the way to Via Melezet)
4. Close the door and leave the key inside the lockbox

We wish you a good trip and goodbye!

Safe travels,
Lorenzo""",
            },
        },
        "it": {
            "_default": {
                "name": "standard",
                "template": """Gentile {name},

Ricorda che il check-out è domani per le 10:00.

Per cortesia prima del check-out:
1. Pulire i piatti e le posate.
2. Assicurarsi di aver spento tutte le luci e di aver chiuso tutte le finestre.
3. Chiudere la porta a chiave e {key_return_instruction_it}.

Vi auguro un buon viaggio e arrivederci!

Buon viaggio,
Lorenzo""",
            },
            "Bardonecchia": {
                "name": "bardonecchia_it",
                "template": """Gentile {name},

Grazie per aver soggiornato con noi!
Il check-out è domani entro le 10:00.

Per cortesia prima del check-out:
1. Lasciare il frigo vuoto e aperto.
2. Pulire i piatti e le posate.
3. Buttare la spazzatura (i bidoni sono lungo Via Melezet)
4. Chiudere la porta e lasciare la chiave nel lockbox

Vi auguriamo un buon viaggio e arrivederci!

Buon viaggio,
Lorenzo""",
            },
        },
    },

    "post_stay": {
        "en": [
            {
                "name": "standard",
                "template": """Dear {name},

Thanks for leaving the place in great shape!

If you have anything to share about your stay, pros or cons, I'm very interested to hear as I like to improve my guest's experience.

I'll be leaving you a 5-star review when Airbnb allows 😊

Safe travels!
Lorenzo""",
            },
            {
                "name": "formal",
                "template": """Dear {name},

Thank you for staying with us and leaving the home in such great shape. I can't tell you how much we appreciate it!

We have left a glowing 5-star review to reflect what a pleasure it was to host you. We would be most grateful for your review in return.

Safe travels!
Lorenzo""",
            },
        ],
        "it": [
            {
                "name": "standard",
                "template": """Gentile {name},

Grazie ancora per aver prenotato da noi, è stato un piacere ospitarti e speriamo tu abbia apprezzato il tuo soggiorno.

Se avete qualche suggerimento su come possiamo migliorare l'esperienza dei nostri futuri ospiti ve ne saremmo molto grati.

Stasera vi lascerò una recensione a 5 stelle 😊

Buon viaggio!
Lorenzo""",
            },
        ],
    },

    "form": {
        "en": [
            {
                "name": "standard",
                "template": """Hi {name}, please fill out the following form before arrival:
{form_link}

({form_explanation})

All the best,
Lorenzo""",
            },
            {
                "name": "with_checkin_gate",
                "template": """Hi {name},

Before receiving your final check-in instructions please fill out the following form:
{form_link}

({form_explanation})

All the best,
Lorenzo""",
            },
        ],
        "it": [
            {
                "name": "standard",
                "template": """Gentile {name},

Prima di ricevere le istruzioni per il check-in è richiesta la compilazione del seguente modulo:
{form_link}

({form_explanation})

Cordiali saluti,
Lorenzo""",
            },
        ],
    },
}

# ── Key Return Mapping ───────────────────────────────────────────────────────

KEY_RETURN = {
    "Milano": {
        "en": "leave the keys on the table",
        "it": "lasciare le chiavi sul tavolo",
    },
    "Drovetti": {
        "en": "leave the keys in the lockbox",
        "it": "lasciare le chiavi nel lockbox",
    },
    "Bardonecchia": {
        "en": "leave the key inside the lockbox",
        "it": "lasciare la chiave nel lockbox",
    },
    "Giacinto Collegno": {
        "en": "leave the keys on the table",
        "it": "lasciare le chiavi sul tavolo",
    },
}

# ── Commands ─────────────────────────────────────────────────────────────────

def cmd_welcome(name: str, property_name: str, lang: str = "en"):
    prop = _resolve_property(property_name)
    prop_config = _get_prop(property_name)
    templates = TEMPLATES["welcome"].get(lang, TEMPLATES["welcome"]["en"])

    # Use recommendations variant if property has a link
    rec_link = prop_config.get("recommendations_link")
    if rec_link:
        tpl = next((t for t in templates if "recommendations" in t.get("name", "")), templates[0])
        msg = tpl["template"].format(name=name, recommendations_link=rec_link)
    else:
        tpl = templates[0]  # standard
        msg = tpl["template"].format(name=name)

    _print_draft(msg, "welcome", prop, lang)


def cmd_checkin(name: str, property_name: str, code: str = None, lang: str = "en"):
    prop = _resolve_property(property_name)
    prop_config = _get_prop(property_name)
    checkin_templates = TEMPLATES["checkin"].get(lang, TEMPLATES["checkin"]["en"])

    # Get property-specific or default template
    tpl = checkin_templates.get(prop, checkin_templates.get("_default"))

    # Select correct check-in video based on language
    if lang == "it" and prop_config.get("checkin_video_it"):
        checkin_video = prop_config["checkin_video_it"]
    else:
        checkin_video = prop_config.get("checkin_video", "[VIDEO_LINK]")

    # Get recommendations link (prefer restaurants variant for check-in)
    rec_link = prop_config.get("recommendations_link_restaurants",
                               prop_config.get("recommendations_link", ""))

    # Build format kwargs
    fmt = {
        "name": name,
        "code": code or prop_config.get("nuki_keypad_code", "[CODE]"),
        "checkin_video": checkin_video,
        "lockbox_code": prop_config.get("lockbox_code", "[LOCKBOX_CODE]"),
        "recommendations_link": rec_link,
    }

    msg = tpl["template"].format(**fmt)
    _print_draft(msg, "checkin", prop, lang)


def cmd_during_stay(name: str, lang: str = "en"):
    templates = TEMPLATES["during_stay"].get(lang, TEMPLATES["during_stay"]["en"])
    tpl = templates[0]  # standard
    msg = tpl["template"].format(name=name)
    _print_draft(msg, "during-stay", None, lang)


def cmd_checkout(name: str, property_name: str, lang: str = "en"):
    prop = _resolve_property(property_name)
    checkout_templates = TEMPLATES["checkout"].get(lang, TEMPLATES["checkout"]["en"])

    # Get property-specific or default template
    tpl = checkout_templates.get(prop, checkout_templates.get("_default"))

    key_info = KEY_RETURN.get(prop, KEY_RETURN["Milano"])
    if lang == "it":
        key_instruction = key_info.get("it", key_info["en"])
        msg = tpl["template"].format(name=name, key_return_instruction_it=key_instruction)
    else:
        key_instruction = key_info.get("en", "leave the keys on the table")
        msg = tpl["template"].format(name=name, key_return_instruction=key_instruction)

    _print_draft(msg, "checkout", prop, lang)


def cmd_post_stay(name: str, lang: str = "en"):
    templates = TEMPLATES["post_stay"].get(lang, TEMPLATES["post_stay"]["en"])
    tpl = templates[0]  # standard
    msg = tpl["template"].format(name=name)
    _print_draft(msg, "post-stay", None, lang)


def cmd_form(name: str, property_name: str, booking_ref: str = None, lang: str = "en"):
    prop = _resolve_property(property_name)
    prop_config = _get_prop(property_name)
    templates = TEMPLATES["form"].get(lang, TEMPLATES["form"]["en"])

    form_link = prop_config.get("form_link", "[FORM_LINK]")
    if booking_ref and "{booking_ref}" in form_link:
        form_link = form_link.replace("{booking_ref}", booking_ref)

    explanation_key = "form_explanation_it" if lang == "it" else "form_explanation_en"
    form_explanation = prop_config.get(explanation_key, "")

    # Use with_checkin_gate for Drovetti (form gates check-in instructions)
    if prop == "Drovetti" and lang == "en":
        tpl = next((t for t in templates if t["name"] == "with_checkin_gate"), templates[0])
    else:
        tpl = templates[0]

    msg = tpl["template"].format(
        name=name,
        form_link=form_link,
        form_explanation=form_explanation,
    )
    _print_draft(msg, "form", prop, lang)


def cmd_list_templates():
    print("\n📋  Available Templates\n")
    print("  " + "─" * 55)

    for category, data in TEMPLATES.items():
        category_label = category.replace("_", " ").title()
        print(f"\n  📝 {category_label}")

        if isinstance(data, dict):
            for lang, items in data.items():
                if isinstance(items, list):
                    for tpl in items:
                        print(f"     [{lang}] {tpl['name']}")
                elif isinstance(items, dict):
                    for prop, tpl in items.items():
                        if isinstance(tpl, dict) and "name" in tpl:
                            label = prop if prop != "_default" else "default"
                            print(f"     [{lang}] {label}: {tpl['name']}")

    print(f"\n  " + "─" * 55)
    print(f"  Properties: Milano, Drovetti, Bardonecchia, Giacinto Collegno")
    print(f"  Languages: en (default), it\n")

    print("  Usage examples:")
    print('    python3 guest_responder.py --welcome "Mario Rossi" Milano')
    print('    python3 guest_responder.py --checkin "Mario Rossi" Drovetti --lang it')
    print('    python3 guest_responder.py --checkout "Mario Rossi" Milano')
    print('    python3 guest_responder.py --post-stay "Mario Rossi"')
    print('    python3 guest_responder.py --form "Mario Rossi" Drovetti ABC123')
    print()


# ── Output ───────────────────────────────────────────────────────────────────

def _print_draft(msg: str, category: str, prop: str = None, lang: str = "en"):
    lang_label = "🇮🇹 IT" if lang == "it" else "🇬🇧 EN"
    prop_label = f" @ {prop}" if prop else ""
    print(f"\n✉️  Draft — {category}{prop_label} [{lang_label}]")
    print("─" * 60)
    print(msg)
    print("─" * 60)
    print("📋 Copy the message above. Review before sending!\n")


# ── Argument Parsing ─────────────────────────────────────────────────────────

def _parse_args(args: list) -> dict:
    """Simple argument parser matching hospitable.py style."""
    result = {"command": None, "positional": [], "lang": "en", "code": None}

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--"):
            if arg == "--lang" and i + 1 < len(args):
                result["lang"] = args[i + 1]
                i += 2
                continue
            elif arg == "--code" and i + 1 < len(args):
                result["code"] = args[i + 1]
                i += 2
                continue
            elif arg in ("--help", "-h"):
                result["command"] = "help"
            elif arg == "--list-templates":
                result["command"] = "list-templates"
            else:
                result["command"] = arg.lstrip("-")
        else:
            result["positional"].append(arg)
        i += 1

    return result


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    parsed = _parse_args(args)
    cmd = parsed["command"]
    pos = parsed["positional"]
    lang = parsed["lang"]

    if cmd in ("help", None) and not pos:
        print(__doc__)
    elif cmd == "list-templates":
        cmd_list_templates()
    elif cmd == "welcome":
        if len(pos) < 2:
            print("Usage: --welcome <name> <property> [--lang it]")
            sys.exit(1)
        cmd_welcome(pos[0], pos[1], lang)
    elif cmd == "checkin":
        if len(pos) < 2:
            print("Usage: --checkin <name> <property> [--code XXXX] [--lang it]")
            sys.exit(1)
        cmd_checkin(pos[0], pos[1], parsed["code"], lang)
    elif cmd in ("during-stay", "during_stay"):
        if len(pos) < 1:
            print("Usage: --during-stay <name> [--lang it]")
            sys.exit(1)
        cmd_during_stay(pos[0], lang)
    elif cmd == "checkout":
        if len(pos) < 2:
            print("Usage: --checkout <name> <property> [--lang it]")
            sys.exit(1)
        cmd_checkout(pos[0], pos[1], lang)
    elif cmd in ("post-stay", "post_stay"):
        if len(pos) < 1:
            print("Usage: --post-stay <name> [--lang it]")
            sys.exit(1)
        cmd_post_stay(pos[0], lang)
    elif cmd == "form":
        if len(pos) < 2:
            print("Usage: --form <name> <property> [<booking_ref>] [--lang it]")
            sys.exit(1)
        booking_ref = pos[2] if len(pos) > 2 else None
        cmd_form(pos[0], pos[1], booking_ref, lang)
    else:
        print(f"Unknown command: --{cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
