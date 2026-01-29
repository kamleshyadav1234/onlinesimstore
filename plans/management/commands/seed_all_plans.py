from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Seed all telecom operators with their plans'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Seeding all telecom data...'))
        
        # Import and run all individual seed commands
        from django.core.management import call_command
        
        # First create operators and categories
        self.stdout.write(self.style.SUCCESS('📋 Creating base operators and categories...'))
        call_command('seed_telecom_data')
        
        # Then seed individual operator plans
        self.stdout.write(self.style.SUCCESS('📱 Seeding Jio plans...'))
        call_command('seed_jio_plans')
        
        self.stdout.write(self.style.SUCCESS('📱 Seeding Airtel plans...'))
        call_command('seed_airtel_plans')
        
        self.stdout.write(self.style.SUCCESS('📱 Seeding VI plans...'))
        call_command('seed_vi_plans')
        
        self.stdout.write(self.style.SUCCESS('📱 Seeding BSNL & MTNL plans...'))
        call_command('seed_bsnl_mtnl_plans')
        
        # Additional broadband plans
        self.stdout.write(self.style.SUCCESS('🌐 Seeding broadband plans...'))
        call_command('seed_broadband_plans')
        
        self.stdout.write(self.style.SUCCESS('🎉 All telecom data seeded successfully!'))
        
        # Show summary
        from plans.models import Plan
        from telecom.models import TelecomOperator
        
        total_plans = Plan.objects.count()
        total_operators = TelecomOperator.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f'📊 Database Summary:'))
        self.stdout.write(self.style.SUCCESS(f'   • Total Operators: {total_operators}'))
        self.stdout.write(self.style.SUCCESS(f'   • Total Plans: {total_plans}'))
        self.stdout.write(self.style.SUCCESS(f'   • Active Plans: {Plan.objects.filter(is_active=True).count()}'))