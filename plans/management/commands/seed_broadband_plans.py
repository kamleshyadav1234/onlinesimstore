from django.core.management.base import BaseCommand
from django.db import transaction
from telecom.models import TelecomOperator
from plans.models import PlanCategory, Plan

class Command(BaseCommand):
    help = 'Seed broadband plans (JioFiber, Airtel Xstream)'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌐 Seeding broadband plans...'))
        
        # Get or create broadband operators
        jiofiber, _ = TelecomOperator.objects.get_or_create(
            name='JioFiber',
            defaults={
                'operator_type': 'broadband',
                'description': 'Fiber-to-the-home broadband service',
                'website': 'https://www.jio.com/fiber',
                'customer_care': '198',
                'is_active': True,
            }
        )
        
        airtel_fiber, _ = TelecomOperator.objects.get_or_create(
            name='Airtel Xstream Fiber',
            defaults={
                'operator_type': 'broadband',
                'description': 'High-speed fiber broadband service',
                'website': 'https://www.airtel.in/xstream-fiber',
                'customer_care': '121',
                'is_active': True,
            }
        )
        
        # Get category
        postpaid_cat, _ = PlanCategory.objects.get_or_create(
            name='Postpaid Plans',
            defaults={'category_type': 'postpaid', 'icon': 'fas fa-file-invoice'}
        )
        
        # Broadband Plans
        broadband_plans = [
            # JioFiber Plans
            {
                'operator': jiofiber,
                'name': 'JioFiber Basic ₹399',
                'category': postpaid_cat,
                'description': 'Entry-level fiber broadband with basic speed',
                'price': 399,
                'validity': 30,
                'data_allowance': 'Unlimited data at 30Mbps',
                'voice_calls': 'Unlimited landline calls',
                'sms': 'Not applicable',
                'ott_benefits': 'JioTV, JioCinema',
                'other_benefits': 'Free router installation',
                'is_popular': True,
                'is_featured': False,
            },
            {
                'operator': jiofiber,
                'name': 'JioFiber ₹699',
                'category': postpaid_cat,
                'description': 'Popular plan with 100Mbps speed',
                'price': 699,
                'validity': 30,
                'data_allowance': 'Unlimited data at 100Mbps',
                'voice_calls': 'Unlimited landline calls',
                'sms': 'Not applicable',
                'ott_benefits': 'Amazon Prime, Disney+ Hotstar',
                'other_benefits': 'Free 4K set-top box',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'operator': jiofiber,
                'name': 'JioFiber ₹999',
                'category': postpaid_cat,
                'description': 'High-speed plan with 150Mbps',
                'price': 999,
                'validity': 30,
                'data_allowance': 'Unlimited data at 150Mbps',
                'voice_calls': 'Unlimited landline calls',
                'sms': 'Not applicable',
                'ott_benefits': 'Netflix, Amazon Prime, Disney+ Hotstar',
                'other_benefits': 'Free 4K set-top box, Unlimited data',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'operator': jiofiber,
                'name': 'JioFiber ₹1499',
                'category': postpaid_cat,
                'description': 'Premium plan with 300Mbps speed',
                'price': 1499,
                'validity': 30,
                'data_allowance': 'Unlimited data at 300Mbps',
                'voice_calls': 'Unlimited landline calls',
                'sms': 'Not applicable',
                'ott_benefits': 'Netflix 4K, Amazon Prime, Disney+ Hotstar, ZEE5',
                'other_benefits': 'Free gaming subscription, Priority support',
                'is_popular': False,
                'is_featured': True,
            },
            
            # Airtel Xstream Fiber Plans
            {
                'operator': airtel_fiber,
                'name': 'Airtel Fiber ₹499',
                'category': postpaid_cat,
                'description': 'Basic fiber broadband plan',
                'price': 499,
                'validity': 30,
                'data_allowance': 'Unlimited data at 40Mbps',
                'voice_calls': 'Unlimited landline calls',
                'sms': 'Not applicable',
                'ott_benefits': 'Airtel Xstream Play',
                'other_benefits': 'Free router installation',
                'is_popular': True,
                'is_featured': False,
            },
            {
                'operator': airtel_fiber,
                'name': 'Airtel Fiber ₹799',
                'category': postpaid_cat,
                'description': 'Popular plan with 100Mbps speed',
                'price': 799,
                'validity': 30,
                'data_allowance': 'Unlimited data at 100Mbps',
                'voice_calls': 'Unlimited landline calls',
                'sms': 'Not applicable',
                'ott_benefits': 'Amazon Prime, Disney+ Hotstar',
                'other_benefits': 'Free WiFi router',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'operator': airtel_fiber,
                'name': 'Airtel Fiber ₹999',
                'category': postpaid_cat,
                'description': 'High-speed plan with 200Mbps',
                'price': 999,
                'validity': 30,
                'data_allowance': 'Unlimited data at 200Mbps',
                'voice_calls': 'Unlimited landline calls',
                'sms': 'Not applicable',
                'ott_benefits': 'Netflix Basic, Amazon Prime, Disney+ Hotstar',
                'other_benefits': 'Free landline connection',
                'is_popular': True,
                'is_featured': True,
            },
            {
                'operator': airtel_fiber,
                'name': 'Airtel Fiber ₹1599',
                'category': postpaid_cat,
                'description': 'Premium plan with 1Gbps speed',
                'price': 1599,
                'validity': 30,
                'data_allowance': 'Unlimited data at 1Gbps',
                'voice_calls': 'Unlimited landline calls',
                'sms': 'Not applicable',
                'ott_benefits': 'Netflix 4K, Amazon Prime, Disney+ Hotstar, Apple TV+',
                'other_benefits': 'Free mesh router, Priority installation',
                'is_popular': False,
                'is_featured': True,
            },
        ]
        
        plans_created = 0
        with transaction.atomic():
            for plan_data in broadband_plans:
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
        
        self.stdout.write(self.style.SUCCESS(f'✅ Created {plans_created} broadband plans'))