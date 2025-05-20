import random, os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
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

POSSIBLE_AMENITIES = [
    "Free WiFi", "Pool", "Gym", "Spa", "Restaurant", "Bar", "Parking",
    "Airport Shuttle", "Pet Friendly", "Breakfast Included",
    "Room Service", "Laundry Service", "24h Front Desk"
]

BED_TYPES = ['SINGLE', 'QUEEN', 'KING']

PROJECT_ROOT = settings.BASE_DIR
MEDIA_IMAGES = os.path.join(PROJECT_ROOT, 'media', 'hotel_images')


def find_image_path(name):
    slug = name.lower().replace(' ', '_')
    for ext in ('jpg', 'jpeg', 'png', 'avif'):
        candidate = os.path.join(MEDIA_IMAGES, f"{slug}.{ext}")
        if os.path.exists(candidate):
            return candidate
    return None


class Command(BaseCommand):
    help = "Seed hotels + rooms + attach images + set image_url"

    def handle(self, *args, **options):
        # Wipe existing data (optional)
        Hotel.objects.all().delete()
        Room.objects.all().delete()

        for name, loc in zip(HOTEL_NAMES, LOCATIONS):
            amenities = random.sample(POSSIBLE_AMENITIES, k=5)
            defaults = {
                'location': loc,
                'description': f"A lovely stay at {name}.",
                'has_pool': 'Pool' in amenities,
                'has_gym': 'Gym' in amenities,
                'price': round(random.uniform(50, 300), 2),
                'stars': random.randint(1, 5),
                'amenities': amenities,
                'is_active': True,
            }
            hotel, _ = Hotel.objects.get_or_create(name=name, defaults=defaults)

            # Attach featured_image and set image_url
            img_path = find_image_path(name)
            if img_path:
                with open(img_path, 'rb') as f:
                    hotel.featured_image.save(os.path.basename(img_path), File(f), save=True)
                ext = os.path.splitext(img_path)[1]
                slug = name.lower().replace(' ', '_')
                hotel.image_url = settings.MEDIA_URL + f"hotel_images/{slug}{ext}"
                hotel.save()
                self.stdout.write(self.style.SUCCESS(f"Seeded image & URL for {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"No image found for {name}"))

            # Seed rooms
            target = random.randint(1, 5)
            for i in range(target):
                Room.objects.create(
                    hotel=hotel,
                    name=f"Room {i+1}",
                    description="Comfortable and spacious room.",
                    bed_count=random.randint(1, 3),
                    bathroom_count=random.randint(1, 2),   # New field
                    bed_type=random.choice(BED_TYPES),     # New field
                    price=round(random.uniform(30, 200), 2),
                    capacity=random.choice([1, 2, 3, 4]),
                    is_available=True
                )
            self.stdout.write(f" → {hotel.name} has {hotel.rooms.count()} rooms")

        self.stdout.write(self.style.SUCCESS("🎉 Seeding complete."))
