from django.core.management.base import BaseCommand
from django.db import transaction
from telecom.models import TelecomOperator
from plans.models import PlanCategory, Plan

class Command(BaseCommand):
    help = 'Seed BSNL and MTNL government operator plans'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📱 Seeding BSNL & MTNL plans...'))
        
        # Get or create BSNL operator
        bsnl, created = TelecomOperator.objects.get_or_create(
            name='BSNL',
            defaults={
                'operator_type': 'mobile',
                'description': 'Government-owned telecom service provider',
                'website': 'https://www.bsnl.co.in',
                'customer_care': '1503',
                'is_active': True,
            }
        )
        
        # Get or create MTNL operator
        mtnl, created = TelecomOperator.objects.get_or_create(
            name='MTNL',
            defaults={
                'operator_type': 'mobile',
                'description': 'Government telecom operator for Mumbai and Delhi',
                'website': 'https://www.mtnl.net.in',
                'customer_care': '1500',
                'is_active': True,
            }
        )
        
        # Get categories
        prepaid_cat, _ = PlanCategory.objects.get_or_create(
            name='Prepaid Recharge',
            defaults={'category_type': 'prepaid', 'icon': 'fas fa-mobile-alt'}
        )
        
        data_cat, _ = PlanCategory.objects.get_or_create(
            name='Data Packs',
            defaults={'category_type': 'data', 'icon': 'fas fa-database'}
        )
        
        special_cat, _ = PlanCategory.objects.get_or_create(
            name='Special Offers',
            defaults={'category_type': 'special', 'icon': 'fas fa-gift'}
        )
        
        # BSNL Plans
        bsnl_plans = [
            # Popular STV (Special Tariff Voucher) Plans
            {
                'operator': bsnl,
                'name': 'BSNL STV ₹107',
                'category': prepaid_cat,
                'description': 'Basic plan with unlimited calls and daily data',
                'price': 107,
                'validity': 28,
                'data_allowance': '1GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': '',
                'other_benefits': 'Free incoming roaming',
                'is_popular': True,
                'is_featured': False,
            },
            {
                'operator': bsnl,
                'name': 'BSNL STV ₹197',
                'category': prepaid_cat,
                'description': 'Value plan with 1.5GB daily data',
                'price': 197,
                'validity': 28,
                'data_allowance': '1.5GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': '',
                'other_benefits': 'Free night calling',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'operator': bsnl,
                'name': 'BSNL STV ₹297',
                'category': prepaid_cat,
                'description': 'Popular STV with 90 days validity',
                'price': 297,
                'validity': 90,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': '',
                'other_benefits': 'Free incoming roaming, Low STD rates',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'operator': bsnl,
                'name': 'BSNL STV ₹333',
                'category': prepaid_cat,
                'description': '70 days validity special plan',
                'price': 333,
                'validity': 70,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': '',
                'other_benefits': 'Best for rural coverage',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'operator': bsnl,
                'name': 'BSNL STV ₹549',
                'category': prepaid_cat,
                'description': 'Long validity plan for 120 days',
                'price': 549,
                'validity': 120,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': '',
                'other_benefits': 'Extra data benefits',
                'is_popular': False,
                'is_featured': True,
            },
            {
                'operator': bsnl,
                'name': 'BSNL STV ₹777',
                'category': prepaid_cat,
                'description': 'Super long validity for 200 days',
                'price': 777,
                'validity': 200,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': '',
                'other_benefits': 'Best for long-term users',
                'is_popular': False,
                'is_featured': True,
            },
            
            # Data Packs
            {
                'operator': bsnl,
                'name': 'BSNL Data ₹109',
                'category': data_cat,
                'description': 'Data-only pack with 12GB',
                'price': 109,
                'validity': 30,
                'data_allowance': '12GB total',
                'voice_calls': 'Not included',
                'sms': 'Not included',
                'ott_benefits': '',
                'other_benefits': 'Works in 2G/3G/4G areas',
                'is_popular': True,
                'is_featured': False,
            },
            {
                'operator': bsnl,
                'name': 'BSNL Data ₹225',
                'category': data_cat,
                'description': 'High data pack with 30GB',
                'price': 225,
                'validity': 30,
                'data_allowance': '30GB total',
                'voice_calls': 'Not included',
                'sms': 'Not included',
                'ott_benefits': '',
                'other_benefits': 'Unlimited data at 80kbps after FUP',
                'is_popular': False,
                'is_featured': True,
            },
            
            # Special Offers
            {
                'operator': bsnl,
                'name': 'BSNL Farmer Special ₹199',
                'category': special_cat,
                'description': 'Special plan for rural and farmer customers',
                'price': 199,
                'validity': 60,
                'data_allowance': '1GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': '',
                'other_benefits': 'Extra benefits for agricultural customers',
                'is_popular': True,
                'is_featured': True,
            },
        ]
        
        # MTNL Plans
        mtnl_plans = [
            # MTNL Dolphin Plans (Mumbai/Delhi)
            {
                'operator': mtnl,
                'name': 'MTNL Dolphin 149',
                'category': prepaid_cat,
                'description': 'Basic plan for Mumbai/Delhi users',
                'price': 149,
                'validity': 30,
                'data_allowance': '1GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': '',
                'other_benefits': 'Local calls at 50p/min',
                'is_popular': True,
                'is_featured': False,
            },
            {
                'operator': mtnl,
                'name': 'MTNL Dolphin 249',
                'category': prepaid_cat,
                'description': 'Popular Dolphin plan',
                'price': 249,
                'validity': 30,
                'data_allowance': '1.5GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': '',
                'other_benefits': 'Free night calling',
                'is_popular': True,
                'is_featured': True,
            },
            
            # MTNL Trump Plans
            {
                'operator': mtnl,
                'name': 'MTNL Trump 199',
                'category': prepaid_cat,
                'description': 'Entry-level Trump plan',
                'price': 199,
                'validity': 90,
                'data_allowance': '1GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': '',
                'other_benefits': 'Long validity benefit',
                'is_popular': True,
                'is_featured': False,
            },
            {
                'operator': mtnl,
                'name': 'MTNL Trump 399',
                'category': prepaid_cat,
                'description': 'Popular Trump plan with 90 days validity',
                'price': 399,
                'validity': 90,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': '',
                'other_benefits': 'Local calls at 1p/sec, Free night calling',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'operator': mtnl,
                'name': 'MTNL Trump 599',
                'category': prepaid_cat,
                'description': 'Premium Trump plan',
                'price': 599,
                'validity': 180,
                'data_allowance': '1.5GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': '',
                'other_benefits': 'Free night data, Low roaming charges',
                'is_popular': False,
                'is_featured': True,
            },
            {
                'operator': mtnl,
                'name': 'MTNL Trump 999',
                'category': prepaid_cat,
                'description': 'Super Trump plan with 365 days validity',
                'price': 999,
                'validity': 365,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': '',
                'other_benefits': 'Annual plan best for long-term users',
                'is_popular': False,
                'is_featured': True,
            },
            
            # Special Offers
            {
                'operator': mtnl,
                'name': 'MTNL Mumbai Special ₹99',
                'category': special_cat,
                'description': 'Mumbai exclusive special offer',
                'price': 99,
                'validity': 28,
                'data_allowance': '1GB per day',
                'voice_calls': 'Unlimited local calls',
                'sms': '100 SMS per day',
                'ott_benefits': '',
                'other_benefits': 'Valid only in Mumbai circle',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'operator': mtnl,
                'name': 'MTNL Delhi Dhamaka ₹149',
                'category': special_cat,
                'description': 'Delhi exclusive festival offer',
                'price': 149,
                'validity': 45,
                'data_allowance': '1.5GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': '',
                'other_benefits': 'Valid only in Delhi circle',
                'is_popular': True,
                'is_featured': True,
            },
        ]
        
        plans_created = 0
        with transaction.atomic():
            # Create BSNL plans
            for plan_data in bsnl_plans:
                plan, created = Plan.objects.get_or_create(
                    operator=plan_data['operator'],
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
            
            # Create MTNL plans
            for plan_data in mtnl_plans:
                plan, created = Plan.objects.get_or_create(
                    operator=plan_data['operator'],
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
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {plans_created} BSNL & MTNL plans'))