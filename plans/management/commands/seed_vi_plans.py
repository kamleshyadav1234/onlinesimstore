from django.core.management.base import BaseCommand
from django.db import transaction
from telecom.models import TelecomOperator
from plans.models import PlanCategory, Plan

class Command(BaseCommand):
    help = 'Seed VI (Vodafone Idea) prepaid plans'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📱 Seeding VI plans...'))
        
        # Get or create VI operator
        vi, created = TelecomOperator.objects.get_or_create(
            name='Vodafone Idea (VI)',
            defaults={
                'operator_type': 'mobile',
                'description': 'Pan-India telecom operator with extensive coverage',
                'website': 'https://www.myvi.in',
                'customer_care': '199',
                'is_active': True,
            }
        )
        
        # Get categories
        prepaid_cat, _ = PlanCategory.objects.get_or_create(
            name='Prepaid Recharge',
            defaults={'category_type': 'prepaid', 'icon': 'fas fa-mobile-alt'}
        )
        
        special_cat, _ = PlanCategory.objects.get_or_create(
            name='Special Offers',
            defaults={'category_type': 'special', 'icon': 'fas fa-gift'}
        )
        
        roaming_cat, _ = PlanCategory.objects.get_or_create(
            name='International Roaming',
            defaults={'category_type': 'roaming', 'icon': 'fas fa-globe'}
        )
        
        # VI Plans
        vi_plans = [
            # Popular Prepaid Plans
            {
                'name': 'VI ₹179 Plan',
                'category': prepaid_cat,
                'description': 'Entry-level plan with unlimited calls and data',
                'price': 179,
                'validity': 28,
                'data_allowance': '1GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Vodafone Play',
                'other_benefits': 'Extra 1GB data on first recharge',
                'is_popular': True,
                'is_featured': False,
            },
            {
                'name': 'VI ₹299 Plan',
                'category': prepaid_cat,
                'description': 'Best value plan with 1.5GB daily data',
                'price': 299,
                'validity': 28,
                'data_allowance': '1.5GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Vodafone Play, ZEE5 Premium',
                'other_benefits': 'Extra 2GB data on Sundays',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'name': 'VI ₹399 Plan',
                'category': prepaid_cat,
                'description': 'Premium plan with 2GB daily data',
                'price': 399,
                'validity': 56,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Amazon Prime (Mobile), Vodafone Play',
                'other_benefits': 'Night unlimited data, Weekend booster',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'name': 'VI ₹549 Plan',
                'category': prepaid_cat,
                'description': 'Long validity plan for 84 days',
                'price': 549,
                'validity': 84,
                'data_allowance': '1.5GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Amazon Prime, ZEE5 Premium',
                'other_benefits': 'Free outgoing roaming',
                'is_popular': False,
                'is_featured': True,
            },
            {
                'name': 'VI ₹699 Plan',
                'category': prepaid_cat,
                'description': 'Super saver plan with 2.5GB daily data',
                'price': 699,
                'validity': 84,
                'data_allowance': '2.5GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Amazon Prime, Netflix Basic, ZEE5',
                'other_benefits': 'International calling minutes included',
                'is_popular': False,
                'is_featured': True,
            },
            
            # Special Offers
            {
                'name': 'VI Super ₹199',
                'category': special_cat,
                'description': 'Special offer with enhanced data benefits',
                'price': 199,
                'validity': 28,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Vodafone Play Premium',
                'other_benefits': 'Double data for first 3 days',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'name': 'VI Festival ₹499',
                'category': special_cat,
                'description': 'Festival special plan with OTT subscriptions',
                'price': 499,
                'validity': 70,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Amazon Prime, Disney+ Hotstar',
                'other_benefits': 'Free international roaming pack',
                'is_popular': False,
                'is_featured': True,
            },
            
            # International Roaming
            {
                'name': 'VI Europe Roaming ₹899',
                'category': roaming_cat,
                'description': 'International roaming pack for Europe',
                'price': 899,
                'validity': 10,
                'data_allowance': '5GB total',
                'voice_calls': '100 minutes outgoing',
                'sms': '100 SMS',
                'ott_benefits': '',
                'other_benefits': 'Valid in 20+ European countries',
                'is_popular': False,
                'is_featured': True,
            },
            {
                'name': 'VI USA Roaming ₹1299',
                'category': roaming_cat,
                'description': 'Roaming pack for USA and Canada',
                'price': 1299,
                'validity': 15,
                'data_allowance': '10GB total',
                'voice_calls': '200 minutes outgoing',
                'sms': '200 SMS',
                'ott_benefits': '',
                'other_benefits': 'Works in USA, Canada, Mexico',
                'is_popular': False,
                'is_featured': True,
            },
            
            # Data Packs
            {
                'name': 'VI Data Booster ₹48',
                'category': prepaid_cat,
                'description': 'Data-only booster pack',
                'price': 48,
                'validity': 7,
                'data_allowance': '5GB total',
                'voice_calls': 'Not included',
                'sms': 'Not included',
                'ott_benefits': '',
                'other_benefits': 'Works on 4G+ network',
                'is_popular': True,
                'is_featured': False,
            },
            {
                'name': 'VI Night Data ₹19',
                'category': prepaid_cat,
                'description': 'Night unlimited data pack',
                'price': 19,
                'validity': 7,
                'data_allowance': 'Unlimited (12AM-6AM)',
                'voice_calls': 'Not included',
                'sms': 'Not included',
                'ott_benefits': '',
                'other_benefits': 'Unlimited data during night hours',
                'is_popular': True,
                'is_featured': False,
            },
        ]
        
        plans_created = 0
        with transaction.atomic():
            for plan_data in vi_plans:
                plan, created = Plan.objects.get_or_create(
                    operator=vi,
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
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {plans_created} VI plans'))