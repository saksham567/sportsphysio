SERVICES = [
    {
        "icon": "ti-bone",
        "name": "ACL Rehabilitation",
        "description": (
            "Pre & post-surgery ACL recovery programs designed to restore strength, "
            "stability, and return-to-sport confidence."
        ),
        "tag": "Speciality",
    },
    {
        "icon": "ti-radius-bottom-right",
        "name": "Meniscus Rehab",
        "description": (
            "Structured recovery for meniscal tears — conservative management or "
            "post-surgical, tailored to your scan and symptoms."
        ),
        "tag": "Speciality",
    },
    {
        "icon": "ti-spine",
        "name": "Lower Back Rehab",
        "description": (
            "Evidence-based protocols for disc issues, muscle strains, and postural "
            "pain — active rehab, not just rest."
        ),
        "tag": "Speciality",
    },
    {
        "icon": "ti-run",
        "name": "Sports Injury Rehabilitation",
        "description": (
            "From sprains and strains to chronic overuse — rehab programs for athletes "
            "to get back in the game stronger."
        ),
        "tag": "All sports",
    },
]

PLANS = [
    {
        "slug": "video-consultation",
        "icon": "ti-video",
        "icon_class": "blue",
        "name": "1-on-1 Video Consultation",
        "price": 500,
        "price_display": "₹500",
        "per": "one-time session",
        "duration_icon": "ti-clock",
        "duration": "30 minutes",
        "featured": False,
        "cta": "Book Consultation",
        "cta_class": "outline-btn",
        "plan_label": "Video Consultation — ₹500 (30 min)",
        "is_recurring": False,
        "booking_heading": "Pick your consultation slot",
        "booking_desc": (
            "Select a one-time 30-minute video consultation slot. "
            "You'll be redirected to payment immediately after booking."
        ),
        "features": [
            ("check", "Live video call with Dr. Aahana"),
            ("check", "Bodyweight movement assessment"),
            ("check", "Injury history & symptom review"),
            ("check", "Initial guidance & next steps"),
            (
                "warn",
                "Wear comfortable clothes — you'll be asked to perform a few bodyweight movements for assessment",
            ),
        ],
    },
    {
        "slug": "monthly-rehab",
        "icon": "ti-heart-rate-monitor",
        "icon_class": "teal",
        "name": "Monthly Rehab Program",
        "price": 3000,
        "price_display": "₹3,000",
        "per": "per month",
        "duration_icon": "ti-calendar",
        "duration": "Full month · Week by week",
        "featured": True,
        "badge": "Best Value",
        "cta": "Start Rehab",
        "cta_class": "blue-btn",
        "plan_label": "Monthly Rehab Program — ₹3,000/month",
        "is_recurring": True,
        "booking_heading": "Pick your weekly check-in time",
        "booking_desc": (
            "Choose a recurring weekly slot for your 1-on-1 check-in call with Dr. Aahana "
            "throughout your rehab month. This repeats every week at the same time."
        ),
        "features": [
            ("check", "Personalised week-by-week rehab program"),
            ("check", "Exercise videos for every movement"),
            ("check", "WhatsApp support throughout"),
            ("check", "Form analysis & technique feedback"),
            ("check", "Program adjusted as you progress"),
        ],
    },
]

REVIEWS = [
    {
        "stars": 5,
        "text": (
            "Dr. Aahana's ACL program is genuinely incredible. Post-surgery I was scared "
            "to load my knee — she guided me every step of the way with exercise videos "
            "and daily WhatsApp check-ins."
        ),
        "initials": "RK",
        "author": "Rohan Kapoor",
        "tag": "ACL rehab · 3 months ago",
    },
    {
        "stars": 5,
        "text": (
            "Finally someone who explained my lower back problem properly. The week-by-week "
            "program actually made sense and I saw results within 3 weeks."
        ),
        "initials": "PS",
        "author": "Priya S.",
        "tag": "Lower back rehab · 1 month ago",
    },
    {
        "stars": 5,
        "text": (
            "The video consultation was worth every rupee. She assessed my movement, "
            "identified the issue, and I had a rehab plan within 24 hours. Super professional."
        ),
        "initials": "AM",
        "author": "Arjun M.",
        "tag": "Video consult · 2 weeks ago",
    },
]

HERO_STATS = [
    ("ACL", "Specialisation"),
    ("100%", "Online Rehab"),
    ("Govt.", "Certified PT"),
    ("4.9★", "Patient Rating"),
]
