# create_initial_data.py
from django.core.management.base import BaseCommand
from telecom.models import TelecomOperator, ServiceArea
from plans.models import PlanCategory, Plan

class Command(BaseCommand):
    help = 'Creates initial data for the telecom website'
    
    def handle(self, *args, **kwargs):
        # Create Operators
        operators_data = [
            {
                'name': 'Airtel',
                'operator_type': 'mobile',
                'description': 'Airtel is one of the largest telecom operators in India',
                'website': 'https://www.airtel.in',
                'customer_care': '121',
            },
            {
                'name': 'Jio',
                'operator_type': 'mobile',
                'description': 'Reliance Jio offers affordable data and calling plans',
                'website': 'https://www.jio.com',
                'customer_care': '199',
            },
            {
                'name': 'Vi',
                'operator_type': 'mobile',
                'description': 'Vodafone Idea provides mobile services across India',
                'website': 'https://www.myvi.in',
                'customer_care': '199',
            },
            {
                'name': 'BSNL',
                'operator_type': 'mobile',
                'description': 'Government-owned telecom service provider',
                'website': 'https://www.bsnl.co.in',
                'customer_care': '1503',
            },
        ]
        
        for op_data in operators_data:
            operator, created = TelecomOperator.objects.get_or_create(
                name=op_data['name'],
                defaults=op_data
            )
            if created:
                self.stdout.write(f'Created operator: {operator.name}')
        
        # Create Categories
        categories = [
            {'name': 'Prepaid Plans', 'category_type': 'prepaid', 'icon': 'fa-sim-card'},
            {'name': 'Postpaid Plans', 'category_type': 'postpaid', 'icon': 'fa-credit-card'},
            {'name': 'Data Packs', 'category_type': 'data', 'icon': 'fa-database'},
            {'name': 'Roaming Packs', 'category_type': 'roaming', 'icon': 'fa-globe'},
            {'name': 'International Packs', 'category_type': 'international', 'icon': 'fa-plane'},
            {'name': 'Special Offers', 'category_type': 'special', 'icon': 'fa-gift'},
        ]
        
        for cat_data in categories:
            category, created = PlanCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        self.stdout.write(self.style.SUCCESS('Initial data created successfully!'))