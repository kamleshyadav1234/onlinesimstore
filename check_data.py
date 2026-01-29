# Create diagnostic.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telecompedia.settings')
django.setup()

from plans.models import Plan, PlanCategory
from django.db.models import Count

print("=" * 70)
print("DIAGNOSTIC: PLAN CATEGORY ISSUES")
print("=" * 70)

# 1. Check all categories
print("\n1. ALL CATEGORIES IN DATABASE:")
categories = PlanCategory.objects.all().order_by('id')
for cat in categories:
    print(f"  ID {cat.id}: '{cat.name}' (Type: {cat.category_type})")

# 2. Check plans in each category
print("\n2. PLANS IN EACH CATEGORY (ACTIVE ONLY):")
for cat in categories:
    active_count = Plan.objects.filter(category=cat, is_active=True).count()
    total_count = Plan.objects.filter(category=cat).count()
    print(f"  ID {cat.id} ('{cat.name}'):")
    print(f"    Active plans: {active_count}")
    print(f"    Total plans: {total_count}")
    
    # Show sample plans
    if active_count > 0:
        sample_plans = Plan.objects.filter(category=cat, is_active=True)[:2]
        for plan in sample_plans:
            print(f"    • {plan.operator.name} - {plan.name} (₹{plan.price})")

# 3. Check plans without category
print("\n3. PLANS WITHOUT CATEGORY:")
no_category = Plan.objects.filter(category__isnull=True)
print(f"  Total: {no_category.count()} plans")
for plan in no_category[:5]:
    print(f"    • {plan.operator.name} - {plan.name} (Active: {plan.is_active})")

# 4. Check plans that are inactive
print("\n4. INACTIVE PLANS:")
inactive = Plan.objects.filter(is_active=False)
print(f"  Total: {inactive.count()} plans")
for plan in inactive[:5]:
    cat_name = plan.category.name if plan.category else "No Category"
    print(f"    • {plan.operator.name} - {plan.name} (Category: {cat_name})")

# 5. Simulate your view's filter
print("\n5. SIMULATING FILTER category=7 (Prepaid):")
try:
    category_7 = PlanCategory.objects.get(id=7)
    print(f"  Category ID 7 is: '{category_7.name}'")
    
    # Check with same logic as your view
    filtered_plans = Plan.objects.filter(is_active=True, category_id=7)
    print(f"  Active plans with category_id=7: {filtered_plans.count()}")
    
    if filtered_plans.count() > 0:
        print("  Sample plans:")
        for plan in filtered_plans[:3]:
            print(f"    • {plan.operator.name} - {plan.name} - ₹{plan.price}")
    else:
        print("  PROBLEM: No active plans found with category_id=7!")
        print("  Checking all plans with category_id=7 (including inactive):")
        all_plans_cat7 = Plan.objects.filter(category_id=7)
        print(f"    Total: {all_plans_cat7.count()}")
        for plan in all_plans_cat7:
            print(f"    • {plan.operator.name} - {plan.name} - Active: {plan.is_active}")
        
except PlanCategory.DoesNotExist:
    print("  ERROR: Category ID 7 does not exist!")

print("\n" + "=" * 70)
print("RECOMMENDED ACTIONS:")
print("1. If 'Active plans with category_id=7' is 0: Your plans are inactive")
print("2. If category doesn't exist: You need to create it")
print("3. If plans have no category: Assign categories to them")
print("=" * 70)
