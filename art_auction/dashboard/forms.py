import uuid
from django import forms
from .models import Artwork, PurchaseCategory  # Adjust import paths if necessary
from PIL import Image
import imagehash


class ArtworkCreateForm(forms.ModelForm):
    sale_type = forms.ChoiceField(
        choices=[("discount", "Discount"), ("auction", "Auction")],
        widget=forms.RadioSelect,
        required=True
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False
    )
    purchase_category = forms.ModelChoiceField(
        queryset=PurchaseCategory.objects.all(), required=False
    )
    opening_bid = forms.DecimalField(required=False)
    model_360 = forms.FileField(required=False, label="Upload 360 Model")

    class Meta:
        model = Artwork
        fields = [
            "sale_type", "product_name", "product_price", "opening_bid",
            "product_cat", "product_image", "model_360", "end_date", "purchase_category",
            "dimension_unit", "length_in_centimeters", "width_in_centimeters", "foot", "inches"
        ]

    def save(self, commit=True, *args, **kwargs):
        # Generate product_id dynamically if not provided
        if not self.instance.product_id:
            self.instance.product_id = str(uuid.uuid4())  # Generate a unique UUID for the product ID

        return super().save(commit=commit, *args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        sale_type = cleaned_data.get("sale_type")

        if sale_type == "auction":
            if not cleaned_data.get("opening_bid"):
                self.add_error("opening_bid", "Opening bid is required for auctions.")
            if not cleaned_data.get("end_date"):
                self.add_error("end_date", "End date is required for auctions.")
        elif sale_type == "discount":
            if not cleaned_data.get("purchase_category"):
                self.add_error("purchase_category", "Purchase category is required for discounts.")

        return cleaned_data

class ArtworkUpdateForm(forms.ModelForm):
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        label="Auction End Date",
    )

    class Meta:
        model = Artwork
        fields = [
            "product_name",
            "product_price",
            "product_image",
            "product_cat",
            "end_date",
            "length_in_centimeters",
            "width_in_centimeters",
            "foot",
            "inches",
        ]

    def clean_product_image(self):
        # Duplicate image detection logic
        uploaded_image = self.cleaned_data.get("product_image")
        if uploaded_image:
            uploaded_image_hash = imagehash.phash(Image.open(uploaded_image))
            existing_artworks = Artwork.objects.exclude(id=self.instance.id)

            for artwork in existing_artworks:
                stored_image_hash = imagehash.phash(
                    Image.open(artwork.product_image.path)
                )
                if uploaded_image_hash == stored_image_hash:
                    raise forms.ValidationError(
                        "Duplicate image detected. This artwork has already been uploaded."
                    )
        return uploaded_image
