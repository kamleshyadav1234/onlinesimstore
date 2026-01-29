# plans/management/commands/seed_telecom_data.py
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.files.base import ContentFile
from telecom.models import TelecomOperator, ServiceArea
from plans.models import PlanCategory, Plan

class Command(BaseCommand):
    help = 'Seed database with sample Indian telecom operators and plans'
    
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🌐 Seeding telecom database...'))
        
        # Create categories
        categories = self.create_categories()
        
        # Create operators
        operators = self.create_operators()
        
        # Create service areas
        self.create_service_areas(operators)
        
        # Create plans
        self.create_plans(operators, categories)
        
        self.stdout.write(self.style.SUCCESS('✅ Database seeding completed successfully!'))
    
    def create_categories(self):
        """Create default plan categories"""
        categories_data = [
            {
                'name': 'Prepaid Recharge',
                'category_type': 'prepaid',
                'icon': 'fas fa-mobile-alt',
                'description': 'Regular prepaid mobile recharge plans with daily data'
            },
            {
                'name': 'Postpaid Plans',
                'category_type': 'postpaid',
                'icon': 'fas fa-file-invoice',
                'description': 'Monthly postpaid subscription plans with billing'
            },
            {
                'name': 'Data Packs',
                'category_type': 'data',
                'icon': 'fas fa-database',
                'description': 'Data-only top-up packs without calling benefits'
            },
            {
                'name': 'International Roaming',
                'category_type': 'roaming',
                'icon': 'fas fa-globe-americas',
                'description': 'International roaming packs for travelers'
            },
            {
                'name': 'Special Offers',
                'category_type': 'special',
                'icon': 'fas fa-gift',
                'description': 'Limited time offers and promotional plans'
            },
            {
                'name': 'Annual Plans',
                'category_type': 'prepaid',
                'icon': 'fas fa-calendar-alt',
                'description': 'Yearly validity plans for long-term users'
            },
        ]
        
        categories = {}
        for data in categories_data:
            category, created = PlanCategory.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            categories[data['name']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created category: {data["name"]}'))
        
        return categories
    
    def create_operators(self):
        """Create Indian telecom operators"""
        operators_data = [
            {
                'name': 'Reliance Jio',
                'operator_type': 'mobile',
                'description': 'India\'s largest 4G/5G mobile network operator with extensive coverage and affordable data plans. Offers JioFiber broadband services.',
                'website': 'https://www.jio.com',
                'customer_care': '198',
                'is_active': True,
            },
            {
                'name': 'Airtel',
                'operator_type': 'mobile',
                'description': 'One of India\'s leading telecom operators offering 2G, 3G, 4G and 5G services. Provides Airtel Xstream fiber and DTH services.',
                'website': 'https://www.airtel.in',
                'customer_care': '121',
                'is_active': True,
            },
            {
                'name': 'Vodafone Idea (VI)',
                'operator_type': 'mobile',
                'description': 'Pan-India telecom operator formed by merger of Vodafone India and Idea Cellular. Known for extensive rural coverage.',
                'website': 'https://www.myvi.in',
                'customer_care': '199',
                'is_active': True,
            },
            {
                'name': 'BSNL',
                'operator_type': 'mobile',
                'description': 'Government-owned telecom service provider offering mobile, broadband and landline services across India.',
                'website': 'https://www.bsnl.co.in',
                'customer_care': '1503',
                'is_active': True,
            },
            {
                'name': 'MTNL',
                'operator_type': 'mobile',
                'description': 'Government telecom operator serving Mumbai and Delhi metropolitan areas.',
                'website': 'https://www.mtnl.net.in',
                'customer_care': '1500',
                'is_active': True,
            },
            {
                'name': 'Airtel Xstream Fiber',
                'operator_type': 'broadband',
                'description': 'High-speed fiber broadband service with bundled OTT subscriptions.',
                'website': 'https://www.airtel.in/xstream-fiber',
                'customer_care': '121',
                'is_active': True,
            },
            {
                'name': 'JioFiber',
                'operator_type': 'broadband',
                'description': 'Fiber-to-the-home broadband service with 4K set-top box and OTT apps.',
                'website': 'https://www.jio.com/fiber',
                'customer_care': '198',
                'is_active': True,
            },
        ]
        
        operators = {}
        for data in operators_data:
            operator, created = TelecomOperator.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            operators[data['name']] = operator
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created operator: {data["name"]}'))
        
        return operators
    
    def create_service_areas(self, operators):
        """Create service areas for operators"""
        service_areas_data = [
            # Jio service areas
            {
                'operator': 'Reliance Jio',
                'state': 'MH',
                'city': 'Mumbai',
                'pincodes': '400001,400002,400003,400004,400005,400006,400007,400008,400009,400010',
                'availability': True,
            },
            {
                'operator': 'Reliance Jio',
                'state': 'DL',
                'city': 'Delhi',
                'pincodes': '110001,110002,110003,110004,110005,110006',
                'availability': True,
            },
            {
                'operator': 'Reliance Jio',
                'state': 'KA',
                'city': 'Bangalore',
                'pincodes': '560001,560002,560003,560004,560005',
                'availability': True,
            },
            
            # Airtel service areas
            {
                'operator': 'Airtel',
                'state': 'MH',
                'city': 'Mumbai',
                'pincodes': '400011,400012,400013,400014,400015,400016',
                'availability': True,
            },
            {
                'operator': 'Airtel',
                'state': 'TN',
                'city': 'Chennai',
                'pincodes': '600001,600002,600003,600004,600005',
                'availability': True,
            },
            
            # VI service areas
            {
                'operator': 'Vodafone Idea (VI)',
                'state': 'GJ',
                'city': 'Ahmedabad',
                'pincodes': '380001,380002,380003,380004,380005',
                'availability': True,
            },
            
            # BSNL service areas (all India)
            {
                'operator': 'BSNL',
                'state': 'UP',
                'city': 'Lucknow',
                'pincodes': '226001,226002,226003,226004,226005',
                'availability': True,
            },
        ]
        
        for area_data in service_areas_data:
            operator = operators.get(area_data['operator'])
            if operator:
                ServiceArea.objects.get_or_create(
                    operator=operator,
                    state=area_data['state'],
                    city=area_data['city'],
                    defaults={
                        'pincodes': area_data['pincodes'],
                        'availability': area_data['availability'],
                    }
                )
        
        self.stdout.write(self.style.SUCCESS('  Created service areas'))
    
    def create_plans(self, operators, categories):
        """Create sample plans for Indian operators"""
        plans_data = [
            # Jio Prepaid Plans
            {
                'operator': 'Reliance Jio',
                'category': 'Prepaid Recharge',
                'name': 'Jio ₹299 Plan',
                'description': 'Popular prepaid plan with 1.5GB daily data, unlimited calls and 100 SMS/day. Includes Jio apps subscription.',
                'price': 299,
                'validity': 28,
                'data_allowance': '1.5GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'JioTV, JioCinema, JioSaavn free subscription',
                'other_benefits': 'Free incoming calls, No roaming charges',
                'is_popular': True,
                'is_featured': True,
                'is_active': True,
            },
            {
                'operator': 'Reliance Jio',
                'category': 'Prepaid Recharge',
                'name': 'Jio ₹399 Plan',
                'description': 'High data plan with 2GB daily data, unlimited calling and SMS. Comes with Disney+ Hotstar subscription.',
                'price': 399,
                'validity': 28,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Disney+ Hotstar (Mobile), JioTV, JioCinema',
                'other_benefits': 'Data rollover up to 200GB, Free outgoing calls',
                'is_popular': True,
                'is_featured': False,
                'is_active': True,
            },
            {
                'operator': 'Reliance Jio',
                'category': 'Annual Plans',
                'name': 'Jio ₹2999 Annual Plan',
                'description': 'Annual plan with 2GB daily data and unlimited benefits for 365 days. Best for long-term users.',
                'price': 2999,
                'validity': 365,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'JioTV, JioCinema, JioSaavn, Disney+ Hotstar',
                'other_benefits': 'Annual subscription to all Jio apps',
                'is_popular': False,
                'is_featured': True,
                'is_active': True,
            },
            
            # Airtel Prepaid Plans
            {
                'operator': 'Airtel',
                'category': 'Prepaid Recharge',
                'name': 'Airtel ₹299 Plan',
                'description': 'Unlimited calls with 1GB daily data and 100 SMS/day. Includes Airtel Thanks benefits.',
                'price': 299,
                'validity': 28,
                'data_allowance': '1GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Airtel Xstream Play, Wynk Music',
                'other_benefits': 'Airtel Thanks rewards, Data rollover',
                'is_popular': True,
                'is_featured': True,
                'is_active': True,
            },
            {
                'operator': 'Airtel',
                'category': 'Prepaid Recharge',
                'name': 'Airtel ₹479 Plan',
                'description': '56 days validity with 1.5GB daily data and Amazon Prime subscription.',
                'price': 479,
                'validity': 56,
                'data_allowance': '1.5GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Amazon Prime (Mobile), Disney+ Hotstar',
                'other_benefits': 'Double data on weekends, Night unlimited data',
                'is_popular': True,
                'is_featured': True,
                'is_active': True,
            },
            
            # Airtel Postpaid Plans
            {
                'operator': 'Airtel',
                'category': 'Postpaid Plans',
                'name': 'Airtel Postpaid ₹499',
                'description': 'Monthly postpaid with 75GB data, unlimited calls and carryforward data.',
                'price': 499,
                'validity': 30,
                'data_allowance': '75GB total (2.5GB/day average)',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Netflix Basic, Amazon Prime, Disney+ Hotstar',
                'other_benefits': 'Data rollover up to 200GB, Free outgoing roaming',
                'is_popular': False,
                'is_featured': True,
                'is_active': True,
            },
            
            # VI Plans
            {
                'operator': 'Vodafone Idea (VI)',
                'category': 'Prepaid Recharge',
                'name': 'VI ₹299 Plan',
                'description': 'Unlimited calls with 1.5GB daily data and weekend data benefits.',
                'price': 299,
                'validity': 28,
                'data_allowance': '1.5GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Vodafone Play, ZEE5 Premium',
                'other_benefits': 'Extra 2GB data on Sundays, Night unlimited',
                'is_popular': True,
                'is_featured': True,
                'is_active': True,
            },
            {
                'operator': 'Vodafone Idea (VI)',
                'category': 'Prepaid Recharge',
                'name': 'VI ₹399 Plan',
                'description': '56 days validity with 2GB daily data and Amazon Prime subscription.',
                'price': 399,
                'validity': 56,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'Amazon Prime (Mobile), Vodafone Play',
                'other_benefits': 'Double data on first recharge, Free outgoing roaming',
                'is_popular': True,
                'is_featured': False,
                'is_active': True,
            },
            
            # BSNL Plans
            {
                'operator': 'BSNL',
                'category': 'Prepaid Recharge',
                'name': 'BSNL STV ₹297',
                'description': 'Special Tariff Voucher with 90 days validity and unlimited calling.',
                'price': 297,
                'validity': 90,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'No OTT benefits',
                'other_benefits': 'Free incoming roaming, Low call rates',
                'is_popular': True,
                'is_featured': True,
                'is_active': True,
            },
            {
                'operator': 'BSNL',
                'category': 'Data Packs',
                'name': 'BSNL Data Pack ₹109',
                'description': 'Data-only pack with 12GB data for 30 days.',
                'price': 109,
                'validity': 30,
                'data_allowance': '12GB total',
                'voice_calls': 'Not included',
                'sms': 'Not included',
                'ott_benefits': 'No OTT benefits',
                'other_benefits': 'Works in 2G/3G/4G areas',
                'is_popular': True,
                'is_featured': False,
                'is_active': True,
            },
            
            # MTNL Plans
            {
                'operator': 'MTNL',
                'category': 'Prepaid Recharge',
                'name': 'MTNL Trump 399',
                'description': 'Special plan for Mumbai/Delhi users with long validity.',
                'price': 399,
                'validity': 90,
                'data_allowance': '2GB per day',
                'voice_calls': 'Unlimited calls to any network',
                'sms': '100 SMS per day',
                'ott_benefits': 'No OTT benefits',
                'other_benefits': 'Local calls at 1p/sec, Free night calling',
                'is_popular': True,
                'is_featured': True,
                'is_active': True,
            },
            
            # Broadband Plans
            {
                'operator': 'Airtel Xstream Fiber',
                'category': 'Postpaid Plans',
                'name': 'Airtel Fiber ₹999',
                'description': '100 Mbps unlimited fiber broadband with OTT bundle.',
                'price': 999,
                'validity': 30,
                'data_allowance': 'Unlimited data at 100Mbps',
                'voice_calls': 'Unlimited landline calls',
                'sms': 'Not applicable',
                'ott_benefits': 'Amazon Prime, Disney+ Hotstar, ZEE5',
                'other_benefits': 'Free router installation, Unlimited data',
                'is_popular': True,
                'is_featured': True,
                'is_active': True,
            },
            {
                'operator': 'JioFiber',
                'category': 'Postpaid Plans',
                'name': 'JioFiber ₹999',
                'description': '150 Mbps unlimited fiber broadband with 4K set-top box.',
                'price': 999,
                'validity': 30,
                'data_allowance': 'Unlimited data at 150Mbps',
                'voice_calls': 'Unlimited landline calls',
                'sms': 'Not applicable',
                'ott_benefits': 'Netflix, Amazon Prime, Disney+ Hotstar',
                'other_benefits': 'Free 4K set-top box, Unlimited data',
                'is_popular': True,
                'is_featured': True,
                'is_active': True,
            },
            
            # Data Packs
            {
                'operator': 'Reliance Jio',
                'category': 'Data Packs',
                'name': 'Jio Data Add-on ₹51',
                'description': 'Additional data pack for existing users.',
                'price': 51,
                'validity': 7,
                'data_allowance': '6GB total',
                'voice_calls': 'Not included',
                'sms': 'Not included',
                'ott_benefits': 'No OTT benefits',
                'other_benefits': 'Can be recharged multiple times',
                'is_popular': True,
                'is_featured': False,
                'is_active': True,
            },
            {
                'operator': 'Airtel',
                'category': 'Data Packs',
                'name': 'Airtel Data Add-on ₹58',
                'description': 'Extra data top-up pack.',
                'price': 58,
                'validity': 10,
                'data_allowance': '8GB total',
                'voice_calls': 'Not included',
                'sms': 'Not included',
                'ott_benefits': 'No OTT benefits',
                'other_benefits': 'Works on 4G network',
                'is_popular': False,
                'is_featured': True,
                'is_active': True,
            },
        ]
        
        plans_created = 0
        with transaction.atomic():
            for plan_data in plans_data:
                operator = operators.get(plan_data['operator'])
                if not operator:
                    continue
                
                category = categories.get(plan_data['category'])
                
                plan, created = Plan.objects.get_or_create(
                    operator=operator,
                    name=plan_data['name'],
                    defaults={
                        'category': category,
                        'description': plan_data['description'],
                        'price': plan_data['price'],
                        'validity': plan_data['validity'],
                        'validity_unit': 'days',
                        'data_allowance': plan_data.get('data_allowance', ''),
                        'voice_calls': plan_data.get('voice_calls', ''),
                        'sms': plan_data.get('sms', ''),
                        'ott_benefits': plan_data.get('ott_benefits', ''),
                        'other_benefits': plan_data.get('other_benefits', ''),
                        'is_popular': plan_data.get('is_popular', False),
                        'is_featured': plan_data.get('is_featured', False),
                        'is_active': plan_data.get('is_active', True),
                    }
                )
                
                if created:
                    plans_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  Created {plans_created} sample plans'))