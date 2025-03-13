document.addEventListener("DOMContentLoaded", function () {
  // Helper function to show or hide fields
  function toggleField(fieldId, show) {
    const field = document.querySelector("#" + fieldId)?.closest(".form-row");
    if (field) {
      field.style.display = show ? "" : "none";
    }
  }

  // Sale Type Logic
  const saleTypeField = document.querySelector("#id_sale_type");
  const discountFields = ["id_product_price"]; // Exclude product_id
  const biddingFields = ["id_opening_bid", "id_end_date", "id_product_cat"];

  function toggleSaleTypeFields() {
    const selectedType = saleTypeField?.value;

    // Toggle fields based on the sale type
    const isDiscount = selectedType === "discount";
    const isBidding = selectedType === "auction";

    // Toggle fields for discount and bidding
    discountFields.forEach((fieldId) => toggleField(fieldId, isDiscount));
    biddingFields.forEach((fieldId) => toggleField(fieldId, isBidding));

    // Ensure product_id is always visible
    toggleField("id_product_id", true);
    toggleField("id_product_qty", true);
  }

  // Dimension Unit Logic
  const dimensionUnitField = document.querySelector("#id_dimension_unit");
  const lengthInCentimetersField = document
    .querySelector("#id_length_in_centimeters")
    ?.closest(".form-row");
  const widthInCentimetersField = document
    .querySelector("#id_width_in_centimeters")
    ?.closest(".form-row");
  const footField = document.querySelector("#id_foot")?.closest(".form-row");
  const inchesField = document
    .querySelector("#id_inches")
    ?.closest(".form-row");

  function toggleDimensionFields() {
    const selectedUnit = dimensionUnitField?.value;

    // Show/hide fields based on the selected unit
    const showCentimeters = selectedUnit === "cm";
    const showFeetInches = selectedUnit === "ft";

    lengthInCentimetersField?.style.setProperty(
      "display",
      showCentimeters ? "" : "none"
    );
    widthInCentimetersField?.style.setProperty(
      "display",
      showCentimeters ? "" : "none"
    );
    footField?.style.setProperty("display", showFeetInches ? "" : "none");
    inchesField?.style.setProperty("display", showFeetInches ? "" : "none");
  }

  // Event Listeners
  if (saleTypeField) {
    saleTypeField.addEventListener("change", toggleSaleTypeFields);
    toggleSaleTypeFields(); // Initialize on page load
  }

  if (dimensionUnitField) {
    dimensionUnitField.addEventListener("change", toggleDimensionFields);
    toggleDimensionFields(); // Initialize on page load
  }
});
