import random
from django.core.management.base import BaseCommand
from bookings.models import Hotel, Room

HOTEL_NAMES = [
    "Blue Nile Retreat", "Addis Comfort Inn", "Lalibela Sky Hotel",
    "Axum Heritage Lodge", "Simien Mountain View", "Omo Riverside",
    "Harar Old Town Hotel", "Gondar Castle Inn", "Bahir Dar Lakeside",
    "Dire Dawa Central", "Adama Oasis", "Arba Minch Panorama",
    "Mekele Highland Hotel", "Awash Falls Resort", "Debre Zeit Escape",
    "Shashemene Green Gardens", "Jimma Coffee House", "Jinka Valley Lodge",
    "Semera Desert Rose", "Negele Borana Eco Lodge"
]

LOCATIONS = [
    "Addis Ababa, Ethiopia", "Lalibela, Ethiopia", "Axum, Ethiopia",
    "Simien Mountains, Ethiopia", "Omo Valley, Ethiopia", "Harar, Ethiopia",
    "Gondar, Ethiopia", "Bahir Dar, Ethiopia", "Dire Dawa, Ethiopia",
    "Adama, Ethiopia", "Arba Minch, Ethiopia", "Mekele, Ethiopia",
    "Awash, Ethiopia", "Debre Zeit, Ethiopia", "Shashemene, Ethiopia",
    "Jimma, Ethiopia", "Jinka, Ethiopia", "Semera, Ethiopia", "Negele Borana, Ethiopia"
]

class Command(BaseCommand):
    help = "Seed 20 Ethiopian hotels (0–5 rooms each), preserving any existing ones."

    def handle(self, *args, **options):
        for name, loc in zip(HOTEL_NAMES, LOCATIONS):
            hotel, created = Hotel.objects.get_or_create(
                name=name,
                defaults={
                    'location': loc,
                    'description': f"A lovely stay at {name}.",
                    'has_pool': random.choice([True, False]),
                    'has_gym': random.choice([True, False]),
                    'price': round(random.uniform(50, 300), 2),
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Created hotel: {name}"))
            # Add rooms until the hotel has between 0 and 5 total
            current = hotel.rooms.count()
            target = random.randint(0, 5)
            for i in range(current, target):
                Room.objects.create(
                    hotel=hotel,
                    name=f"Room {i+1}",
                    room_type=random.choice(['SINGLE','DOUBLE','SUITE']),
                    price=round(random.uniform(30,200),2),
                    capacity=random.choice([1,2,3,4]),
                    is_available=True,
                )
            self.stdout.write(f"   → Now has {hotel.rooms.count()} rooms.\n")
        self.stdout.write(self.style.SUCCESS("🎉 Seeding complete."))
