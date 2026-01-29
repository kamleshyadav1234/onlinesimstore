# plans/management/commands/cleanup_categories.py
from django.core.management.base import BaseCommand
from django.db import transaction
from plans.models import PlanCategory, Plan

class Command(BaseCommand):
    help = 'Clean up duplicate categories and reorganize'
    
    def handle(self, *args, **options):
        print("Cleaning up categories...")
        
        # Define which categories to keep (the ones with plans)
        keep_categories = {
            7: 'Prepaid Recharge',      # Has 28 plans
            2: 'Postpaid Plans',        # Has 7 plans
            3: 'Data Packs',            # Has 7 plans
            6: 'Special Offers',        # Has 7 plans
            8: 'International Roaming', # Has 2 plans
            9: 'Annual Plans',          # Has 2 plans
        }
        
        # Define empty categories to delete
        delete_categories = [1, 4, 5]
        
        with transaction.atomic():
            # First, check if we need to move any plans
            for old_id, new_id in [(1, 7), (4, 8), (5, 8)]:
                try:
                    old_cat = PlanCategory.objects.get(id=old_id)
                    new_cat = PlanCategory.objects.get(id=new_id)
                    
                    # Move any plans (should be 0, but just in case)
                    moved = Plan.objects.filter(category=old_cat).update(category=new_cat)
                    if moved > 0:
                        print(f"Moved {moved} plans from ID {old_id} to ID {new_id}")
                        
                except PlanCategory.DoesNotExist:
                    pass
            
            # Delete empty categories
            for cat_id in delete_categories:
                try:
                    cat = PlanCategory.objects.get(id=cat_id)
                    cat.delete()
                    print(f"Deleted empty category ID {cat_id}: '{cat.name}'")
                except PlanCategory.DoesNotExist:
                    pass
            
            # Rename kept categories to standard names
            rename_map = {
                7: 'Prepaid',
                2: 'Postpaid',
                3: 'Data',
                6: 'Special',
                8: 'International',
                9: 'Annual',
            }
            
            for cat_id, new_name in rename_map.items():
                try:
                    cat = PlanCategory.objects.get(id=cat_id)
                    old_name = cat.name
                    cat.name = new_name
                    cat.save()
                    print(f"Renamed ID {cat_id}: '{old_name}' -> '{new_name}'")
                except PlanCategory.DoesNotExist:
                    pass
        
        print("\nFinal categories:")
        for cat in PlanCategory.objects.all().order_by('id'):
            plan_count = Plan.objects.filter(category=cat).count()
            print(f"ID {cat.id}: '{cat.name}' - {plan_count} plans")
        
        print(f"\n✅ Total plans: {Plan.objects.count()}")
        print(f"✅ Total categories: {PlanCategory.objects.count()}")