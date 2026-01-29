from django.core.management.base import BaseCommand
from django.db import transaction
from telecom.models import TelecomOperator
from plans.models import PlanCategory, Plan

class Command(BaseCommand):
    help = 'Seed Jio prepaid and postpaid plans'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📱 Seeding Jio plans...'))
        
        # Get or create Jio operator
        jio, created = TelecomOperator.objects.get_or_create(
            name='Reliance Jio',
            defaults={
                'operator_type': 'mobile',
                'description': 'India\'s largest 4G/5G mobile network operator',
                'website': 'https://www.jio.com',
                'customer_care': '198',
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
        
        data_cat, _ = PlanCategory.objects.get_or_create(
            name='Data Packs',
            defaults={'category_type': 'data', 'icon': 'fas fa-database'}
        )
        
        annual_cat, _ = PlanCategory.objects.get_or_create(
            name='Annual Plans',
            defaults={'category_type': 'prepaid', 'icon': 'fas fa-calendar-alt'}
        )
        
        # Jio Prepaid Plans
        jio_plans = [
            # Prepaid Plans
            {
                'name': 'Jio ₹199 Plan',
                'category': prepaid_cat,
                'description': 'Entry-level plan with 1GB daily data and unlimited calls',
                'price': 199,
                'validity': 28,
                'data_allowance': '1GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'JioTV, JioCinema',
                'other_benefits': 'Free incoming calls',
                'is_popular': True,
                'is_featured': False,
            },
            {
                'name': 'Jio ₹299 Plan',
                'category': prepaid_cat,
                'description': 'Popular plan with 1.5GB daily data and Jio apps',
                'price': 299,
                'validity': 28,
                'data_allowance': '1.5GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'JioTV, JioCinema, JioSaavn',
                'other_benefits': 'No roaming charges',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'name': 'Jio ₹399 Plan',
                'category': prepaid_cat,
                'description': 'High-speed plan with 2GB daily data and Hotstar',
                'price': 399,
                'validity': 28,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Disney+ Hotstar, JioTV, JioCinema',
                'other_benefits': 'Data rollover up to 200GB',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'name': 'Jio ₹599 Plan',
                'category': prepaid_cat,
                'description': '84 days validity with 1.5GB daily data',
                'price': 599,
                'validity': 84,
                'data_allowance': '1.5GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Disney+ Hotstar, Amazon Prime',
                'other_benefits': 'Extra data on recharge',
                'is_popular': False,
                'is_featured': True,
            },
            
            # Postpaid Plans
            {
                'name': 'Jio Postpaid ₹399',
                'category': postpaid_cat,
                'description': 'Basic postpaid with 75GB data and OTT benefits',
                'price': 399,
                'validity': 30,
                'data_allowance': '75GB total',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Netflix, Amazon Prime, Disney+ Hotstar',
                'other_benefits': 'Data rollover, Free outgoing roaming',
                'is_popular': False,
                'is_featured': True,
            },
            {
                'name': 'Jio Postpaid ₹799',
                'category': postpaid_cat,
                'description': 'Premium postpaid with 150GB data and family benefits',
                'price': 799,
                'validity': 30,
                'data_allowance': '150GB total',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '300 SMS per day',
                'ott_benefits': 'Netflix 4K, Amazon Prime, Disney+ Hotstar',
                'other_benefits': 'Family data sharing, Priority support',
                'is_popular': False,
                'is_featured': True,
            },
            
            # Data Packs
            {
                'name': 'Jio Data Pack ₹51',
                'category': data_cat,
                'description': 'Data-only pack for existing users',
                'price': 51,
                'validity': 7,
                'data_allowance': '6GB total',
                'voice_calls': 'Not included',
                'sms': 'Not included',
                'ott_benefits': '',
                'other_benefits': 'Can be recharged multiple times',
                'is_popular': True,
                'is_featured': False,
            },
            {
                'name': 'Jio Data Pack ₹101',
                'category': data_cat,
                'description': 'Medium data pack',
                'price': 101,
                'validity': 14,
                'data_allowance': '12GB total',
                'voice_calls': 'Not included',
                'sms': 'Not included',
                'ott_benefits': '',
                'other_benefits': 'Works on 5G network',
                'is_popular': False,
                'is_featured': True,
            },
            
            # Annual Plans
            {
                'name': 'Jio Annual ₹2599',
                'category': annual_cat,
                'description': 'Yearly plan with 2GB daily data',
                'price': 2599,
                'validity': 365,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Netflix, Amazon Prime, Disney+ Hotstar',
                'other_benefits': 'Free international roaming pack',
                'is_popular': False,
                'is_featured': True,
            },
        ]
        
        plans_created = 0
        with transaction.atomic():
            for plan_data in jio_plans:
                plan, created = Plan.objects.get_or_create(
                    operator=jio,
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
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {plans_created} Jio plans'))