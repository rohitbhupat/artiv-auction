from dashboard.models import Catalogue, PurchaseCategory


def catalogue_list(request):
    return {
        "catalogue_list": Catalogue.objects.all(),
        "purchase_categories": PurchaseCategory.objects.all(),
    }
