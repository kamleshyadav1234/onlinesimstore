from django.core.management.base import BaseCommand
from django.db import transaction
from telecom.models import TelecomOperator
from plans.models import PlanCategory, Plan

class Command(BaseCommand):
    help = 'Seed Airtel prepaid and postpaid plans'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📱 Seeding Airtel plans...'))
        
        # Get or create Airtel operator
        airtel, created = TelecomOperator.objects.get_or_create(
            name='Airtel',
            defaults={
                'operator_type': 'mobile',
                'description': 'One of India\'s leading telecom operators',
                'website': 'https://www.airtel.in',
                'customer_care': '121',
                'is_active': True,
            }
        )
        
        # Get categories
        prepaid_cat, _ = PlanCategory.objects.get_or_create(
            name='Prepaid Recharge',
            defaults={'category_type': 'prepaid', 'icon': 'fas fa-mobile-alt'}
        )
        
        postpaid_cat, _ = PlanCategory.objects.get_or_create(
            name='Postpaid Plans',
            defaults={'category_type': 'postpaid', 'icon': 'fas fa-file-invoice'}
        )
        
        special_cat, _ = PlanCategory.objects.get_or_create(
            name='Special Offers',
            defaults={'category_type': 'special', 'icon': 'fas fa-gift'}
        )
        
        # Airtel Plans
        airtel_plans = [
            # Popular Prepaid Plans
            {
                'name': 'Airtel ₹179 Plan',
                'category': prepaid_cat,
                'description': 'Basic plan with unlimited calls and 1GB daily data',
                'price': 179,
                'validity': 28,
                'data_allowance': '1GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Airtel Xstream Play',
                'other_benefits': 'Airtel Thanks rewards',
                'is_popular': True,
                'is_featured': False,
            },
            {
                'name': 'Airtel ₹299 Plan',
                'category': prepaid_cat,
                'description': 'Best seller with 1GB daily data and unlimited calls',
                'price': 299,
                'validity': 28,
                'data_allowance': '1GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Airtel Xstream Play, Wynk Music',
                'other_benefits': 'Data rollover, Night unlimited data',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'name': 'Airtel ₹349 Plan',
                'category': prepaid_cat,
                'description': '2GB daily data with premium benefits',
                'price': 349,
                'validity': 28,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Amazon Prime (Mobile), Disney+ Hotstar',
                'other_benefits': 'Double data on weekends',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'name': 'Airtel ₹479 Plan',
                'category': prepaid_cat,
                'description': '56 days validity with 1.5GB daily data',
                'price': 479,
                'validity': 56,
                'data_allowance': '1.5GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Amazon Prime, Disney+ Hotstar',
                'other_benefits': 'Double data on first recharge',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'name': 'Airtel ₹719 Plan',
                'category': prepaid_cat,
                'description': '84 days validity with 2GB daily data',
                'price': 719,
                'validity': 84,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Netflix, Amazon Prime, Disney+ Hotstar',
                'other_benefits': 'International calling pack included',
                'is_popular': False,
                'is_featured': True,
            },
            
            # Postpaid Plans
            {
                'name': 'Airtel Postpaid ₹399',
                'category': postpaid_cat,
                'description': 'Entry-level postpaid with 40GB data',
                'price': 399,
                'validity': 30,
                'data_allowance': '40GB total',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Netflix Basic, Amazon Prime',
                'other_benefits': 'Data rollover, Free outgoing roaming',
                'is_popular': False,
                'is_featured': True,
            },
            {
                'name': 'Airtel Postpaid ₹499',
                'category': postpaid_cat,
                'description': 'Popular postpaid with 75GB data',
                'price': 499,
                'validity': 30,
                'data_allowance': '75GB total',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Netflix Basic, Amazon Prime, Disney+ Hotstar',
                'other_benefits': 'Data rollover up to 200GB',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'name': 'Airtel Postpaid ₹799',
                'category': postpaid_cat,
                'description': 'Premium postpaid with 150GB data',
                'price': 799,
                'validity': 30,
                'data_allowance': '150GB total',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '300 SMS per day',
                'ott_benefits': 'Netflix 4K, Amazon Prime, Disney+ Hotstar',
                'other_benefits': 'Family data sharing, Priority customer care',
                'is_popular': False,
                'is_featured': True,
            },
            
            # Special Offers
            {
                'name': 'Airtel ₹199 Special',
                'category': special_cat,
                'description': 'Limited time offer with extra benefits',
                'price': 199,
                'validity': 28,
                'data_allowance': '1.5GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Airtel Xstream Play, SonyLIV',
                'other_benefits': 'Extra 5GB data on recharge',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'name': 'Airtel ₹399 Carnival Offer',
                'category': special_cat,
                'description': 'Festival special plan with enhanced benefits',
                'price': 399,
                'validity': 56,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Amazon Prime, ZEE5 Premium',
                'other_benefits': 'Free international calling minutes',
                'is_popular': False,
                'is_featured': True,
            },
        ]
        
        plans_created = 0
        with transaction.atomic():
            for plan_data in airtel_plans:
                plan, created = Plan.objects.get_or_create(
                    operator=airtel,
                    name=plan_data['name'],
                    defaults={
                        'category': plan_data['category'],
                        'description': plan_data['description'],
                        'price': plan_data['price'],
                        'validity': plan_data['validity'],
                        'validity_unit': 'days',
                        'data_allowance': plan_data['data_allowance'],
                        'voice_calls': plan_data['voice_calls'],
                        'sms': plan_data['sms'],
                        'ott_benefits': plan_data['ott_benefits'],
                        'other_benefits': plan_data['other_benefits'],
                        'is_popular': plan_data['is_popular'],
                        'is_featured': plan_data['is_featured'],
                        'is_active': True,
                    }
                )
                if created:
                    plans_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {plans_created} Airtel plans'))